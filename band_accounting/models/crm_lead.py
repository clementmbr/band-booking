# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    revenue_invoice_id = fields.Many2one(
        string="Revenue Invoice",
        comodel_name="account.invoice",
        ondelete="set null",
        help="Customer's Invoice related to this negociation",
    )

    revenue_journal_ids = fields.Many2many(
        string="Received by",
        comodel_name="account.journal",
        relation="rel_lead_revenue_journal",
        column1="lead_id",
        column2="revenue_journal_id",
        readonly=True,
        help="Payment Journal used to receive the Revenue Invoice",
    )

    settle_commission = fields.Boolean(string="Settle Commission")

    participant_invoice_ids = fields.One2many(
        string="Field name",
        comodel_name="account.invoice",
        inverse_name="lead_id",
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
        help="Payment Journal used to pay the Participant Invoices",
    )

    lead_net_income = fields.Monetary(
        string="Net Income",
        currency_field="company_currency",
        readonly=True,
        help="Net Income for the Band.\nResult from the Revenue less the participants "
        "total invoices",
    )

    @api.onchange("revenue_invoice_id")
    def _onchange_revenue_journal_ids(self):
        for lead in self:
            journal_ids = lead.revenue_invoice_id.payment_ids.mapped("journal_id")
            lead.update({"revenue_journal_ids": [(6, 0, journal_ids.ids)]})

    @api.onchange("participant_invoice_ids")
    def _onchange_participant_invoice_ids(self):
        for lead in self:
            payment_ids = lead.participant_invoice_ids.mapped("payment_ids")
            journal_ids = payment_ids.mapped("journal_id")
            lead.update({"participant_journal_ids": [(6, 0, journal_ids.ids)]})

    # TODO: hide Sale and INvoice page in contacts
