# -*- coding: utf-8 -*-
{
    'name': "Tracking view fix",

    'summary': """
        Change the tracking view to add responsable.
    """,

    'description': """
        Change the tracking view to add responsable.
    """,

    'author': "Xphera",
    'website': "http://xphera.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_stock_traceability.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
