# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = 'crm.lead'

    lead_partners = fields.Many2many(comodel_name='res.partner',
                                     related='partner_id.show_related_partner_ids',
                                     string='Lead Partners')
    lead_event_ids = fields.One2many('event.event', 'lead_id',
                                     string='Events', context={'state': 'confirm'})

    # Relate Lead Tags, Description and Addres to Customer's
    tag_ids = fields.Many2many(
        'res.partner.category', related='partner_id.category_id', string='Tags')
    description = fields.Text('Notes', related='partner_id.comment')
    street = fields.Char('Street', related='partner_id.street', store=True)
    street2 = fields.Char('Street2', related='partner_id.street2', store=True)
    zip = fields.Char('Zip', change_default=True,
                      related='partner_id.zip', store=True)
    city = fields.Char('City', related='partner_id.city', store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State', related='partner_id.state_id', store=True)
    country_id = fields.Many2one(
        'res.country', string='Country', related='partner_id.country_id', store=True)
    website = fields.Char(
        'Website', index=True, help="Website of the contact", related='partner_id.website')
    # To display in Opportunities kanban view
    country_code = fields.Char(
        string='Country Code', related='partner_id.country_id.code', store=True)
    short_date = fields.Char(
        string='Short Date', compute='_compute_short_date')

    # Special Show Structure fields related fields
    # with Customer's Show Strucure fields
    is_structure = fields.Boolean(
        string='The Contact is a Show Structure',
        related='partner_id.is_structure',
        store=True,
        default='False')
    structure_type = fields.Selection(string='Structure Type',
                                      related='partner_id.structure_type',
                                      store=True)
    show_capacity = fields.Selection(
        string='Show Capacity',
        related='partner_id.show_capacity',
        readonly=False,
        store=True,
        help="Average audience expected in this venue or festival")

    show_period_date_begin = fields.Date(
        string='Beginning Show Period',
        related='partner_id.show_period_date_begin',
        store=True,
        readonly=False,)
    show_period_date_end = fields.Date(
        string='Ending Show Period',
        related='partner_id.show_period_date_end',
        store=True,
        readonly=False,)
    show_period_all_year = fields.Boolean(
        string='All year long',
        related='partner_id.show_period_all_year',
        readonly=False,
        store=True,
        default='False')

    @api.multi
    @api.depends('show_period_date_begin')
    def _compute_short_date(self):
        for lead in self:
            if lead.show_period_date_begin:
                date = str(lead.show_period_date_begin)
                date_obj = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
                lead.short_date = datetime.strftime(date_obj, '%d' + '/' + '%m')

    @api.onchange('partner_id')
    def on_change_customer(self):
        """Fill the Lead's name with Customer's name when selecting the Customer"""
        self.ensure_one()
        self.name = self.partner_id.name

    @api.onchange('show_period_date_begin')
    def onchange_date_begin(self):
        """Pre-fill show_period_date_end with show_period_date_begin
        if no show_period_date_end"""
        self.ensure_one()
        if not self.show_period_date_end:
            self.show_period_date_end = self.show_period_date_begin

    @api.multi
    def _address_as_string(self):
        """Necessary method to 'open_map' action"""
        self.ensure_one()
        addr = []
        if self.street:
            addr.append(self.street)
        if self.street2:
            addr.append(self.street2)
        if self.city:
            addr.append(self.city)
        if self.state_id:
            addr.append(self.state_id.name)
        if self.country_id:
            addr.append(self.country_id.name)
        if not addr:
            raise UserError(_("Address missing on partner '%s'.") % self.name)
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
        map_website = self.env.user.context_map_website_id
        if not map_website:
            raise UserError(
                _('Missing map provider: '
                  'you should set it in your preferences.'))
        if (map_website.lat_lon_url and hasattr(self, 'partner_latitude') and
                self.partner_latitude and self.partner_longitude):
            url = self._prepare_url(
                map_website.lat_lon_url, {
                    '{LATITUDE}': self.partner_latitude,
                    '{LONGITUDE}': self.partner_longitude})
        else:
            if not map_website.address_url:
                raise UserError(
                    _("Missing parameter 'URL that uses the address' "
                      "for map website '%s'.") % map_website.name)
            url = self._prepare_url(
                map_website.address_url,
                {'{ADDRESS}': self._address_as_string()})
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
