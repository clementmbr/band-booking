# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Band Booking",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "www.akretion.com.br",
    "depends": [
        # Native addons
        "crm",
        "event",
        "partner_autocomplete",
        # OCA addons
        "crm_stage_type",  # https://github.com/OCA/crm
        "partner_external_map",  # https://github.com/OCA/partner-contact
        # band special addons
        "partner_structure",  # https://github.com/clementmbr/band-booking
    ],
    "data": [
        # Data
        "data/crm_stage.xml",
        "data/crm_lost_reason.xml",
        # Security
        "security/partner_structure_security.xml",
        # Views
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
        "views/contact_views.xml",
        "views/crm_lead_views.xml",
        "views/event_views.xml",
        "views/assets.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
