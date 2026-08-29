# -*- coding: utf-8 -*-
{
    'name': "library_management",
    'summary': "Module for managing library books and loans",
    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Services/Library',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'views/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/ir_cron_data.xml',
        'data/mail_template.xml',
        'data/dashboard_data.xml',
        'views/book_view.xml',
        'views/member_view.xml',
        'views/loan_view.xml',
        'views/library_dashboard_view.xml',
        'wizard/loan_report_wizard_view.xml',
        'wizard/book_import_wizard_view.xml',
        'reports/loan_report_template.xml',
        'reports/loan_report_action.xml',
        'reports/book_report_template.xml',
        'reports/book_report_action.xml',
        'reports/member_report_template.xml',
        'reports/member_report_action.xml',
        'views/menu.xml'
        
    ],
    'assets': {
        'web.assets_backend': [
            'library_management/static/src/js/library_dashboard.js',
            'library_management/static/src/scss/library_dashboard.scss',
            'library_management/static/src/xml/library_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

