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
        default=lambda self: self.env.ref('base.USD', raise_if_not_found=False).id
    )

    @api.depends('unit_cost', 'value')
    def _compute_usd_valuation(self):
        # Buscamos la moneda USD de forma segura
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for layer in self:
            if not usd_currency:
                layer.usd_unit_cost = 0.0
                layer.usd_value = 0.0
                continue
                
            # Usamos la fecha de la capa de valuación para la tasa histórica
            conversion_date = layer.create_date or fields.Date.today()
            
            # Conversión de Unit Cost (MXN -> USD)
            layer.usd_unit_cost = layer.currency_id._convert(
                layer.unit_cost, usd_currency, layer.company_id, conversion_date
            )
            
            # Conversión de Valor Total (MXN -> USD)
            layer.usd_value = layer.currency_id._convert(
                layer.value, usd_currency, layer.company_id, conversion_date
            )