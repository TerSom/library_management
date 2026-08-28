{
    'name': 'Library Calendar Integration',
    'version': '1.0',
    'license': 'LGPL-3',
    'summary': 'Otomatis membuat jadwal di kalender untuk tenggat pengembalian buku.',
    'author': 'Terry',
    'depends': ['library_management', 'calendar'],
    'data': [
        'views/loan_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}