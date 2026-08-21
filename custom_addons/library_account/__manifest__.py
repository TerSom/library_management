{
    'name': 'Library Accounting Integration',
    'version': '1.0',
    'summary': 'Menjembatani Denda Perpustakaan dengan Modul Invoicing/Accounting Odoo',
    'author': 'Terry',
    'depends': ['library_management', 'account'],
    'data': [
        'views/loan_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}