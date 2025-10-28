{
    'name': 'OWL External Invoice Request',
    'version': '1.0',
    'summary': 'Allow partners to request and download invoices via public link',
    'category': 'Accounting',
    'author': 'Adita Putri Puspaningrum',
    'depends': [
        'base',
        'contacts',
        'sale', 
        'account', 
        'web',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'views/external_sale_invoice_templates.xml',
    ],
    'assets': {
        'external_invoice_request.assets_standalone_app': [
            ('include', 'web._assets_helpers'),
            ('include', 'web._assets_bootstrap'),
            ('include', 'web._assets_core'), 
            'external_invoice_request/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
