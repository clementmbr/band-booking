# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom CRM for Booking",
    "version": "12.0.0.0.1",
    "author": "Akretion",
    "website": "www.akretion.com",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": [
        "crm",
        "event",
        "partner_autocomplete",
        "crm_stage_type",  # https://github.com/OCA/crm
        "partner_external_map",  # https://github.com/OCA/partner-contact
        "partner_category_type",  # https://github.com/clementmbr/crm-booking
    ],
    "data": [
        # Data
        "data/res_partner_category.xml",
        "data/res_partner_category_noupdate.xml",
        # Security
        "security/partner_structure_security.xml",
        # Wizards
        "wizard/crm_lead_to_opportunity_views.xml",
        # Views
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
        "views/contact_views.xml",
        "views/calendar_views.xml",
        "views/crm_lead_views.xml",
        "views/event_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "application": False,
}
