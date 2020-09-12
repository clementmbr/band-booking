import logging

from lxml import etree

from odoo import SUPERUSER_ID, _, api
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(_("Deleting native product categories for 'band_accounting'..."))

    # Delete unused native product categories
    # ==========================
    data_elements = etree.parse(file_open("product/data/product_data.xml"))
    model_elements = data_elements.xpath("//record[@model='product.category']")

    categ_expense = env.ref("band_accounting.product_category_expense")
    categ_all = env.ref("product.product_category_all")

    to_unlink = env["product.category"]
    for el in model_elements:
        if el.get("id") != "product_category_all":
            try:
                categ_id = env.ref("product." + el.get("id"))
            except ValueError:
                continue
            prod_ids = env["product.template"].search([("categ_id", "=", categ_id.id)])

            if el.get("id") == "cat_expense":
                prod_ids.write({"categ_id": categ_expense.id})
            else:
                prod_ids.write({"categ_id": categ_all.id})

            to_unlink |= categ_id

    to_unlink.unlink()
