{
    'name': 'Recruitment Website',
    'version': '1.0',
    'summary': 'Custom recruitment process with 3 rounds',
    'description': 'Professional recruitment website with dashboard, job positions, application form, and round tracking',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/company_info.xml',
        'views/job_position.xml',
        'views/applicant.xml',
        'views/contact.xml',
        'views/recruitment.xml',
        'views/dashboard.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'recruitment_website/static/src/js/dashboard.js',
            'recruitment_website/static/src/scss/dashboard.css',
        ],
        
    },
}