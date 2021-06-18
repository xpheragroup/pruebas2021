# -*- coding: utf-8 -*-
{
    'name': "tracking_fields",

    'summary': """
        Module to add tracking to base fields.
    """,

    'description': """
        Module to add tracking to base fields.
    """,

    'author': "Xphera",
    'website': "http://xphera.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'mrp',
                'account_accountant','stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
