# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields


class EventEvent(models.Model):
    _inherit = 'event.event'

    lead_id = fields.Many2one('crm.lead',
                              ondelete='cascade', string="Opportunity")

    lead_type = fields.Selection(string="Opportunity's Type",related='lead_id.type', readonly='True')

    stage_id = fields.Many2one(
        'crm.stage', string="Opportunity's Stage",
        ondelete='restrict', index=True, copy=False, related='lead_id.stage_id',
        store=True,
        readonly='True')

    team_id = fields.Many2one(
        'crm.team', string='Sales Team', oldname='section_id', related='lead_id.team_id')

    show_capacity = fields.Selection(
        string='Show Capacity',
        related='lead_id.show_capacity',
        readonly=True,
        store=True,
        help="Average audience expected in this venue or festival")

    tag_ids = fields.Many2many(
        'res.partner.category', related='lead_id.tag_ids', string='Tags') # TODO : store=True impossible...

    city = fields.Char('City', related='address_id.city', store=True, readonly=True)

    subtitle = fields.Char('Event Subtitle', compute='_compute_event_subtitle', store=True)

    @api.multi
    @api.depends('stage_id', 'city')
    def _compute_event_subtitle(self):
        for event in self:
            if event.city:
                event.subtitle = str(event.city) + " - " + str(event.stage_id.name)
            else:
                event.subtitle = str(event.stage_id.name)

    @api.onchange('date_begin')
    def onchange_date_begin(self):
        """Pre-fill date_end with date_begin if no date_end"""
        self.ensure_one()
        if not self.date_end:
            self.date_end = self.date_begin
