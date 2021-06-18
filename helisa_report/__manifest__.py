{
    'name': "Helisa Report",
    'version': '0.1',
    'summary': """
        This module adds Helisa migration report funcionality to fulfill Accounting requeriments.""",
    'description': """
        This module adds Helisa migration report funcionality to fulfill Accounting requeriments.
    """,

    'author': "Xphera S.A.S.",
    'website': "http://xphera.co",
    'category': 'Accounting',
    'depends': ['base', 'account'],
    'data': [
        'views/views.xml',
    ],
    'external_dependencies': {
        'python': ['xlwt'],
    }
}
