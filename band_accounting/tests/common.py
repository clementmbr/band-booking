# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class CommonSetup(common.TransactionCase):
    def create_open_invoice(self, partner_id, product_id, amount, in_out):
        """
        `in_out` must be "in_invoice" for supplier Bills or
        "out_invoice" for customer Invoice.
        """
        # Create an invoice
        vals_inv = {
            "type": in_out,
            "partner_id": partner_id.id,
        }
        vals_inv = self.env["account.invoice"].play_onchanges(
            vals_inv, list(vals_inv.keys())
        )
        invoice = self.env["account.invoice"].create(vals_inv)
        # Add invoice_line to invoice
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

    def register_invoice_payment(self, invoice):
        vals_payment = (
            self.env["account.payment"]
            .with_context(default_invoice_ids=[(4, invoice.id, False)])
            .default_get(list(self.env["account.payment"].fields_get()))
        )
        vals_payment = self.env["account.payment"].play_onchanges(
            vals_payment, list(vals_payment.keys())
        )

        payment_invoice = self.env["account.payment"].create(vals_payment)
        payment_invoice.action_validate_invoice_payment()

    def setUp(self):
        super().setUp()

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
                "name": "Commission",
                "purchase_ok": True,
                "type": "service",
                "categ_id": self.ref("band_accounting.prod_categ_commission"),
            }
        )
        # Lead
        self.lead = self.env["crm.lead"].create(
            {"partner_id": self.festival.id, "name": "Gig opportunity"}
        )
        self.revenue_invoice = self.create_open_invoice(
            self.festival, self.prod_gig, 2000, "out_invoice"
        )
