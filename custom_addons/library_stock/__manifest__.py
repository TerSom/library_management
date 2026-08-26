{
    'name': 'Library Stock Integration',
    'version': '1.0',
    'license': 'LGPL-3',
    'summary': 'Integrasi Peminjaman Buku dengan Modul Inventory (Gudang) Odoo',
    'author': 'Terry',
    'depends': ['library_management', 'stock'],
    'data': [
        'views/book_inherit_view.xml',
        'views/loan_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}