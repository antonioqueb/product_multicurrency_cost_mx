{
    'name': 'Product Multi-Currency Costing (MXN/USD)',
    'version': '19.0.1.0.4',
    'category': 'Inventory/Purchase',
    'summary': 'Manage product costs in USD while keeping MXN as base',
    'author': 'Alphaqueb Consulting',
    'depends': ['product', 'stock', 'account', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/product_template_views.xml',
        'views/stock_move_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}