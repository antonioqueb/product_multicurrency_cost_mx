from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

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

    @api.depends('price_unit', 'product_uom_qty', 'date')
    def _compute_usd_valuation(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for move in self:
            if not usd_currency:
                move.usd_unit_cost = 0.0
                move.usd_value = 0.0
                continue
                
            # Usamos la fecha del movimiento para la tasa histórica
            conversion_date = move.date or fields.Date.today()
            
            # En Odoo 19, price_unit es el costo unitario del movimiento
            move.usd_unit_cost = move.company_id.currency_id._convert(
                move.price_unit, usd_currency, move.company_id, conversion_date
            )
            
            # Valor total = costo unitario * cantidad
            total_val = move.price_unit * move.product_uom_qty
            move.usd_value = move.company_id.currency_id._convert(
                total_val, usd_currency, move.company_id, conversion_date
            )