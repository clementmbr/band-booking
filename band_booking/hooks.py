# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import logging
from os import listdir, path

from lxml import etree

from odoo import SUPERUSER_ID, _, api, tools
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(_("Preparing datas for 'band_booking'..."))

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
        _logger.info(_("Loading demo datas for 'band_booking'..."))

        files = [
            "demo/res.partner-festival-demo.csv",
            "demo/res.partner-venue-demo.csv",
            "demo/res.partner-contact-demo.csv",
        ]
        for file in files:
            tools.convert_file(
                cr,
                "band_booking",
                file,
                None,
                mode="init",
                noupdate=True,
                kind="init",
                report=None,
            )

        image_folder = "./odoo/external-src/crm-booking/band_booking/static/img/"
        image_files = {}
        for file_name in listdir(image_folder):
            # To load a demo image, its name must be in the format "xml_id-demo.ext"
            if path.splitext(file_name)[0].split("-")[1] == "demo":
                image_files[file_name.split("-")[0]] = image_folder + file_name

        for name, img_path in image_files.items():
            with open(img_path, "rb") as image_file:
                partner = env.ref("band_booking.{}".format(name))
                partner.image = base64.b64encode(image_file.read())
