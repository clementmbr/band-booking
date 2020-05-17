# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerCategory(models.Model):
    _inherit = "res.partner.category"
    _order = "sequence"

    sequence = fields.Integer(
        "Sequence", help="The order a Tag will be displayed when searching"
    )

    category_type_id = fields.Many2one(
        comodel_name="res.partner.category.type",
        help="""- 'Structure' : the tag will only be available in Structures
        - 'Contact' : the tag will only be availble in Contacts

        The category types 'Structure Type' and 'Contact Type' are only present for
        technical purpose with special tags like 'partner', 'festival' or 'venue'.""",
        store=True,
    )

    is_partner_type_categ = fields.Boolean(
        related="category_type_id.is_for_partner_type",
    )


class PartnerCategoryType(models.Model):
    """The available Category Types are defined in ../data/res_partner_category.xml
    and the user should not create new ones.

    The 2 main category types "Structure" and "Contact" allow to display Tags depending
    if it is a Contact or a Structure tag.

    The 2 other category types "Structure Type" and "Contact Type" are used for special
    tags that should not be modified by the user.
    Their related tags will inform for instance if a Structure partner is from the type
    "festival" or "venue" and if a Contact partner is from the type "partner"."""

    _name = "res.partner.category.type"
    _description = "Distinguish categories for Contacts or for Structures"

    name = fields.Char()
    is_for_partner_type = fields.Boolean()
