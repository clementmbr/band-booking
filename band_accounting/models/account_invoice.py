# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _sum_lines_prod_category(self, inv, cat):
        """Returns the subtotal of invoice lines from a specific product category"""
        line_ids = inv.invoice_line_ids.filtered(lambda l: l.product_id.categ_id == cat)
        return sum(line_ids.mapped("price_subtotal"))

    @api.depends("invoice_line_ids")
    def _compute_amount_expense(self):
        categ_expense = self.env.ref("band_accounting.prod_categ_expense")
        for inv in self:
            inv.amount_expense = self._sum_lines_prod_category(inv, categ_expense)

    @api.depends("invoice_line_ids")
    def _compute_amount_fee(self):
        categ_fee = self.env.ref("band_accounting.prod_categ_fee")
        for inv in self:
            inv.amount_fee = self._sum_lines_prod_category(inv, categ_fee)

    @api.depends("invoice_line_ids")
    def _compute_amount_commission(self):
        categ_commission = self.env.ref("band_accounting.prod_categ_commission")
        for inv in self:
            inv.amount_commission = self._sum_lines_prod_category(inv, categ_commission)

    # one2one relation with leads pointing to this invoice through `revenue_invoice_id`
    invoice_lead_id = fields.Many2one(
        string="Invoice's Opportunity",
        comodel_name="crm.lead",
        ondelete="set null",
        help="Related Opportunity",
    )

    bill_lead_id = fields.Many2one(
        string="Bill's Opportunity",
        comodel_name="crm.lead",
        ondelete="set null",
        help="Related Opportunity",
    )

    amount_expense = fields.Monetary(
        string="Expenses",
        currency_field="company_currency_id",
        readonly=True,
        compute="_compute_amount_expense",
        store=True,
        help="Amount of the Invoice's Expenses lines",
    )
    amount_fee = fields.Monetary(
        string="Fee",
        currency_field="company_currency_id",
        readonly=True,
        compute="_compute_amount_fee",
        store=True,
        help="Amount of the Invoice's Fee lines",
    )
    amount_commission = fields.Monetary(
        string="Commission",
        currency_field="company_currency_id",
        readonly=True,
        compute="_compute_amount_commission",
        store=True,
        help="Amount of the Invoice's Commission lines",
    )

    def name_get(self):
        """Override native name_get to display custom invoice name in leads"""
        res = []
        if self._context.get("default_type") == "opportunity" or self._context.get(
            "revenue_income_display_name"
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

    @api.constrains("invoice_lead_id")
    def _remove_invoice_lead_id_on_others(self):
        # Check if there is 'invoice_lead_id' fields duplicates when many
        # invoices have this field changed at the same time (e.g. by server action)
        lead_seen = self.env["crm.lead"]
        for inv in self:
            if inv.invoice_lead_id not in lead_seen:
                lead_seen |= inv.invoice_lead_id
            else:
                raise ValidationError(
                    _(
                        "There cannot be more than 1 invoice referring to the same "
                        "'invoice_lead_id'.\nCheck these invoices : {}".format(self.ids)
                    )
                )
        # Remove 'invoice_lead_id' from other invoices related to the same lead
        # as our current invoice triggered by this constrains decorator
        for inv in self:
            if inv.invoice_lead_id:
                all_inv = self.env["account.invoice"].search(
                    [("invoice_lead_id", "=", inv.invoice_lead_id.id)]
                )
                (all_inv - inv).write({"invoice_lead_id": False})
