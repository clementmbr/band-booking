# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import logging
from os import listdir

from lxml import etree

from odoo import SUPERUSER_ID, _, api, tools
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Load mandatory datas used in python files before loading them"""
    _logger.info(_("Loading crm_booking data..."))

    tools.convert_file(
        cr,
        "crm_booking",
        "data/res_partner_category.xml",
        None,
        mode="init",
        noupdate=True,
        kind="init",
        report=None,
    )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(_("Preparing datas for 'crm_booking'..."))

    # Delete unused native datas
    # ==========================
    def _unlink_data(model, module, file_path):
        data_elements = etree.parse(file_open(file_path))
        model_elements = data_elements.xpath("//record[@model='{}']".format(model))

        to_unlink = env["{}".format(model)]
        for el in model_elements:
            el_xmlid = "{}.".format(module) + el.get("id")
            try:
                to_unlink |= env.ref(el_xmlid)
            except ValueError:
                continue
        to_unlink.unlink()

    # Delete native lost reasons
    _unlink_data("crm.lost.reason", "crm", "crm/data/crm_data.xml")
    # Delete native crm stages
    _unlink_data("crm.stage", "crm", "crm/data/crm_stage_data.xml")

    # Add all the users do 'group_use_lead' in order to display Leads for everybody
    # =============================================================================
    users = env["res.users"].search([("id", "!=", env.ref("base.public_user").id)])
    group_use_lead = env.ref("crm.group_use_lead")
    group_use_lead.users = [(6, 0, users.ids)]

    # Load demo records
    # =================
    if tools.config.get("demo_booking"):
        tools.convert_file(
            cr,
            "crm_booking",
            "demo/res.partner-demo.csv",
            None,
            mode="init",
            noupdate=True,
            kind="init",
            report=None,
        )

        image_folder = "./odoo/external-src/crm-booking/crm_booking/static/img/"
        image_files = {}
        for file_name in listdir(image_folder):
            if file_name.split("-")[1] == "demo":
                image_files[file_name.split("-")[0]] = image_folder + file_name

        for name, img_path in image_files.items():
            with open(img_path, "rb") as file:
                partner = env.ref("__import__.{}".format(name))
                partner.image = base64.b64encode(file.read())
