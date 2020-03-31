# Copyright 2015 Akretion (http://www.akretion.com).
# @author Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AddRelatedPartner(models.TransientModel):
    _name = "add.related.partner"
    # _inherit = 'res.partner'
    _description = "Wizard to add selected partners to field 'related_partner_ids'"

    partner_ids = fields.Many2many(
        'res.partner',
        string="List of all partner Contacts",
        default=lambda self: self.env['res.partner'].search([('is_structure', '=', False)]),
    )

    selected_partner_ids = fields.Many2many(
        'res.partner',
        string="Selected Contacts",
        domain=['is_structure', '=', False],
    )

    # TODO : Define the button method to add to related_partner_ids the selected partners in the wizard
    @api.multi
    def button_add_selected_partners(self):
        """
        Add selected partners to 'related_partner_ids'
        """
        pass
