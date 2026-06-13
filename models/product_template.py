from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_currency_id = fields.Many2one(
        'res.currency', string='USD Currency',
        compute='_compute_usd_currency_id',
        store=True,
        readonly=False
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
            
            # Usar la moneda de la compañía del registro o la de la sesión actual
            company = record.company_id or self.env.company
            base_currency = company.currency_id
            
            record.usd_cost = base_currency._convert(
                record.standard_price, 
                usd_currency, 
                company, 
                fields.Date.today()
            )

    @api.model
    def _cron_update_usd_costs(self):
        """ 
        CRON con LOGS detallados para ver qué está pasando 
        """
        _logger.info("=== INICIANDO CRON DE COSTOS USD ===")
        
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        products = self.search([('active', '=', True)])
        
        for product in products:
            # Determinamos la empresa para la tasa de cambio
            company = product.company_id or self.env.company
            base_currency = company.currency_id
            
            # Calculamos
            new_val = base_currency._convert(
                product.standard_price, 
                usd_currency, 
                company, 
                fields.Date.today()
            )
            
            # LOG DE DEPURACIÓN: Esto aparecerá en tu consola de Docker
            _logger.info(
                "Producto: %s | Costo MXN: %s | Nuevo USD: %s | Empresa Usada: %s", 
                product.name, product.standard_price, new_val, company.name
            )
            
            # Forzamos la escritura en la base de datos
            product.write({
                'usd_cost': new_val,
                'usd_currency_id': usd_currency.id
            })
            
        # Forzar que Odoo guarde los cambios en disco inmediatamente
        self.env.flush_all()
        _logger.info("=== CRON FINALIZADO: %s productos procesados ===", len(products))