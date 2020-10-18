# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class PartnerCategory(models.Model):
    _inherit = "res.partner.category"
    _order = "sequence"

    sequence = fields.Integer(
        "Sequence", help="The order a Tag will be displayed when searching"
    )

    # Make the distinction to display a tag in Structures or Contacts partners
    category_type = fields.Selection(
        string="Category Type",
        selection=[("structure", "Structure"), ("contact", "Contact")],
        store=True,
        required=True,
    )

    # Special bool to distinguish mandatory tags related to "partner type" like
    # 'venue' or 'contact' from the other classic tags
    is_partner_type_categ = fields.Boolean(required=True, default=False)

    def unlink(self):
        if self.filtered("is_partner_type_categ"):
            raise UserError(
                _(
                    "It is not allowed to unlink Tags related to a partner type like "
                    "'festival', 'venue' or 'partner'"
                )
            )
        return super().unlink()
