from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cost_currency_id = fields.Many2one(
        'res.currency', string='Foreign Cost Currency',
        default=lambda self: self.env.ref('base.USD').id
    )
    
    foreign_cost_price = fields.Monetary(
        string='Foreign Cost',
        currency_field='cost_currency_id',
        help="Price in foreign currency (e.g. USD)"
    )
    
    last_rate_used = fields.Float(
        string='Last Rate Used',
        digits=(12, 6),
        help="Exchange rate used for the last cost update"
    )

    @api.onchange('foreign_cost_price', 'cost_currency_id')
    def _onchange_foreign_cost(self):
        """Al cambiar el costo en USD, actualiza el standard_price (MXN)"""
        if self.foreign_cost_price and self.cost_currency_id:
            company_currency = self.env.company.currency_id
            # Obtener tasa actual
            rate = self.cost_currency_id._get_rates(self.env.company, fields.Date.today()).get(self.cost_currency_id.id)
            if rate:
                # Odoo rates son 1/tasa (ej: 1/20 = 0.05)
                actual_rate = 1 / rate
                self.last_rate_used = actual_rate
                self.standard_price = self.foreign_cost_price * actual_rate

    def action_update_cost_from_usd(self):
        """Actualiza el costo MXN basado en el USD guardado y la tasa actual"""
        for record in self:
            record._onchange_foreign_cost()
