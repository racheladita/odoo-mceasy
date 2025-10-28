from flask import Flask, request, jsonify
import xmlrpc.client
import os

app = Flask(__name__)

ODOO_URL = os.environ.get('ODOO_URL', 'http://odoo:8069')
DB = os.environ.get('ODOO_DB', 'mceasy')
USER = os.environ.get('ODOO_USER', 'odoo')
PASS = os.environ.get('ODOO_PASS', 'odoo')

def auth():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASS, {})
    if not uid:
        raise RuntimeError("Auth failed")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models

@app.route('/so/create', methods=['POST'])
def create_so():
    data = request.json or {}
    uid, models = auth()
    
    # Ensure partner_id exists
    partner_id = int(data.get('partner_id'))
    partner = models.execute_kw(DB, uid, PASS, 'res.partner', 'read', [[partner_id], {'fields': ['name']}])
    if not partner:
        return jsonify({'error': f'Partner {partner_id} not found'}), 400
    
    vals = {
        'partner_id': partner_id,
        'order_line': []
    }

    product_ids = [line['product_id'] for line in data.get('order_lines', [])]
    if not product_ids:
        return jsonify({'error': 'No order lines provided'}), 400
    
    products = models.execute_kw(
        DB, uid, PASS,
        'product.product', 'read',
        [product_ids],
        {'fields': ['name', 'uom_id', 'sale_ok']}
    )
    product_map = {p['id']: p for p in products}

    # Build order lines
    for line in data.get('order_lines', []):
        product = product_map.get(line['product_id'])
        if not product or not product['sale_ok']:
            continue  # skip invalid or non-saleable products

        vals['order_line'].append((0, 0, {
            'product_id': product['id'],
            'product_uom_qty': float(line.get('qty', 1)),
            'price_unit': float(line.get('price_unit', 0)),
            'product_uom': product['uom_id'][0],  
            'name': product['name'],
            'tax_id': [(6, 0, [])], 
        }))

    if not vals['order_line']:
        return jsonify({'error': 'No valid order lines to create'}), 400

    # Create sale order
    try:
        so_id = models.execute_kw(DB, uid, PASS, 'sale.order', 'create', [vals])
        return jsonify({'so_id': so_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/so/<int:so_id>/update', methods=['POST'])
def update_so(so_id):
    data = request.json or {}
    uid, models = auth()
    vals = data.get('vals', {})
    res = models.execute_kw(DB, uid, PASS, 'sale.order', 'write', [[so_id], vals])
    return jsonify({'result': res})

@app.route('/so/search', methods=['GET'])
def search_so():
    uid, models = auth()
    domain = request.args.get('domain')
    
    import json as _json
    domain_list = _json.loads(domain) if domain else [['state', '!=', 'cancel']]
    res = models.execute_kw(DB, uid, PASS, 'sale.order', 'search_read', [domain_list], {'fields': ['id','name','amount_total','state']})
    return jsonify(res)

@app.route('/so/<int:so_id>', methods=['GET'])
def get_so(so_id):
    uid, models = auth()
    res = models.execute_kw(DB, uid, PASS, 'sale.order', 'read', [[so_id]])
    return jsonify(res)

@app.route('/so/<int:so_id>/action_confirm', methods=['POST'])
def action_confirm(so_id):
    uid, models = auth()
    res = models.execute_kw(DB, uid, PASS, 'sale.order', 'action_confirm', [[so_id]])
    return jsonify({'result': res})

@app.route('/so/<int:so_id>/action_cancel', methods=['POST'])
def action_cancel(so_id):
    uid, models = auth()
    res = models.execute_kw(DB, uid, PASS, 'sale.order', 'action_cancel', [[so_id]])
    return jsonify({'result': res})

@app.route('/so/<int:so_id>/action_reset', methods=['POST'])
def action_reset(so_id):
    uid, models = auth()
    res = models.execute_kw(DB, uid, PASS, 'sale.order', 'action_draft', [[so_id]])
    return jsonify({'result': res})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
