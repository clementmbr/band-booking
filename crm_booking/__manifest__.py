# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Custom CRM for Booking',
    'version': '12.0.0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'description':
    """
        Add a many2many field to link Opportunities to Partners
    """,
    'depends': [
        'crm',
        'event',
        'crm_stage_type', # https://github.com/OCA/crm
        'partner_external_map', # https://github.com/OCA/partner-contact

    ],
    'data': [
        'wizard/crm_lead_to_opportunity_views.xml',

        'views/res_partner_views.xml',
        'views/contact_views.xml',
        'views/calendar_views.xml',
        'views/crm_lead_views.xml',
        'views/event_views.xml',
    ],
    'installable': True,
    'application': False,
}
