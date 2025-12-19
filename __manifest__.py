{
    'name': 'Product Multi-Currency Costing (MXN/USD)',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Manage product costs in USD while keeping MXN as base',
    'description': """
        - Agrega costo en moneda extranjera (USD) a los productos.
        - Conversión automática de Costo USD -> Costo MXN.
        - Wizard para actualizar costos masivamente según el tipo de cambio del día.
    """,
    'author': 'Alphaqueb Consulting',
    'depends': ['product', 'stock', 'account', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/stock_valuation_layer_views.xml',
        
    ],
    'installable': True,
    'license': 'LGPL-3',
}
