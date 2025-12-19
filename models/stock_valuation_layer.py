from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    usd_unit_cost = fields.Float(
        string='Costo Unit. USD',
        compute='_compute_usd_valuation',
        digits=(12, 4)
    )
    usd_value = fields.Monetary(
        string='Valor Total USD',
        compute='_compute_usd_valuation',
        currency_field='usd_currency_id'
    )
    usd_currency_id = fields.Many2one(
        'res.currency', 
        string='USD', 
        default=lambda self: self.env.ref('base.USD').id
    )

    @api.depends('unit_cost', 'value', 'create_date')
    def _compute_usd_valuation(self):
        usd_currency = self.env.ref('base.USD')
        for layer in self:
            # Usamos la fecha de creación para la tasa histórica o la fecha de hoy si no hay
            conversion_date = layer.create_date or fields.Date.today()
            
            # Convertir Costo Unitario
            layer.usd_unit_cost = layer.currency_id._convert(
                layer.unit_cost, usd_currency, layer.company_id, conversion_date
            )
            
            # Convertir Valor Total de la capa
            layer.usd_value = layer.currency_id._convert(
                layer.value, usd_currency, layer.company_id, conversion_date
            )