# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import _

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(_("Migrating data from 12.0.0.0.1 to 12.0.2.0.0..."))
    categ_model = env["res.partner.category"]

    # Change partner_type old tags for new partner_type tags in partner
    changed_rel_xml_ids = [
        ("partner_structure.festival_tag", "partner_category_type.festival_tag"),
        ("partner_structure.venue_tag", "partner_category_type.venue_tag"),
        ("partner_structure.partner_tag", "partner_category_type.contact_tag"),
    ]
    for change_rel in changed_rel_xml_ids:
        old_tag_id = env.ref(change_rel[0])
        new_tag_id = env.ref(change_rel[1])

        partner_ids = env["res.partner"].search([("category_id", "in", old_tag_id.id)])
        partner_ids.write({"category_id": [(2, old_tag_id.id), (4, new_tag_id.id)]})

    # Update res.partner.category objects
    tag_ids = categ_model.search([])
    for tag_id in tag_ids:
        xml_id = tag_id.get_xml_id()[tag_id.id]
        if xml_id in [rel[0] for rel in changed_rel_xml_ids]:
            tag_id.unlink()
        else:
            if tag_id.name in ["contact", "follower", "influencer"]:
                category_type = "contact"
            else:
                category_type = "structure"

            tag_id.write({"category_type": category_type})

    # Add contact tag for partners who didn't have partner_tag
    struct_tag_ids = categ_model.search([("category_type", "=", "structure")])
    contact_tag_id = env.ref("partner_category_type.contact_tag")

    contact_ids = env["res.partner"].search(
        [("category_id", "not in", struct_tag_ids.ids)]
    )
    contact_ids.write({"category_id": [(4, contact_tag_id.id)]})

    # Rename 'structure_type' field in res.partner
    openupgrade.rename_fields(
        env, [("res.partner", "res_partner", "structure_type", "partner_type",)]
    )
