# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from pytz import country_timezones

from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    lead_id = fields.Many2one("crm.lead", ondelete="cascade", string="Opportunity")

    lead_type = fields.Selection(
        string="Opportunity's Type", related="lead_id.type", readonly="True"
    )

    stage_id = fields.Many2one(
        "crm.stage",
        string="Opportunity's Stage",
        ondelete="restrict",
        index=True,
        copy=False,
        related="lead_id.stage_id",
        store=True,
        readonly="True",
    )

    team_id = fields.Many2one(
        "crm.team", string="Sales Team", oldname="section_id", related="lead_id.team_id"
    )

    company_id = fields.Many2one(
        "res.company",
        string="Band",
        index=True,
        default=lambda self: self.env.user.company_id.id,
    )

    company_currency = fields.Many2one(
        string="Currency",
        related="company_id.currency_id",
        readonly=True,
        relation="res.currency",
    )

    planned_revenue = fields.Monetary(
        string="Expected Revenue",
        currency_field="company_currency",
        readonly=True,
        related="lead_id.planned_revenue",
    )

    is_structure = fields.Boolean(
        string="The Event Address is a Show Structure",
        related="address_id.is_structure",
        default="False",
    )

    structure_capacity = fields.Selection(
        related="address_id.structure_capacity", readonly=True, store=True,
    )

    event_link = fields.Char(
        "Event link",
        index=True,
        help="Facebook event or other web link to the event details",
    )

    partner_tag_ids = fields.Many2many(
        "res.partner.category", related="lead_id.partner_tag_ids", string="Tags"
    )

    city = fields.Char("City", related="address_id.city", store=True, readonly=True)

    subtitle = fields.Char(
        "Event Subtitle", compute="_compute_event_subtitle", store=True
    )

    @api.depends("stage_id", "city")
    def _compute_event_subtitle(self):
        for event in self:
            city = event.city or ""
            stage = event.stage_id.name or ""
            if city and stage:
                event.subtitle = str(city) + " - " + str(stage)
            elif city and not stage:
                event.subtitle = str(city)
            else:
                event.subtitle = str(stage)

    @api.onchange("lead_id")
    def onchange_lead_id(self):
        """Change the event's company to related lead's company"""
        for event in self:
            if event.lead_id:
                event.company_id = event.lead_id.company_id

    @api.onchange("date_begin")
    def onchange_date_begin(self):
        """Pre-fill date_end with date_begin if no date_end"""
        self.ensure_one()
        if not self.date_end:
            self.date_end = self.date_begin

    @api.onchange("address_id")
    def onchange_address_id(self):
        """Define event Timezone from the event address country if existing"""
        for event in self:
            if event.address_id and event.address_id.country_id:
                event.date_tz = country_timezones(event.address_id.country_id.code)[0]

    def open_map(self):
        """Use open_map method from module 'partner_external_map' """
        self.ensure_one()
        partner = self.address_id
        return partner.open_map()
