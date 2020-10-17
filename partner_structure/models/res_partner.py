# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

STRUCTURE_CAPACITY = [
    ("inf1k", "< 1000"),
    ("sup1k", "> 1000"),
    ("sup5k", "> 5k"),
    ("sup10k", "> 10k"),
    ("sup30k", "> 30k"),
    ("sup100k", "> 100k"),
]

# Relation between partner_type value and it's related tag's XML_ID defined in
# "../data/res_partner_category.xml"
RELATION_PARTNER_TYPE_TAG = {
    ("festival", "partner_structure.festival_tag"),
    ("venue", "partner_structure.venue_tag"),
    ("contact", "partner_structure.contact_tag"),
}


class Partner(models.Model):
    """Make the difference between classic Contacts and Structures (i.e. Venues and
    Festivals for the moment).
    Venues and Festivals will be linked to classic 'partners' and will display
    special fields about the Structure.
    """

    _inherit = "res.partner"

    def _get_structure_capacity(self):
        return STRUCTURE_CAPACITY

    is_structure = fields.Boolean(store=True)

    partner_type = fields.Selection(
        selection=[
            ("festival", _("Festival")),
            ("venue", _("Venue")),
            ("contact", _("Contact")),
        ],
        string="Partner Type",
        default="contact",
        required=True,
        store=True,
    )

    structure_capacity = fields.Selection(
        selection=_get_structure_capacity,
        string="Expected Audience",
        help="Average audience expected in this venue or festival",
    )

    struct_date_begin = fields.Date(
        string="Festival Date", help="The date on which the festival is used to start."
    )
    struct_date_end = fields.Date(string="Festival Date End")
    # Short date formated like "DD/MM - DD/MM" for Partner's tree view and
    # Lead's kanban view
    struct_short_date = fields.Char(compute="_compute_struct_short_date")
    # Computed date for "Group by Festival date" and "Order tree views" utilities
    # (= same days and month as `struct_date_begin` but with a computed year to be
    # a date in the future)
    struct_updated_date = fields.Date(
        compute="_compute_struct_updated_date", store=True
    )

    related_structure_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Related Structure",
        relation="rel_struct_partner",
        column1="related_partner_id",
        column2="related_structure_id",
        store=True,
    )
    related_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Related Contacts",
        relation="rel_struct_partner",
        column1="related_structure_id",
        column2="related_partner_id",
    )

    # Used structures names for Contacts tree view
    display_related_structure_names = fields.Char(
        "Related Structures",
        compute="_compute_display_related_structure_names",
        store=True,
        index=True,
    )
    # Used to display Tags in tree views
    display_category_ids = fields.Many2many(
        "res.partner.category",
        string="Tags for tree view",
        compute="_compute_display_category_ids",
    )

    # Sequence integer to handle partner order in m2m tree views
    sequence = fields.Integer()

    @api.depends("struct_date_begin")
    def _compute_struct_updated_date(self):
        """Compute ``struct_updated_date`` to be used in "Group by Festival
        date" and used also to order the Festivals tree view.

        It has the same days and month as ``struct_date_begin`` but with a
        modified year to be a date included in the next 365 days.
        """
        now = datetime.now()
        one_year = relativedelta(years=1)

        for partner in [p for p in self if p.struct_date_begin]:
            date_obj = datetime.strptime(
                str(partner.struct_date_begin), DEFAULT_SERVER_DATE_FORMAT
            )
            while date_obj < now:
                date_obj += one_year
            while date_obj > (now + one_year):
                date_obj -= one_year

            partner.struct_updated_date = (
                datetime.strftime(date_obj, DEFAULT_SERVER_DATE_FORMAT) or ""
            )

    @api.depends("struct_date_begin", "struct_date_end")
    def _compute_struct_short_date(self):
        """Display date in format DD/MM for Festivals tree view and
        CRM kanban view"""
        # TODO : Display MM/DD or DD/MM depending on user language
        for partner in self:
            date_begin = partner.struct_date_begin
            date_end = partner.struct_date_end
            if date_begin:
                date_begin_obj = datetime.strptime(
                    str(date_begin), DEFAULT_SERVER_DATE_FORMAT
                )
                partner.struct_short_date = datetime.strftime(
                    date_begin_obj, "%d" + "/" + "%m"
                )
                if date_end and date_end != date_begin:
                    date_end_obj = datetime.strptime(
                        str(date_end), DEFAULT_SERVER_DATE_FORMAT
                    )
                    short_date_end = datetime.strftime(date_end_obj, "%d" + "/" + "%m")
                    partner.struct_short_date += " - " + short_date_end

    @api.depends("related_structure_ids")
    def _compute_display_related_structure_names(self):
        for partner in self:
            for structure in partner.related_structure_ids:
                if not partner.display_related_structure_names:
                    partner.display_related_structure_names = str(structure.name)
                else:
                    partner.display_related_structure_names += ", " + str(
                        structure.name
                    )

    def _compute_display_category_ids(self):
        """Display tags in tree view except special ones made to distinguish the type
        of Structure or Contact, like 'festival', 'venue' or 'partner' """
        for partner in self:
            partner_type_tags = self.env["res.partner.category"].search(
                [("is_partner_type_categ", "=", True)]
            )
            partner.display_category_ids = partner.category_id - partner_type_tags

    # ---------------------------------------------------------------------
    # Onchange Relations between category_id, partner_type and company_type
    # ---------------------------------------------------------------------

    def _get_partner_type_from_tag(self, tag_id):
        """Returns partner_type from tag_id"""
        if tag_id.is_partner_type_categ:
            for tuplet in RELATION_PARTNER_TYPE_TAG:
                if tuplet[1] == tag_id.get_xml_id()[tag_id.id]:
                    return tuplet[0]

    def _get_tag_from_partner_type(self, partner_type):
        """Returns a tag_id from string partner_type (like "venue" or "contact")"""
        for tuplet in RELATION_PARTNER_TYPE_TAG:
            if tuplet[0] == partner_type:
                return self.env.ref(tuplet[1])

    @api.onchange("category_id")
    def onchange_category_id(self):
        """Set partner_type dependind on Partner's tags"""
        contact_tag_id = self._get_tag_from_partner_type("contact")

        for partner in self:
            if not partner.category_id:
                partner.update(
                    {
                        "partner_type": "contact",
                        "category_id": [(4, contact_tag_id.id, 0)],
                        "is_structure": False,
                    }
                )
            else:
                # Update partner_type depending on the partner_type's tags in the
                # current partner's tags
                struct_tag_ids = partner.category_id.filtered("is_partner_type_categ")

                if len(struct_tag_ids) > 1:
                    # It means that the onchange added a partner_type's tag to another
                    # one already present (e.g. adding 'venue' tag when "festival"
                    # is present).
                    # In this case we delete the old one (i.e. the 1st one of the list)
                    # and match partner_type with the new one (i.e. the 2nd one)
                    old_struct_tag_id = struct_tag_ids[0]
                    new_struct_tag_id = struct_tag_ids[1]
                    new_part_type = self._get_partner_type_from_tag(new_struct_tag_id)

                    partner.update(
                        {
                            "category_id": [(3, old_struct_tag_id.id, 0)],
                            "partner_type": new_part_type,
                            "is_structure": True,
                            "is_company": True,
                        }
                    )
                elif len(struct_tag_ids) == 1:
                    # In this case, there was no partner_type's tag, so we just set
                    # the partner as a (new) structure
                    new_part_type = self._get_partner_type_from_tag(struct_tag_ids[0])
                    is_structure = struct_tag_ids[0].category_type == "structure"

                    partner.update(
                        {"partner_type": new_part_type, "is_structure": is_structure}
                    )
                    if is_structure:
                        partner.update({"is_company": True})
                else:
                    # There cannot be no partner_type's tag. Set to "contact" by default
                    partner.update(
                        {
                            "partner_type": "contact",
                            "category_id": [(4, contact_tag_id.id, 0)],
                            "is_structure": False,
                        }
                    )

    @api.onchange("partner_type")
    def onchange_partner_type(self):
        """Set related structure tag (i.e. the tag with the same name
        as partner_type's)"""
        struct_tag_ids = self.env["res.partner.category"].search(
            [("category_type", "=", "structure")]
        )
        contact_tag_ids = self.env["res.partner.category"].search(
            [("category_type", "=", "contact")]
        )
        c_type_tag_id = self._get_tag_from_partner_type("contact")
        action_categ = []

        for partner in self:
            if partner.partner_type == "contact":
                # Remove all tags related to a structure
                action_categ.extend([(3, stag_id.id, 0) for stag_id in struct_tag_ids])
                # Add contact_type tag
                action_categ.append((4, c_type_tag_id.id, 0))

                partner.update({"is_structure": False, "category_id": action_categ})
            else:
                # Remove all tags related to a structure
                action_categ.extend([(3, ctag_id.id, 0) for ctag_id in contact_tag_ids])
                # Add the good structure type tag
                s_type_tag_id = self._get_tag_from_partner_type(partner.partner_type)
                action_categ.append((4, s_type_tag_id.id, 0))

                partner.update({"is_structure": True, "category_id": action_categ})

    @api.onchange("company_type")
    def onchange_company_type(self):
        for partner in self:
            if partner.company_type == "person":
                partner.update(
                    {
                        "is_company": False,
                        "partner_type": "contact",
                        "is_structure": False,
                    }
                )

    @api.onchange("is_structure")
    def onchange_is_structure(self):
        """Change Tags value and domain when switching from Structure to Contact and
        vice-versa"""
        if len(self) == 1:
            if self.is_structure:
                return {
                    "domain": {"category_id": [("category_type", "=", "structure")]}
                }
            else:
                return {"domain": {"category_id": [("category_type", "=", "contact")]}}

    # ---------------------------------------------------------------------
    # Festival date fields
    # ---------------------------------------------------------------------

    @api.onchange("struct_date_begin")
    def onchange_date_begin(self):
        """Pre-fill struct_date_end with struct_date_begin
        if no struct_date_end"""
        self.ensure_one()
        if not self.struct_date_end:
            self.struct_date_end = self.struct_date_begin

    # ---------------------------------------------------------------------
    # Propagate 'related_structure_ids' to Contact's childs and parents
    # ---------------------------------------------------------------------

    def write(self, vals):
        """Propagate the partner's related structures from parent to childs"""
        # Change the values on self
        res = super().write(vals)
        for partner in self:
            if partner.is_structure:
                for rel_partner in partner.related_partner_ids:
                    # Propagate rel_partner's structures to all its family
                    for p in rel_partner.child_ids | rel_partner.parent_id:
                        if p.related_structure_ids != rel_partner.related_structure_ids:
                            p.related_structure_ids = rel_partner.related_structure_ids

        return res
