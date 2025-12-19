from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    usd_unit_cost = fields.Monetary(
        string='Costo Unit. USD',
        compute='_compute_usd_valuation',
        currency_field='usd_currency_id'
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

    @api.depends('price_unit', 'product_uom_qty', 'date', 'company_id')
    def _compute_usd_valuation(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for move in self:
            if not usd_currency:
                move.usd_unit_cost = 0.0
                move.usd_value = 0.0
                continue
                
            conversion_date = move.date or fields.Date.today()
            company_curr = move.company_id.currency_id
            
            move.usd_unit_cost = company_curr._convert(
                move.price_unit, usd_currency, move.company_id, conversion_date
            )
            
            total_val_company = move.price_unit * move.product_uom_qty
            move.usd_value = company_curr._convert(
                total_val_company, usd_currency, move.company_id, conversion_date
            )