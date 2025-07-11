# -*- coding: utf-8 -*-
{
    'name': 'Car Repairing and Servicing',
    # 'version': '18.0.2.0.1',
    'summary': 'Car Repairing',
    'sequence': 10,
    'description': """Car Repairing""",
    'author': 'Dhaval Desai',
    'website': 'https://www.upwork.com/freelancers/~01b41453a710f4c7c1',
    'category': 'Service',
    'depends': ['base', 'contacts', 'sale', 'sale_management', 'stock', 'purchase', 'account', 'web', 'l10n_in', 'hr'],
    'data': [
            'security/ir.model.access.csv',
            'data/cars.xml',
            'data/ir_sequence_data.xml',
            'data/notification_data.xml',
            'data/ir_cron.xml',
            'data/product_category.xml',
            'views/res_config_settings_view.xml',
            'views/car_model_view.xml',
            'views/res_partner_view.xml',
            'views/product_view.xml',
            'views/job_card_view.xml',
            'views/sale_order_view.xml',
            'views/account_move_view.xml',
            'views/res_partner_view_activity.xml',
            'report/box_report_layout.xml',
            'report/invoice_report.xml',
            'report/sale_report.xml',
            'report/job_card_report.xml',
            'report/job_card_inspection.xml',
            'report/job_card_only_inspection.xml',
            # 'views/assets.xml',
    ],
    # 'assets': {
    # 'web.assets_backend': [
    #     'car_repair_services/static/src/js/catalog.js',
    # ]
    # },
    
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
