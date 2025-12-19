from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCostUpdateWizard(models.TransientModel):
    _name = 'product.cost.update.wizard'
    _description = 'Update Product Costs from Foreign Currency'

    currency_id = fields.Many2one('res.currency', string='Currency to Sync', required=True, 
                                 default=lambda self: self.env.ref('base.USD').id)
    current_rate = fields.Float(string='Current Rate (1 USD = ? MXN)', required=True, digits=(12, 6))

    @api.onchange('currency_id')
    def _onchange_currency(self):
        if self.currency_id:
            rate = self.currency_id._get_rates(self.env.company, fields.Date.today()).get(self.currency_id.id)
            if rate:
                self.current_rate = 1 / rate

    def apply_update(self):
        products = self.env['product.template'].search([
            ('foreign_cost_price', '>', 0),
            ('cost_currency_id', '=', self.currency_id.id)
        ])
        if not products:
            raise UserError(_("No products found with a foreign cost in %s") % self.currency_id.name)
        
        for product in products:
            product.standard_price = product.foreign_cost_price * self.current_rate
            product.last_rate_used = self.current_rate
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Updated %s products cost based on rate %s') % (len(products), self.current_rate),
                'sticky': False,
            }
        }
