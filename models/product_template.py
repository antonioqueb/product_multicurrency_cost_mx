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
            # Usar la moneda de la compañía del registro o la de la sesión actual
            company = record.company_id or self.env.company
            # standard_price es company_dependent: se lee en la compañía
            # del producto (no en la activa del usuario/OdooBot).
            standard_price = record.with_company(company).standard_price
            if not standard_price or not usd_currency:
                record.usd_cost = 0.0
                continue

            base_currency = company.currency_id

            record.usd_cost = base_currency._convert(
                standard_price,
                usd_currency,
                company,
                fields.Date.today()
            )

    # Tamaño de lote del cron: acota memoria y aísla fallos.
    _USD_CRON_BATCH_SIZE = 500

    @api.model
    def _cron_update_usd_costs(self):
        """Actualiza el costo en USD de todos los productos activos.

        Robustez (antes: un solo loop sin límite, sin savepoint y con un log
        INFO por producto — un producto con moneda/tasa corrupta abortaba
        TODO el lote todos los días en silencio, dejando usd_cost congelado):
        - procesa por lotes con savepoint: un lote que falle no tumba el resto;
        - registra el detalle en DEBUG y solo el resumen en INFO;
        - reporta al final cuántos productos fallaron.
        """
        _logger.info("=== INICIANDO CRON DE COSTOS USD ===")

        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        if not usd_currency:
            _logger.error("[USD COST] No existe la moneda USD; cron abortado.")
            return

        products = self.search([('active', '=', True)])
        total = len(products)
        updated = 0
        failed = []

        for offset in range(0, total, self._USD_CRON_BATCH_SIZE):
            batch = products[offset:offset + self._USD_CRON_BATCH_SIZE]
            try:
                with self.env.cr.savepoint():
                    for product in batch:
                        # Cron = OdooBot: standard_price (company_dependent)
                        # y tasas se resuelven con la compañía del producto;
                        # los productos compartidos (sin compañía) siguen
                        # con la compañía activa del cron, como hoy.
                        company = product.company_id or self.env.company
                        product = product.with_company(company)
                        base_currency = company.currency_id

                        new_val = base_currency._convert(
                            product.standard_price,
                            usd_currency,
                            company,
                            fields.Date.today(),
                        )

                        _logger.debug(
                            "Producto: %s | Costo MXN: %s | Nuevo USD: %s | Empresa: %s",
                            product.name, product.standard_price, new_val, company.name,
                        )

                        product.write({
                            'usd_cost': new_val,
                            'usd_currency_id': usd_currency.id,
                        })
                        updated += 1
            except Exception:
                # El lote completo se revierte, pero el cron CONTINÚA con los
                # siguientes (antes: un producto corrupto mataba la corrida).
                failed.append((offset, offset + len(batch)))
                _logger.exception(
                    "[USD COST] Falló el lote %s-%s; se continúa con el resto.",
                    offset, offset + len(batch),
                )

        self.env.flush_all()

        if failed:
            _logger.warning(
                "=== CRON FINALIZADO CON ERRORES: %s/%s productos actualizados. "
                "Lotes fallidos: %s ===", updated, total, failed,
            )
        else:
            _logger.info(
                "=== CRON FINALIZADO: %s productos procesados ===", updated,
            )