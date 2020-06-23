# © 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import ast

from odoo import _, api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    facebook = fields.Char(help="Must begin by 'http://' to activate URL link")
    instagram = fields.Char(help="Must begin by 'http://' to activate URL link")

    display_phone = fields.Char("Phone/Mobile", compute="_compute_display_phone")

    # Confirmed partner ?
    is_confirmed = fields.Boolean(string="Confirmed", default=False)

    # Compute lower stage_id for creating lead from partner
    lower_stage_id = fields.Many2one(
        "crm.stage", "Lower Lead Stage", compute="_compute_lower_stage_id"
    )

    # Compute leads number related to partner
    lead_count = fields.Integer("Leads", compute="_compute_lead_count")
    opp_done_count = fields.Integer("Done", compute="_compute_opp_done_count")
    opp_lost_count = fields.Integer("Lost", compute="_compute_opp_lost_count")

    @api.depends("mobile", "phone")
    def _compute_display_phone(self):
        for partner in self:
            partner.display_phone = partner.mobile or partner.phone

    def toogle_confirmed(self):
        for partner in self:
            partner.is_confirmed = not partner.is_confirmed

    # ---------------------------------------------------------------------
    # Button to link (or create) leads from Structure
    # ---------------------------------------------------------------------

    def _compute_lower_stage_id(self):
        """Find the Lead's stage_id with the lower sequence to create
        a lead from partner with this default stage"""
        stages = self.env["crm.stage"].search([])
        dict_sequences = {}
        for stage in stages:
            dict_sequences.setdefault(stage.id, stage.sequence)
        self.lower_stage_id = self.env["crm.stage"].browse(
            [min(dict_sequences, key=dict_sequences.get)]
        )

    def _compute_opportunity_count(self):
        """Override method do display a linked opportunity in partners related
        to a Structure with opportunity"""
        res = super(Partner, self)._compute_opportunity_count()
        for partner in self:
            if partner.is_structure:
                partner.opportunity_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "=", partner.id),
                        ("type", "=", "opportunity"),
                        ("stage_id", "!=", self.env.ref("band_booking.stage_done").id,),
                    ]
                )
            else:
                partner.opportunity_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "in", partner.related_structure_ids.ids),
                        ("type", "=", "opportunity"),
                        ("stage_id", "!=", self.env.ref("band_booking.stage_done").id,),
                    ]
                )

        return res

    def _compute_lead_count(self):
        """Identical method for counting related Leads"""
        for partner in self:
            if partner.is_structure:
                partner.lead_count = self.env["crm.lead"].search_count(
                    [("partner_id", "=", partner.id), ("type", "=", "lead")]
                )
            else:
                partner.lead_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "in", partner.related_structure_ids.ids),
                        ("type", "=", "lead"),
                    ]
                )

    def _compute_opp_done_count(self):
        """Count how many opportunities are in Stage which name is "Done" """
        for partner in self:
            if partner.is_structure:
                partner.opp_done_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "=", partner.id),
                        ("stage_id", "=", self.env.ref("band_booking.stage_done").id,),
                    ]
                )
            else:
                partner.opp_done_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "in", partner.related_structure_ids.ids),
                        ("stage_id", "=", self.env.ref("band_booking.stage_done").id,),
                    ]
                )

    def _compute_opp_lost_count(self):
        """Count how many opportunities were Lost (i.e. inactives with
        a null probability)"""
        for partner in self:
            if partner.is_structure:
                partner.opp_lost_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "=", partner.id),
                        ("probability", "=", 0),
                        ("active", "=", False),
                    ]
                )
            else:
                partner.opp_lost_count = self.env["crm.lead"].search_count(
                    [
                        ("partner_id", "in", partner.related_structure_ids.ids),
                        ("probability", "=", 0),
                        ("active", "=", False),
                    ]
                )

    def action_lead_from_partner(self):
        """Button's action to create a lead from a Structure partner"""
        self.ensure_one()

        xml_id = "crm.crm_lead_all_leads"
        action = self.env.ref(xml_id).read()[0]
        form = self.env.ref("crm.crm_case_form_view_leads")
        action["views"] = [(form.id, "form")]
        action["context"] = {
            "default_partner_id": self.id,
            "default_stage_id": self.lower_stage_id.id,
            "default_type": "lead",
        }

        return action

    def action_related_lead(self):
        """Display related Leads from Partner's smart button"""
        self.ensure_one()

        act_window_xml_id = "crm.crm_lead_all_leads"
        act_window = self.env.ref(act_window_xml_id).read()[0]

        if self.is_structure:
            domain = [("partner_id", "=", self.id), ("type", "=", "lead")]
        else:
            domain = [
                ("partner_id", "in", self.related_structure_ids.ids),
                ("type", "=", "lead"),
            ]

        act_window["domain"] = domain
        if self.lead_count == 1:
            form = self.env.ref("crm.crm_case_form_view_leads")
            act_window["views"] = [(form.id, "form")]
            act_window["res_id"] = self.env["crm.lead"].search(domain).id

        return act_window

    def action_related_opportunity(self):
        """Display related opportunities from Partner's smart button"""
        self.ensure_one()

        act_window_xml_id = "crm.crm_lead_opportunities"
        act_window = self.env.ref(act_window_xml_id).read()[0]

        if self.is_structure:
            domain = [
                ("partner_id", "=", self.id),
                ("stage_id", "!=", self.env.ref("band_booking.stage_done").id),
                ("type", "=", "opportunity"),
            ]
        else:
            domain = [
                ("partner_id", "in", self.related_structure_ids.ids),
                ("stage_id", "!=", self.env.ref("band_booking.stage_done").id),
                ("type", "=", "opportunity"),
            ]

        act_window["domain"] = domain
        if self.opportunity_count == 1:
            form = self.env.ref("crm.crm_case_form_view_oppor")
            act_window["views"] = [(form.id, "form")]
            act_window["res_id"] = self.env["crm.lead"].search(domain).id

        return act_window

    def action_done_opportunity(self):
        """Display Done opportunities from Partner's smart button"""
        self.ensure_one()

        act_window_xml_id = "crm.crm_lead_opportunities"
        act_window = self.env.ref(act_window_xml_id).read()[0]

        if self.is_structure:
            domain = [
                ("partner_id", "=", self.id),
                ("stage_id", "=", self.env.ref("band_booking.stage_done").id),
            ]
        else:
            domain = [
                ("partner_id", "in", self.related_structure_ids.ids),
                ("stage_id", "=", self.env.ref("band_booking.stage_done").id),
            ]

        act_window["domain"] = domain
        if self.opp_done_count == 1:
            form = self.env.ref("crm.crm_case_form_view_oppor")
            act_window["views"] = [(form.id, "form")]
            act_window["res_id"] = self.env["crm.lead"].search(domain).id

        return act_window

    def action_lost_opportunity(self):
        """Display Lost opportunities from Partner's smart button"""
        self.ensure_one()

        act_window_xml_id = "crm.crm_lead_opportunities"
        act_window = self.env.ref(act_window_xml_id).read()[0]

        if self.is_structure:
            domain = [
                ("partner_id", "=", self.id),
                ("probability", "=", 0),
                ("active", "=", False),
            ]
        else:
            domain = [
                ("partner_id", "in", self.related_structure_ids.ids),
                ("probability", "=", 0),
                ("active", "=", False),
            ]

        # act_window["context"] = {"search_default_lost": 1}
        act_window["domain"] = domain
        if self.opp_lost_count == 1:
            form = self.env.ref("crm.crm_case_form_view_oppor")
            act_window["views"] = [(form.id, "form")]
            act_window["res_id"] = self.env["crm.lead"].search(domain).id

        return act_window

    # ---------------------------------------------------------------------
    # Catch Facebook and other info throughout core module partner_autocomplete
    # ---------------------------------------------------------------------

    def _build_additional_contact(self, additional_info):
        """Build comment from additional emails and phone numbers"""
        comment = ""
        if len(additional_info.get("email")) > 1:
            comment += _("\n\nEmails :\n") + "\n".join(additional_info["email"][1:])
        if len(additional_info.get("phone_numbers")) > 1:
            comment += _("\n\nPhone numbers :\n") + "\n".join(
                additional_info["phone_numbers"][1:]
            )

        return comment

    @api.model
    def create(self, vals):
        # Catch facebook and additional emails and phone numbers from the
        # module 'partner_autocomplete'
        # TODO : try to catch these additional info by overriding the 'enrich_company()'
        # in module 'partner_autocomplete' instead of overrinding the create in order to
        # fill the facebook and comment fields during the onchange
        if vals.get("additional_info"):
            additional_info = ast.literal_eval(
                vals["additional_info"].replace("false", "False")
            )
            if additional_info.get("facebook"):
                vals["facebook"] = (
                    "http://www.facebook.com/" + additional_info["facebook"]
                )
            vals["comment"] = self._build_additional_contact(additional_info)

        return super().create(vals)
