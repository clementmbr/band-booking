# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

# TODO : Allow to define this parameters in Partner's Configuration
STRUCTURE_TYPE = [('festival', 'Festival'), ('venue', 'Venue')]
STRUCTURE_CAPACITY = [('inf1k', '< 1000'), ('sup1k', '> 1000'),
                 ('sup5k', '> 5k'), ('sup10k', '> 10k'),
                 ('sup30k', '> 30k'), ('sup100k', '> 100k')]


class Partner(models.Model):
    """
    """
    _inherit = "res.partner"

    def _get_structure_type(self):
        return STRUCTURE_TYPE

    def _get_structure_tags(self):
        return [t[0] for t in STRUCTURE_TYPE]

    def _get_structure_capacity(self):
        return STRUCTURE_CAPACITY

    is_structure = fields.Boolean(
        'Is a Festival or a Venue ?',
        store=True)

    # TODO (in v13) : Join structure_type and company_type with 'addselection'
    # Not possible before v13 because of the confusion between native _compute_company_type
    # and current onchange functions.
    structure_type = fields.Selection(string='Structure Type',
                                      selection=_get_structure_type,
                                      default=False,
                                      store=True)

    structure_capacity = fields.Selection(_get_structure_capacity,
                                     string='Structure Capacity',
                                     help="Average audience expected in this venue or festival")

    show_period_date_begin = fields.Date(string='Beginning Show Period')
    show_period_date_end = fields.Date(string='Ending Show Period')

    related_structure_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Related Structure',
        relation='rel_struct_partner',
        column1='related_partner_id',
        column2='related_structure_id',
        store=True,
    )
    related_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Related Contacts',
        relation='rel_struct_partner',
        column1='related_structure_id',
        column2='related_partner_id',
    )

    display_related_structure_names = fields.Char("Related Structures",
        compute='_compute_display_related_structure_names', store=True, index=True)

    facebook = fields.Char(help="Must begin by 'http://' to activate URL link")
    instagram = fields.Char(
        help="Must begin by 'http://' to activate URL link")

    # Compute lower stage_id for creating lead from partner
    lower_stage_id = fields.Many2one(
        'crm.stage', 'Lower Lead Stage', compute='_compute_lower_stage_id')

    # Compute leads number related to partner
    lead_count = fields.Integer("Leads", compute='_compute_lead_count')

    # Qualified ?
    is_qualified = fields.Boolean(string="Qualified", default=False)

    # Sequence integer to handle partner order in m2m tree views
    sequence = fields.Integer()

    @api.multi
    def toogle_qualified(self):
        for partner in self:
            partner.is_qualified = not partner.is_qualified

    @api.multi
    @api.depends('related_structure_ids')
    def _compute_display_related_structure_names(self):
        for partner in self:
            for structure in partner.related_structure_ids:
                if not partner.display_related_structure_names:
                    partner.display_related_structure_names = str(
                        structure.name)
                else:
                    partner.display_related_structure_names += ", " + \
                        str(structure.name)

    @api.multi
    def _compute_lower_stage_id(self):
        """Find the Lead's stage_id with the lower sequence to create
        a lead from partner with this default stage"""
        stages = self.env['crm.stage'].search([])
        dict_sequences = {}
        for stage in stages:
            dict_sequences.setdefault(stage.id, stage.sequence)
        self.lower_stage_id = self.env['crm.stage'].browse(
            [min(dict_sequences, key=dict_sequences.get)])

    # ---------------------------------------------------------------------
    # Onchange Relations between category_id, structure_type and company_type
    # ---------------------------------------------------------------------
    @api.onchange('category_id')
    def onchange_category_id(self):
        """Set structure_type dependind on Partner's tags"""
        structure_tags = self._get_structure_tags()

        for partner in self:
            partner_tags = [category.name for category in self.category_id]

            if not partner_tags:
                partner.structure_type = False
                partner.is_structure = False
            else:
                # Update structure_type if it exists a partner_tag in the structure_tags
                ptag_in_stags = [
                    tag for tag in partner_tags if tag in structure_tags]
                if len(ptag_in_stags) > 1:
                    # If there is already a structure tag, delete the old one
                    # and match structure_type with the other one
                    old_stag_id = self.env['res.partner.category'].search(
                        [('name', '=', '%s' % ptag_in_stags[0])])
                    partner.category_id = [(3, old_stag_id.id, 0)]
                    partner.structure_type = ptag_in_stags[1]
                    partner.is_structure = True
                    partner.company_type = 'company'
                elif len(ptag_in_stags) == 1:
                    partner.structure_type = ptag_in_stags[0]
                    partner.is_structure = True
                    partner.company_type = 'company'
                else:
                    partner.structure_type = False
                    partner.is_structure = False
                    partner.company_type = 'company'

    @api.onchange('structure_type')
    def onchange_structure_type(self):
        """Set related structure tag (i.e. the tag with the same name as structure_type's)"""
        self.ensure_one()
        # Remove current structure tags
        for structure_tag in self._get_structure_tags():
            structure_tag_id = self.env['res.partner.category'].search(
                [('name', '=', '%s' % structure_tag)])
            self.category_id = [(3, structure_tag_id.id, 0)]

        if self.structure_type:
            self.is_structure = True
            self.company_type = 'company'
            structure_tag_id = self.env['res.partner.category'].search(
                [('name', '=', '%s' % self.structure_type)])
            if structure_tag_id:
                # Add selected structure_type tag
                self.category_id |= structure_tag_id  # Call onchange_category_id
            else:
                # Or create Structure tag if not existing
                self.category_id |= self.env['res.partner.category'].create(
                    [{'name': self.structure_type,
                      'color': 2,
                      }])

    @api.onchange('company_type')
    def onchange_company_type(self):
        for partner in self:
            if partner.company_type == 'person':
                partner.structure_type = False
                partner.is_structure = False

    # ---------------------------------------------------------------------
    # Button to link (or create) leads from partner
    # ---------------------------------------------------------------------
    @api.multi
    def _compute_opportunity_count(self):
        """Override method do display a linked opportunity in partners related
        to a Structure with opportunity"""
        res = super(Partner, self)._compute_opportunity_count()
        for partner in self:
            if partner.is_structure:
                partner.opportunity_count = self.env['crm.lead'].search_count(
                    [('partner_id', '=', partner.id), ('type', '=', 'opportunity')])
            else:
                partner.opportunity_count = self.env['crm.lead'].search_count(
                    [('partner_id', 'in', partner.related_structure_ids.ids), ('type', '=', 'opportunity')])

        return res

    @api.multi
    def _compute_lead_count(self):
        """Identical method for counting related Leads"""
        for partner in self:
            if partner.is_structure:
                partner.lead_count = self.env['crm.lead'].search_count(
                    [('partner_id', '=', partner.id), ('type', '=', 'lead')])
            else:
                partner.lead_count = self.env['crm.lead'].search_count(
                    [('partner_id', 'in', partner.related_structure_ids.ids), ('type', '=', 'lead')])

    @api.multi
    def action_lead_from_partner(self):
        """Button's action to create a lead from a Structure partner"""
        self.ensure_one()

        xml_id = 'crm.crm_lead_all_leads'
        action = self.env.ref(xml_id).read()[0]
        form = self.env.ref(
            'crm.crm_case_form_view_leads')
        action['views'] = [(form.id, 'form')]
        action['context'] = {'default_partner_id': self.id,
                             'default_stage_id': self.lower_stage_id.id}

        return action

    @api.multi
    def action_related_lead(self):
        """Display related Leads from Partner's smart button"""
        self.ensure_one()

        act_window_xml_id = 'crm.crm_lead_all_leads'
        act_window = self.env.ref(act_window_xml_id).read()[0]

        if self.is_structure:
            domain = [('partner_id', '=', self.id)]
        else:
            domain = [('partner_id', 'in', self.related_structure_ids.ids)]

        act_window['domain'] = domain
        if self.lead_count == 1:
            form = self.env.ref('crm.crm_case_form_view_leads')
            act_window['views'] = [(form.id, 'form')]
            act_window['res_id'] = self.env['crm.lead'].search(domain).id

        return act_window

    @api.multi
    def action_related_opportunity(self):
        """Display related opportunities from Partner's smart button"""
        self.ensure_one()

        act_window_xml_id = 'crm.crm_lead_opportunities'
        act_window = self.env.ref(act_window_xml_id).read()[0]

        if self.is_structure:
            domain = [('partner_id', '=', self.id)]
        else:
            domain = [('partner_id', 'in', self.related_structure_ids.ids)]

        act_window['domain'] = domain
        if self.opportunity_count == 1:
            form = self.env.ref('crm.crm_case_form_view_oppor')
            act_window['views'] = [(form.id, 'form')]
            act_window['res_id'] = self.env['crm.lead'].search(domain).id

        return act_window

    # ---------------------------------------------------------------------
    # Add related_structure button
    # ---------------------------------------------------------------------

    # vvvvv TODO - WORK IN PROGRESS vvvvvvv
    # @api.multi
    # def action_add_related_partner(self):
    #     """Button's action to add a new Partner to Many2many related_partner_ids
    #     in Structure field"""
    #     self.ensure_one()
    #
    #     xml_id = 'crm_booking.action_contacts'
    #     action = self.env.ref(xml_id).read()[0]
    #     # form = self.env.ref('crm_booking.view_partner_tree_contacts')
    #     # action['views'] = [(form.id, 'form')]
    #     action['target'] = 'new'
    #     # action['context'] = {'default_related_structure_ids' : self.}
    #
    #     return action

    # ---------------------------------------------------------------------
    # Relation between Structure and non-Structure partners
    # ---------------------------------------------------------------------
    def propagate_related_struct(self):
        for partner in self:
            for child in partner.child_ids:
                if child.related_structure_ids != partner.related_structure_ids:
                    child.related_structure_ids = partner.related_structure_ids

            for parent in partner.parent_id:
                if parent.related_structure_ids != partner.related_structure_ids:
                    parent.related_structure_ids = partner.related_structure_ids

    @api.multi
    def write(self, values):
        """ Propagate the partner's related structures from parent to childs"""
        res = super().write(values)

        if self.is_structure == True:
            for partner in self.related_partner_ids:
                partner.propagate_related_struct()
        else:
            self.propagate_related_struct()

        return res

    # ---------------------------------------------------------------------
    # Show period festival fields
    # ---------------------------------------------------------------------
    @api.one
    @api.constrains('show_period_date_begin', 'show_period_date_end')
    def _check_closing_date(self):
        if self.show_period_date_end and self.show_period_date_begin:
            if self.show_period_date_end < self.show_period_date_begin:
                raise ValidationError('The ending date cannot be earlier\
                    than the beginning date.')

    @api.onchange('show_period_date_begin')
    def onchange_date_begin(self):
        """Pre-fill show_period_date_end with show_period_date_begin
        if no show_period_date_end"""
        self.ensure_one()
        if not self.show_period_date_end:
            self.show_period_date_end = self.show_period_date_begin
