# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo import _, api, fields, models
from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

    def action_expense_from_event(self):
        """Button's action to create a Expense from an Event form"""
        self.ensure_one()

        xml_id = "hr_expense.hr_expense_actions_all"
        action = self.env.ref(xml_id).read()[0]
        form = self.env.ref("hr_expense.hr_expense_view_form")
        action["views"] = [(form.id, "form")]

        # TODO: Check if the event's analytic account exists and create if if not.

        return action
