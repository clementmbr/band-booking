# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Band Booking",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "www.akretion.com.br",
    "depends": [
        "partner_structure",
        "base_usability",  # https://github.com/akretion/odoo-usability
        "web_form_background_color",  # https://github.com/clementmbr/crm-booking],
    ],
    "data": ["data/crm_stage.xml", "data/crm_lost_reason.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
