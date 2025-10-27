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
        'web.assets_frontend': [
            'external_invoice_request/static/src/js/external_sale_invoice_form.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
