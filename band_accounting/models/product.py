# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_band_accounting_categ(self):
        """Return the purchase and saleable categories defined in band_accounting datas
        """
        purchase_xml_ids = [
            "prod_categ_expense",
            "prod_categ_commission",
            "prod_categ_fee",
        ]
        saleable_xml_ids = ["prod_categ_saleable"]

        purchase_categ_ids = self.env["product.category"]
        saleable_categ_ids = self.env["product.category"]

        for xml_id in purchase_xml_ids:
            purchase_categ_ids |= self.env.ref("band_accounting." + xml_id)
        for xml_id in saleable_xml_ids:
            saleable_categ_ids |= self.env.ref("band_accounting." + xml_id)

        return purchase_categ_ids, saleable_categ_ids

    @api.onchange("categ_id")
    def _onchange_categ_id(self):
        purchase_categ_ids, saleable_categ_ids = self._get_band_accounting_categ()

        for prod in self:
            if prod.categ_id in purchase_categ_ids:
                prod.update({"purchase_ok": True, "sale_ok": False, "type": "service"})
            if prod.categ_id in saleable_categ_ids:
                prod.update({"purchase_ok": False, "sale_ok": True, "type": "service"})

    @api.onchange("purchase_ok", "sale_ok", "type")
    def _onchange_restricted_fields(self):
        vals = {"warning": {"title": "Warning"}}
        purchase_categ_ids, saleable_categ_ids = self._get_band_accounting_categ()

        for prod in self:
            if prod.purchase_ok and prod.categ_id in saleable_categ_ids:
                prod.update({"purchase_ok": False})
                vals["warning"]["message"] = _(
                    "A product from the category 'Saleable' cannot be purchased."
                )
                return vals
            if not prod.purchase_ok and prod.categ_id in purchase_categ_ids:
                prod.update({"purchase_ok": True})
                vals["warning"]["message"] = _(
                    "A product from the categories 'Expense', 'Commission' or "
                    "'Fee' must be purchaseable."
                )
                return vals
            if not prod.sale_ok and prod.categ_id in saleable_categ_ids:
                prod.update({"sale_ok": True})
                vals["warning"]["message"] = _(
                    "A product from the category 'Saleable' must be saleable."
                )
                return vals
            if prod.sale_ok and prod.categ_id in purchase_categ_ids:
                prod.update({"sale_ok": False})
                vals["warning"]["message"] = _(
                    "A product from the category 'Expense', 'Commission' or "
                    "'Fee' cannot be saleable."
                )
                return vals
            if (
                prod.categ_id in saleable_categ_ids | purchase_categ_ids
                and prod.type != "service"
            ):
                prod.update({"type": "service"})
                vals["warning"]["message"] = _(
                    "A product from the categories 'Saleable', 'Expense', "
                    "'Commission' or 'Fee' must have a 'service' type."
                )
                return vals

    def name_get(self):
        """Override native name_get to display custom product name in invoice lines"""
        res = super().name_get()
        if self._context.get("display_name_invoice"):
            newres = []
            for (id, name) in res:
                prod_id = self.env["product.product"].browse([id])
                if prod_id.categ_id:
                    name = "[" + prod_id.categ_id.name + "] " + name
                newres.append((id, name))
            res = newres
        return res
