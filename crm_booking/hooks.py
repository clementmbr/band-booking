# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from lxml import etree

from odoo import SUPERUSER_ID, _, api
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Delete Odoo native CRM Lost reasons"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(_("Preparing datas for 'crm_booking'..."))

    crm_data_tree = etree.parse(file_open("crm/data/crm_data.xml"))
    lost_reasons = crm_data_tree.xpath("//record[@model='crm.lost.reason']")

    to_unlink = env["crm.lost.reason"]
    for lost_reason in lost_reasons:
        try:
            to_unlink |= env.ref("crm." + lost_reason.get("id"))
        except ValueError:
            continue
    to_unlink.unlink()
