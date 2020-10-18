# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Partner Structure",
    "version": "12.0.2.0.0",
    "author": "Akretion",
    "website": "www.akretion.com",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": [
        "contacts",
        "partner_category_type",  # https://github.com/clementmbr/band-booking
    ],
    "data": [
        # Data
        "data/res_partner_category_noupdate.xml",
        # Views
        "views/res_partner_views.xml",
        "views/contact_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "application": False,
}
