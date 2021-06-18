# -*- coding: utf-8 -*-
{
    'name': "Xphera Colombian Accounting",
    'version': '0.2',
    'summary': """
        This module overwrite and changes accounting funcionality to fulfill Colombian Accounting requeriments.""",
    'description': """
        This module overwrite and changes accounting funcionality to fulfill Colombian Accounting requeriments.
    """,

    'author': "Xphera S.A.S.",
    'website': "http://xphera.co",
    'category': 'Accounting',
    'depends': ['base', 'account', 'account_reports'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}
