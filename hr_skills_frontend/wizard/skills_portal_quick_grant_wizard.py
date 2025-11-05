from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrSkillsPortalQuickGrantWizard(models.TransientModel):
    _name = "hr.skills.portal.quick.grant.wizard"
    _description = "Quickly grant timed access to /all/skills"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.context.get("active_id"),
        help="User to whom timed access to /all/skills is granted.",
    )
    days = fields.Integer(default=30, string="Duration (days)", required=True)
    start_now = fields.Boolean(default=True, string="Start now")
    date_start = fields.Datetime(string="Start at")

    @api.onchange("start_now")
    def _onchange_start_now(self):
        if self.start_now:
            self.date_start = fields.Datetime.now()

    def action_grant(self):
        self.ensure_one()
        if self.days <= 0:
            raise UserError(_("Duration (days) must be greater than zero."))

        start = (
            fields.Datetime.now()
            if (self.start_now or not self.date_start)
            else self.date_start
        )
        end = fields.Datetime.add(start, days=self.days)

        self.env["hr.skills.portal.access"].sudo().create(
            {
                "user_id": self.user_id.id,
                "date_start": start,
                "date_end": end,
                "active": True,
            }
        )
        return {"type": "ir.actions.act_window_close"}
