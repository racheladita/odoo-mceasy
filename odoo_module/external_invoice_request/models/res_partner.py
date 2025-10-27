from odoo import models, fields, api
import uuid

class ResPartner(models.Model):
    _inherit = 'res.partner'

    external_token = fields.Char(
        string="External Access Token",
        readonly=True,
        copy=False
    )

    _sql_constraints = [
        ('external_token_unique', 'unique(external_token)', 'External token must be unique!')
    ]

    @api.model
    def create(self, vals):
        if not vals.get('external_token'):
            vals['external_token'] = str(uuid.uuid4())
        return super().create(vals)

    def init(self):
        partners = self.env['res.partner'].search([('external_token', '=', False)])
        for partner in partners:
            partner.external_token = str(uuid.uuid4())
