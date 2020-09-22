# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import CommonSetup


class TestLeadInvoice(CommonSetup):
    def test_name_get_invoice(self):
        name_inv = self.revenue_invoice.with_context(
            {"revenue_income_display_name": True}
        ).name_get()[0][1]
        self.assertTrue(name_inv.startswith("$ 2300.0 - Super Festival - INV/"))
        self.assertTrue("2300.0" in name_inv and "- Super Festival - INV/" in name_inv)

    def test_check_duplicate_participant_invoice(self):
        artist_bill_1 = self.create_open_invoice(
            self.artist, self.prod_fee, 150, "in_invoice"
        )
        self.lead.participant_invoice_ids = [(6, 0, [artist_bill_1.id])]

        artist_bill_2 = self.create_open_invoice(
            self.artist, self.prod_fee, 150, "in_invoice"
        )
        with self.assertRaises(ValidationError):
            self.lead.participant_invoice_ids = [(4, artist_bill_2.id, 0)]

        # Possible to add an second invoice for the same artist if the first is paid
        self.register_invoice_payment(artist_bill_1)
        self.lead.participant_invoice_ids = [(6, 0, [artist_bill_1.id])]
        self.assertTrue(
            self.lead.write({"participant_invoice_ids": [(4, artist_bill_2.id, 0)]})
        )
