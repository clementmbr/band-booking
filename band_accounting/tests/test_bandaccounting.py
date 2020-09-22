# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import common


class TestBandAccounting(common.TransactionCase):
    def _create_open_invoice(self, partner_id, product_id, amount):
        # Create an invoice
        vals_inv = {
            "type": "out_invoice",
            "partner_id": partner_id.id,
        }
        vals_inv = self.env["account.invoice"].play_onchanges(
            vals_inv, list(vals_inv.keys())
        )
        invoice = self.env["account.invoice"].create(vals_inv)
        # Add invoice_line to revenue_invoice
        vals_line = {
            "invoice_id": invoice.id,
            "product_id": product_id.id,
            "quantity": 1,
            "price_unit": amount,
        }
        vals_line = self.env["account.invoice.line"].play_onchanges(
            vals_line, list(vals_line.keys())
        )
        self.env["account.invoice.line"].create(vals_line)
        invoice.compute_taxes()
        invoice.action_invoice_open()

        return invoice

    def setUp(self):
        super(TestBandAccounting, self).setUp()

        # People
        self.user = self.ref("base.user_admin")
        self.artist = self.env["res.partner"].create(
            {
                "name": "Roda",
                "company_type": "person",
                "supplier": True,
                "country": self.ref("base.fr"),
            }
        )
        self.agent = self.env["res.partner"].create(
            {
                "name": "Joa",
                "company_type": "person",
                "supplier": True,
                "country": self.ref("base.fr"),
            }
        )
        self.festival = self.env["res.partner"].create(
            {
                "name": "Super Festival",
                "structure_type": "festival",
                "company_type": "company",
                "country": self.ref("base.fr"),
            }
        )
        # Products
        self.prod_gig = self.env["product.product"].create(
            {
                "name": "Gig",
                "sale_ok": True,
                "type": "service",
                "categ_id": self.ref("band_accounting.prod_categ_saleable"),
            }
        )
        self.prod_fee = self.env["product.product"].create(
            {
                "name": "Fee",
                "purchase_ok": True,
                "type": "service",
                "categ_id": self.ref("band_accounting.prod_categ_fee"),
            }
        )
        self.prod_com = self.env["product.product"].create(
            {
                "name": "Fee",
                "purchase_ok": True,
                "type": "service",
                "categ_id": self.ref("band_accounting.prod_categ_commission"),
            }
        )
        # Lead
        self.lead = self.env["crm.lead"].create(
            {"partner_id": self.festival.id, "name": "Gig opportunity"}
        )
        self.revenue_invoice = self._create_open_invoice(
            self.festival, self.prod_gig, 2000
        )

    def test_name_get_invoice(self):
        name_inv = self.revenue_invoice.with_context(
            {"revenue_income_display_name": True}
        ).name_get()[0][1]
        self.assertTrue(name_inv.startswith("$ 2300.0 - Super Festival - INV/"))
        self.assertTrue("2300.0" in name_inv and "- Super Festival - INV/" in name_inv)

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
        self.artist_invoice = self._create_open_invoice(self.artist, self.prod_fee, 200)
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
