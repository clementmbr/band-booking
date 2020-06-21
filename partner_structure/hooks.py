# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import _, tools

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Load mandatory datas used in python files before loading the module"""
    _logger.info(_("Loading partner_structure data..."))

    tools.convert_file(
        cr,
        "partner_structure",
        "data/res_partner_category.xml",
        None,
        mode="init",
        noupdate=True,
        kind="init",
        report=None,
    )
