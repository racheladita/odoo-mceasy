from odoo import models, fields, api
from odoo.exceptions import UserError

class InvoiceRequest(models.Model):
    _name = 'invoice.request'
    _description = 'External Invoice Request'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    sale_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ], default='pending', string='Status')
    create_date = fields.Datetime(readonly=True)

    def action_approval_request(self):
        for rec in self:
            if rec.status == 'approved':
                continue
            sale = rec.sale_id
            if not sale:
                raise UserError("Sale order missing")
            
            invoice_lines = []
            for line in sale.order_line:
                invoice_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'account_id': line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id,
                    'tax_ids': [(6, 0, line.tax_id.ids)],
                }))
            invoice = self.env['account.move'].create({
                'partner_id': rec.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
                'invoice_origin': sale.name,
            })
            invoice.action_post()
            rec.invoice_id = invoice.id
            rec.status = 'approved'
