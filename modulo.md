## ./__init__.py
```py
from . import models```

## ./__manifest__.py
```py
{
    'name': 'Product Multi-Currency Costing (MXN/USD)',
    'version': '19.0.1.0.3',
    'category': 'Inventory/Purchase',
    'summary': 'Manage product costs in USD while keeping MXN as base',
    'author': 'Alphaqueb Consulting',
    'depends': ['product', 'stock', 'account', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/stock_valuation_layer_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}```

## ./models/__init__.py
```py
from . import product_template
from . import stock_valuation_layer```

## ./models/product_template.py
```py
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_currency_id = fields.Many2one(
        'res.currency', string='USD Currency',
        default=lambda self: self.env.ref('base.USD').id
    )
    
    # Campo calculado que reacciona a cambios en standard_price (MXN)
    usd_cost = fields.Monetary(
        string='Costo USD',
        compute='_compute_usd_cost',
        currency_field='usd_currency_id',
        store=True, # Lo guardamos para que sea filtrable en listas
        help="Equivalente en USD del costo principal en MXN"
    )

    @api.depends('standard_price', 'usd_currency_id')
    def _compute_usd_cost(self):
        """Calcula USD basado en el MXN (standard_price) y la tasa actual"""
        for record in self:
            if record.standard_price and record.usd_currency_id:
                # Convertimos de MXN (Compañía) a USD
                record.usd_cost = record.env.company.currency_id._convert(
                    record.standard_price, 
                    record.usd_currency_id, 
                    record.env.company, 
                    fields.Date.today()
                )
            else:
                record.usd_cost = 0.0```

## ./models/stock_valuation_layer.py
```py
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
            )```

## ./views/product_template_views.xml
```xml
<odoo>
    <!-- Agregar a la Vista Lista -->
    <record id="product_template_tree_view_usd" model="ir.ui.view">
        <field name="name">product.template.tree.usd</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_tree_view"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='standard_price']" position="after">
                <field name="usd_cost" widget="monetary" string="Costo USD"/>
            </xpath>
        </field>
    </record>

    <!-- Agregar al Formulario -->
    <record id="product_template_form_view_inherit_cost" model="ir.ui.view">
        <field name="name">product.template.form.inherit.cost</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_only_form_view"/>
        <field name="arch" type="xml">
            <xpath expr="//div[@name='standard_price_uom']" position="after">
                <field name="usd_currency_id" invisible="1"/>
                <label for="usd_cost"/>
                <div class="o_row">
                    <field name="usd_cost" widget="monetary" readonly="1"/>
                    <span>USD</span>
                </div>
            </xpath>
        </field>
    </record>
</odoo>```

## ./views/stock_valuation_layer_views.xml
```xml
<odoo>
    <record id="stock_valuation_layer_tree_usd" model="ir.ui.view">
        <field name="name">stock.valuation.layer.tree.usd</field>
        <field name="model">stock.valuation.layer</field>
        <field name="inherit_id" ref="stock_account.stock_valuation_layer_tree"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='unit_cost']" position="after">
                <field name="usd_unit_cost" string="Costo Unit. USD" optional="show" digits="[12,4]"/>
            </xpath>
            <xpath expr="//field[@name='value']" position="after">
                <field name="usd_value" string="Valor Total USD" optional="show" sum="Total USD"/>
            </xpath>
        </field>
    </record>
</odoo>```

