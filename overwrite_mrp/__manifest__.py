# -*- coding: utf-8 -*-
{
    'name': "Xphera Fabrication Module",
    'version': '0.1',
    'summary': """
        This module overwrite and changes and create some modules for custom fabrication.""",
    'description': """
        This module overwrite and changes the model mrp.bom to add new fields.
    """,

    'author': "Xphera S.A.S.",
    'website': "http://xphera.co",
    'category': 'Base',
    'depends': ['account', 'mrp', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/approve_material_list_view.xml',
        'views/material_list_group_view.xml',
    ],
}
