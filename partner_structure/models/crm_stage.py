# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class Stage(models.Model):
    _inherit = "crm.stage"

    def unlink(self):
        """Prevent from deleting mandatory 'Done' stage and display a message if
        the deleted stage is still linked to leads."""
        to_unlink = self - self.env.ref("partner_structure.stage_done")
        if len(to_unlink) < len(self):
            raise UserError(
                _(
                    """It is not allowed to delete the 'Done' stage as it is used
                    by the 'partner_structure' module to link Contacts with 'Done'\
                    leads."""
                )
            )

        for stage in to_unlink:
            stage_leads = self.env["crm.lead"].search(
                [
                    ("stage_id", "=", stage.id),
                    "|",
                    ("active", "=", False),
                    ("active", "=", True),
                ]
            )
            if stage_leads:
                raise UserError(
                    _(
                        """The following leads are still related to the stage "{stage}":
                        {stage_leads}

                        Please consider moving these leads before deleting this stage.
                        """.format(
                            stage=stage.name,
                            stage_leads="\n".join(["- " + l.name for l in stage_leads]),
                        )
                    )
                )
        return super(Stage, to_unlink).unlink()
