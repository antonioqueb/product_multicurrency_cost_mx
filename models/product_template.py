from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_currency_id = fields.Many2one(
        'res.currency', string='USD Currency',
        default=lambda self: self.env.ref('base.USD', raise_if_not_found=False).id
    )
    
    usd_cost = fields.Monetary(
        string='Costo USD',
        compute='_compute_usd_cost',
        currency_field='usd_currency_id',
        store=True,
        help="Equivalente en USD del costo principal en MXN"
    )

    @api.depends('standard_price', 'usd_currency_id')
    def _compute_usd_cost(self):
        for record in self:
            if record.standard_price and record.usd_currency_id:
                record.usd_cost = record.env.company.currency_id._convert(
                    record.standard_price, 
                    record.usd_currency_id, 
                    record.env.company, 
                    fields.Date.today()
                )
            else:
                record.usd_cost = 0.0