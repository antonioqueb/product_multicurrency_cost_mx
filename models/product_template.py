from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_currency_id = fields.Many2one(
        'res.currency', string='USD Currency',
        compute='_compute_usd_currency_id',
        store=True
    )
    
    usd_cost = fields.Monetary(
        string='Costo USD',
        compute='_compute_usd_cost',
        currency_field='usd_currency_id',
        store=True,
        digits='Product Price'
    )

    @api.depends('company_id')
    def _compute_usd_currency_id(self):
        usd = self.env.ref('base.USD', raise_if_not_found=False)
        for record in self:
            record.usd_currency_id = usd.id if usd else False

    @api.depends('standard_price', 'usd_currency_id', 'company_id')
    def _compute_usd_cost(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for record in self:
            if not record.standard_price or not usd_currency:
                record.usd_cost = 0.0
                continue
            
            company = record.company_id or self.env.company
            base_currency = company.currency_id
            
            if base_currency == usd_currency:
                record.usd_cost = record.standard_price
            else:
                record.usd_cost = base_currency._convert(
                    record.standard_price, 
                    usd_currency, 
                    company, 
                    fields.Date.today()
                )

    @api.model
    def _cron_update_usd_costs(self):
        """ Método llamado por la Acción Planificada """
        # Buscamos solo productos activos para ahorrar recursos
        products = self.search([('active', '=', True)])
        products._compute_usd_cost()