# -*- coding: utf-8 -*-
{
    'name': "Xphera Base Import Trace",
    'version': '0.1',
    'summary': """
        This module overwrite and changes the model import through a file avoiding duplicates.""",
    'description': """
        This module overwrite and changes the model import through a file avoiding duplicates using file names and MD5 hash.
    """,

    'author': "Xphera S.A.S.",
    'website': "http://xphera.co",
    'category': 'Base',
    'depends': ['base_import'],
    'data': [
        'security/ir.model.access.csv'
    ],
}
