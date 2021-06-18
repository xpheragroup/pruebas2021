# -*- coding: utf-8 -*-
{
    'name': "Overwrite Mail",

    'summary': """
        This module overwrite and changes mail funcionality to fulfill requeriments.""",

    'description': """
        This module overwrite and changes mail funcionality to fulfill requeriments.
    """,

    'author': "Xphera S.A.S.",
    'website': "http://xphera.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

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
    'qweb':['static/src/xml/custom_thread.xml']
}
