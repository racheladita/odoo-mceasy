from odoo import http
from odoo.http import request
import json

class ExternalSaleInvoiceController(http.Controller):
    # GET endpoint to view the list of sale orders that can be invoiced
    @http.route(['/external/sale-invoice/<string:external_token>'], type='http', auth='public', website=True)
    def external_sale_invoice(self, external_token, **kwargs):
        partner = request.env['res.partner'].sudo().search([('external_token', '=', external_token)], limit=1)
        if not partner:
            return request.make_response("Invalid token", status=404)

        return request.render('external_invoice_request.external_sale_invoice_template', {
            'partner_token': external_token
        })

    @http.route(['/external/sale-invoice-data/<string:external_token>'], type='http', auth='public', website=True)
    def external_sale_invoice_data(self, external_token, **kwargs):
        partner = request.env['res.partner'].sudo().search([('external_token', '=', external_token)], limit=1)
        if not partner:
            return request.make_response("Invalid token", status=404)

        sale_orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'sale'),
            ('invoice_status', '=', 'to invoice')
        ])

        data = []
        for so in sale_orders:
            order_data = {
                'id': so.id,
                'name': so.name,
                'amount_total': so.amount_total,
                'date_order': so.date_order,
            }
            data.append(order_data)

        return request.make_json_response({
            'partner': partner.name,
            'sale_orders': data
        })
    # POST endpoint to create invoice request
    @http.route(['/external/request-invoice'], type='json', auth='public', csrf=False, methods=['POST'])
    def request_invoice(self, **kwargs):
        try:
            data = request.get_json_data()
        except Exception:
            data = kwargs 

        token = data.get('token')
        sale_order_id = data.get('sale_order_id')

        if not token or not sale_order_id:
            return request.make_json_response({'error': 'Missing token or sale_order_id'}, status=400)

        partner = request.env['res.partner'].sudo().search([('external_token', '=', token)], limit=1)
        if not partner:
            return request.make_json_response({'error': 'Invalid partner token'}, status=404)

        sale_order = request.env['sale.order'].sudo().browse(int(sale_order_id))
        if not sale_order.exists() or sale_order.partner_id.id != partner.id:
            return request.make_json_response({'error': 'Sale order not found or does not belong to this partner'}, status=400)

        invoice_request = request.env['invoice.request'].sudo().create({
            'partner_id': partner.id,
            'sale_id': sale_order.id,
            'status': 'pending',
        })

        return {
            'status': invoice_request.status,
            'message': 'Invoice request created successfully. Awaiting approval.'
        }

    # GET
    @http.route(['/external/invoice-status/<string:token>'], type='http', auth='public', csrf=False, methods=['GET'])
    def invoice_status(self, token, **kwargs):
        partner = request.env['res.partner'].sudo().search([('external_token', '=', token)], limit=1)
        if not partner:
            return request.make_json_response({'error': 'Invalid token'}, status=404)

        requests = request.env['invoice.request'].sudo().search([('partner_id', '=', partner.id)])

        result = []
        for req in requests:
            result.append({
                'sale_order': req.sale_id.name,
                'status': req.status,
                'invoice_id': req.invoice_id.id if req.invoice_id else None,
                'invoice_name': req.invoice_id.name if req.invoice_id else None
            })

        return request.make_json_response({
            'partner': partner.name,
            'invoice_requests': result
        })
    
    # GET
    @http.route(['/external/download-invoice/<string:token>/<int:invoice_id>'], type='http', auth='public')
    def download_invoice(self, token, invoice_id, **kw):
        partner = request.env['res.partner'].sudo().search([('external_token', '=', token)], limit=1)
        if not partner:
            return request.make_response("Invalid token", status=404)

        invoice = request.env['account.move'].sudo().browse(invoice_id)
        if not invoice or invoice.partner_id.id != partner.id:
            return request.make_response("Unauthorized", status=403)

        pdf_content, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('account.report_invoice', [invoice.id])
        filename = f"Invoice_{invoice.name}.pdf"
        return request.make_response(pdf_content, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename={filename}')
        ])


