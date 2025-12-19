from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    usd_unit_cost = fields.Float(
        string='Costo Unitario USD',
        compute='_compute_usd_valuation',
    )
    usd_value = fields.Float(
        string='Valor Total USD',
        compute='_compute_usd_valuation',
    )

    def _compute_usd_valuation(self):
        usd_currency = self.env.ref('base.USD')
        for layer in self:
            # Convertimos el costo unitario y valor total de la capa de valuación a USD
            layer.usd_unit_cost = layer.currency_id._convert(
                layer.unit_cost, usd_currency, layer.company_id, layer.create_date
            )
            layer.usd_value = layer.currency_id._convert(
                layer.value, usd_currency, layer.company_id, layer.create_date
            )