# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Band Accounting",
    "summary": """
        Manage revenue, fees and expenses related to an Opportunity""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "http://akretion.com",
    "depends": [
        # Native addons
        "crm",
        "account",
        "l10n_generic_coa",
        # OCA addons
        "onchange_helper",  # https://github.com/OCA/server-tools
    ],
    "data": [
        # Data
        "data/product_category.xml",
        # Views
        "views/account_invoice_views.xml",
        "views/crm_lead_views.xml",
        # Wizard
        "wizard/fee_distribution_wizard_view.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
