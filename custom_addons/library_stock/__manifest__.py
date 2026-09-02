{
    'name': 'Library Stock Integration',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'summary': 'Integrasi Peminjaman Buku dengan Modul Inventory (Gudang) Odoo',
    'author': 'Terry',
    'depends': ['library_management', 'stock'],
    'data': [
        'views/book_inherit_view.xml',
        'views/loan_inherit_view.xml',
        'views/picking_inherit.xml',
    ],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'auto_install': False,
}
