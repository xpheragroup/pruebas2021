# -*- coding: utf-8 -*-
{
    'name': "Módulo Xphera",

    'summary': """
        Modificaciones a validación de campos.""",

    'description': """
        Modificaciones a validación de campos.
    """,

    'author': "Xphera S.A.S.",
    'website': "http://xphera.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.20',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
