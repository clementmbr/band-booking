# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    revenue_invoice_id = fields.Many2one(
        string="Revenue Invoice",
        comodel_name="account.invoice",
        compute="_compute_revenue_invoice_id",
        inverse="_inverse_revenue_invoice_id",
        store=True,
        ondelete="set null",
        help="Customer's Invoice related to this negociation",
    )
    # Tecnical field to simulate a one2one relation between `revenue_invoice_id` and
    # invoice field `invoice_lead_id`
    revenue_invoice_ids = fields.One2many(
        comodel_name="account.invoice",
        inverse_name="invoice_lead_id",
        string="Technical Revenue Invoices",
    )

    revenue_income_state = fields.Selection(
        string="Revenue Invoice State", related="revenue_invoice_id.state",
    )

    revenue_journal_ids = fields.Many2many(
        string="Received by",
        comodel_name="account.journal",
        relation="rel_lead_revenue_journal",
        column1="lead_id",
        column2="revenue_journal_id",
        readonly=True,
        compute="_compute_revenue_journal_ids",
        help="Payment Journal used to receive the Revenue Invoice",
    )

    settle_commission = fields.Boolean(string="Settle Commission", default=True)
    settle_fee = fields.Boolean(string="Settle Fee", default=True)

    participant_invoice_ids = fields.One2many(
        string="Field name",
        comodel_name="account.invoice",
        inverse_name="bill_lead_id",
        help="Participants invoices gathering the Fee, Expenses and Commission "
        "for each participant",
    )

    participant_journal_ids = fields.Many2many(
        string="Paid by",
        comodel_name="account.journal",
        relation="rel_lead_participant_journal",
        column1="lead_id",
        column2="participant_journal_id",
        readonly=True,
        compute="_compute_participant_invoice_ids",
        help="Payment Journal used to pay the Participant Invoices",
    )

    lead_net_income = fields.Monetary(
        string="Net Income",
        currency_field="company_currency",
        readonly=True,
        compute="_compute_lead_net_income",
        help="Net Income for the Band.\nResult from the Revenue less the participants "
        "total invoices",
    )

    @api.depends("revenue_invoice_ids")
    def _compute_revenue_invoice_id(self):
        """Triggered when an invoice fill its field `invoice_lead_id` and a
        new item is added to the `revenue_invoice_ids` lead field."""
        for lead in self:
            if len(lead.revenue_invoice_ids) > 0:
                lead.revenue_invoice_id = lead.revenue_invoice_ids[0]
        # FIXME: when you create an invoice from the "create and edit" button in
        # a lead being created, the invoice created doesn't appear in the
        # revenue_invoice_id field until you save the lead.
        # (because the inverse method is triggered only when saving the lead)

    def _inverse_revenue_invoice_id(self):
        """Triggered when `revenue_invoice_id` is filled manually
        instead of being computed by its dependency `revenue_invoice_ids`"""
        for lead in self:
            if len(lead.revenue_invoice_ids) > 0:
                # delete `invoice_lead_id` reference from old invoice
                # stored in `revenue_invoice_ids`
                inv = lead.env["account.invoice"].browse(lead.revenue_invoice_ids[0].id)
                inv.invoice_lead_id = False
            # Now set the new `invoice_lead_id` reference to the new invoice
            # written in `revenue_invoice_id`
            if lead.revenue_invoice_id:
                lead.revenue_invoice_id.invoice_lead_id = lead

    @api.depends("revenue_invoice_id")
    def _compute_revenue_journal_ids(self):
        for lead in self:
            journal_ids = lead.revenue_invoice_id.payment_ids.mapped("journal_id")
            lead.revenue_journal_ids = [(6, 0, journal_ids.ids)]

    @api.depends("participant_invoice_ids")
    def _compute_participant_invoice_ids(self):
        for lead in self:
            payment_ids = lead.participant_invoice_ids.mapped("payment_ids")
            journal_ids = payment_ids.mapped("journal_id")
            lead.participant_journal_ids = [(6, 0, journal_ids.ids)]

    @api.depends("participant_invoice_ids", "revenue_invoice_id")
    def _compute_lead_net_income(self):
        for lead in self:
            lead.lead_net_income = lead.revenue_invoice_id.amount_total - sum(
                lead.participant_invoice_ids.mapped("amount_total")
            )

    @api.constrains("participant_invoice_ids")
    def _check_duplicate_participant_invoice(self):
        for lead in self:
            partner_seen = self.env["res.partner"]
            for inv in lead.participant_invoice_ids:
                if inv.partner_id not in partner_seen:
                    partner_seen |= inv.partner_id
                elif inv.state not in ["paid", "cancel"]:
                    raise ValidationError(
                        _(
                            "There is already an opened bill for {}.\n"
                            "Please update or cancel it instead of adding a new one"
                            ".".format(inv.partner_id.name)
                        )
                    )

    def button_add_fees(self):
        self.ensure_one()
        fee_distrib_view_xmlid = "band_accounting.fee_distribution_wizard_view_form"
        return {
            "context": {
                "default_lead_id": self.id,
                "default_company_id": self.company_id.id,
                "revenue_income_display_name": True,
            },
            "name": _("Distribute Fees and Commissions to the participants"),
            "view_id": self.env.ref(fee_distrib_view_xmlid).id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "fee.distribution.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    # TODO:
    # - hide Sale and INvoice page in contacts
    # - add analytic account to lead and all the related invoice.lines
    # - emoji green/yellow/red if invoice receveived/open/draft
