# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lead_id = fields.Many2one(
        string="Opportunity",
        comodel_name="crm.lead",
        ondelete="set null",
        readonly=True,
        help="Related Opportunity",
    )

    def name_get(self):
        """Override native name_get to display custom invoice name in leads"""
        res = []
        if self._context.get("default_type") == "opportunity" or self._context.get(
            "lead_income_display_name"
        ):
            for inv in self:
                name = "{}".format(inv.amount_total)
                if inv.currency_id.position == "before":
                    name = "{} ".format(inv.currency_id.symbol) + name
                else:
                    name += " {}".format(inv.currency_id.symbol)
                if inv.partner_id:
                    name += " - {}".format(inv.partner_id.name)
                if inv.number:
                    name += " - {}".format(inv.number)

                res.append((inv.id, name))
        else:
            res = super().name_get()
        return res
