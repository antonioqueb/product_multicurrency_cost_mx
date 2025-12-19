from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_currency_id = fields.Many2one(
        'res.currency', string='USD Currency',
        default=lambda self: self.env.ref('base.USD').id
    )
    
    # Campo calculado que reacciona a cambios en standard_price (MXN)
    usd_cost = fields.Monetary(
        string='Costo USD',
        compute='_compute_usd_cost',
        currency_field='usd_currency_id',
        store=True, # Lo guardamos para que sea filtrable en listas
        help="Equivalente en USD del costo principal en MXN"
    )

    @api.depends('standard_price', 'usd_currency_id')
    def _compute_usd_cost(self):
        """Calcula USD basado en el MXN (standard_price) y la tasa actual"""
        for record in self:
            if record.standard_price and record.usd_currency_id:
                # Convertimos de MXN (Compañía) a USD
                record.usd_cost = record.env.company.currency_id._convert(
                    record.standard_price, 
                    record.usd_currency_id, 
                    record.env.company, 
                    fields.Date.today()
                )
            else:
                record.usd_cost = 0.0