# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields


class EventEvent(models.Model):
    _inherit = 'event.event'

    lead_id = fields.Many2one('crm.lead',
                              ondelete='cascade', string="Opportunity")

    lead_type = fields.Selection(
        string="Opportunity's Type", related='lead_id.type', readonly='True')

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

    event_link = fields.Char(
        'Event link', index=True, help="Facebook event or other web link to the event details")

    tag_ids = fields.Many2many(
        'res.partner.category', related='lead_id.tag_ids', string='Tags')  # TODO : store=True impossible...

    city = fields.Char('City', related='address_id.city',
                       store=True, readonly=True)

    subtitle = fields.Char(
        'Event Subtitle', compute='_compute_event_subtitle', store=True)

    @api.multi
    @api.depends('stage_id', 'city')
    def _compute_event_subtitle(self):
        for event in self:
            city = event.city or ''
            stage = event.stage_id.name or ''
            if city and stage:
                event.subtitle = str(city) + " - " + str(stage)
            elif city and not stage:
                event.subtitle = str(city)
            else:
                event.subtitle = str(stage)

    @api.onchange('date_begin')
    def onchange_date_begin(self):
        """Pre-fill date_end with date_begin if no date_end"""
        self.ensure_one()
        if not self.date_end:
            self.date_end = self.date_begin

    # ---------------------------------------------------------------------
    # MAP button methods
    # ---------------------------------------------------------------------
    @api.multi
    def _address_as_string(self):
        """Necessary method to 'open_map' action"""
        self.ensure_one()
        address = self.address_id
        addr = []
        if address.street:
            addr.append(self.street)
        if address.street2:
            addr.append(self.street2)
        if address.city:
            addr.append(self.city)
        if address.state_id:
            addr.append(self.state_id.name)
        if address.country_id:
            addr.append(self.country_id.name)
        if not addr:
            raise UserError(
                _("Address missing on partner '%s'.") % address.name)
        return ' '.join(addr)

    @api.model
    def _prepare_url(self, url, replace):
        """Necessary method to 'open_map' action"""
        assert url, 'Missing URL'
        for key, value in replace.items():
            if not isinstance(value, str):
                # for latitude and longitude which are floats
                value = str(value)
            url = url.replace(key, value)
        logger.debug('Final URL: %s', url)
        return url

    @api.multi
    def open_map(self):
        """Copy action from module 'partner_external_map' to link Opportunities
        address to an external map site"""
        self.ensure_one()
        address = self.address_id
        map_website = self.env.user.context_map_website_id
        if not map_website:
            raise UserError(
                _('Missing map provider: '
                  'you should set it in your preferences.'))
        if (map_website.lat_lon_url and hasattr(address, 'partner_latitude') and
                address.partner_latitude and address.partner_longitude):
            url = address._prepare_url(
                map_website.lat_lon_url, {
                    '{LATITUDE}': address.partner_latitude,
                    '{LONGITUDE}': address.partner_longitude})
        else:
            if not map_website.address_url:
                raise UserError(
                    _("Missing parameter 'URL that uses the address' "
                      "for map website '%s'.") % map_website.name)
            url = address._prepare_url(
                map_website.address_url,
                {'{ADDRESS}': address._address_as_string()})
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
    # ---------------------------------------------------------------------
