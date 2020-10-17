# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    lead_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        related="partner_id.related_partner_ids",
        string="Lead Partners",
        readonly=False,
    )
    lead_event_ids = fields.One2many(
        "event.event",
        "lead_id",
        string="Events",
        context={
            "state": "confirm",
            "company_id": lambda self: self.env.user.company_id,
        },
    )
    event_count = fields.Integer(compute="_compute_event_count")

    # Relate Lead Tags, Description and Addres to Customer's
    partner_tag_ids = fields.Many2many(
        "res.partner.category",
        related="partner_id.category_id",
        string="Customer's Tags",
    )
    partner_description = fields.Text(
        "Customer's Notes", related="partner_id.comment", readonly=False
    )

    # Fields to display in Opportunities kanban view
    country_code = fields.Char(
        string="Country Code", related="partner_id.country_id.code", store=True
    )
    struct_short_date = fields.Char(related="partner_id.struct_short_date")

    # Special Show Structure fields related fields
    # with Customer's Show Strucure fields
    is_structure = fields.Boolean(
        string="The Contact is a Show Structure",
        related="partner_id.is_structure",
        store=True,
        default="False",
    )
    partner_type = fields.Selection(
        string="Structure Type", related="partner_id.partner_type", store=True
    )
    structure_capacity = fields.Selection(
        string="Expected Audience",
        related="partner_id.structure_capacity",
        readonly=False,
        store=True,
        help="Average audience expected in this venue or festival",
    )

    struct_date_begin = fields.Date(
        related="partner_id.struct_date_begin", store=True, readonly=False,
    )
    struct_date_end = fields.Date(
        related="partner_id.struct_date_end", store=True, readonly=False,
    )
    struct_updated_date = fields.Date(
        related="partner_id.struct_updated_date", store=True,
    )

    @api.depends("lead_event_ids")
    def _compute_event_count(self):
        """Number of events related to the lead"""
        for lead in self:
            lead.event_count = self.env["event.event"].search_count(
                [("lead_id", "=", lead.id), ("date_end", ">", fields.Datetime.now())]
            )

    @api.onchange("partner_id")
    def on_change_customer(self):
        """Fill the Lead's name with Customer's name when selecting the Customer"""
        self.ensure_one()
        self.name = self.partner_id.name

    @api.onchange("struct_date_begin")
    def onchange_date_begin(self):
        """Pre-fill struct_date_end with struct_date_begin
        if no struct_date_end"""
        self.ensure_one()
        if not self.struct_date_end:
            self.struct_date_end = self.struct_date_begin

    def action_add_new_related_event(self):
        """Button's action to add a new Event to lead_event_ids"""
        self.ensure_one()

        xml_id = "event.action_event_view"
        action = self.env.ref(xml_id).read()[0]
        form = self.env.ref("event.view_event_form")
        action["views"] = [(form.id, "form")]
        action["target"] = "new"
        action["context"] = {
            "default_lead_id": self.id,
            "default_name": self.name,
            "default_address_id": self.partner_id.id,
            "default_date_begin": self.struct_date_begin,
            "default_date_end": self.struct_date_end,
        }

        return action

    def action_lead_to_new_opportunity(self):
        """Override the 'lead2opportunity.partner' wizard.
        Force the creation of a new opportunity."""
        self.ensure_one()
        self.convert_opportunity(self.partner_id.id, [self.user_id.id], self.team_id.id)

        return self.redirect_opportunity_view()

    # ---------------------------------------------------------------------
    # Link with related Events
    # ---------------------------------------------------------------------

    def action_set_lost(self):
        """Archive related Events when lost"""
        res = super().action_set_lost()
        for lead in self:
            for event in lead.lead_event_ids:
                event.write({"active": False})
        return res

    def toggle_active(self):
        """Active related Events when restore"""
        res = super().toggle_active()
        for lead in self:
            for event in self.env["event.event"].search([("active", "=", False)]):
                if event.lead_id.id == lead.id:
                    event.write({"active": True})
        return res

    # ---------------------------------------------------------------------
    # MAP button methods
    # ---------------------------------------------------------------------

    def open_map(self):
        """Use open_map method from module 'partner_external_map' """
        self.ensure_one()
        partner = self.partner_id
        return partner.open_map()
