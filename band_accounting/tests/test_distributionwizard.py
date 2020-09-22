# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import CommonSetup


class TestDistributionWizard(CommonSetup):
    def test_distrib_no_existing_invoice(self):
        self.distrib = self.env["fee.distribution.wizard"].create(
            {"lead_id": self.lead.id}
        )
        self.env["fee.distribution.line.wizard"].create(
            [
                {
                    "fee_distribution_wizard_id": self.distrib.id,
                    "participant_id": self.artist.id,
                    "fee_product_id": self.prod_fee.id,
                    "fee_amount": 150.00,
                },
                {
                    "fee_distribution_wizard_id": self.distrib.id,
                    "participant_id": self.agent.id,
                    "commission_product_id": self.prod_com.id,
                    "commission_amount": 150.00,
                },
            ]
        )
        self.distrib.action_fill_invoices()
        for inv in self.lead.participant_invoice_ids:
            self.assertEqual(inv.amount_total, 172.5)
            if inv.partner_id.id == self.artist.id:
                self.assertEqual(
                    inv.invoice_line_ids[0].product_id.id, self.prod_fee.id
                )
            if inv.partner_id.id == self.agent.id:
                self.assertEqual(
                    inv.invoice_line_ids[0].product_id.id, self.prod_com.id
                )

    def _create_distrib_with_fee(self, lead, partner, product, amount):
        # Create a distribution wizard
        distrib = self.env["fee.distribution.wizard"].create({"lead_id": lead.id})
        self.env["fee.distribution.line.wizard"].create(
            [
                {
                    "fee_distribution_wizard_id": distrib.id,
                    "participant_id": partner.id,
                    "fee_product_id": product.id,
                    "fee_amount": amount,
                },
            ]
        )
        return distrib

    def test_distrib_existing_invoice_superior(self):
        self.artist_invoice = self.create_open_invoice(
            self.artist, self.prod_fee, 200, "in_invoice"
        )
        self.artist_invoice.bill_lead_id = self.lead

        self.distrib = self._create_distrib_with_fee(
            self.lead, self.artist, self.prod_fee, 150
        )
        with self.assertRaises(UserError):
            self.distrib.action_fill_invoices()

    def test_distrib_existing_invoice_equal(self):
        self.distrib = self._create_distrib_with_fee(
            self.lead, self.artist, self.prod_fee, 200
        )
        self.assertTrue(self.distrib.action_fill_invoices())

    def test_distrib_existing_invoice_inferior(self):
        self.distrib = self._create_distrib_with_fee(
            self.lead, self.artist, self.prod_fee, 250
        )
        self.assertTrue(self.distrib.action_fill_invoices())
        inv = self.lead.participant_invoice_ids[0]
        self.assertEqual(inv.invoice_line_ids[0].price_subtotal, 250)
