# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrSkillsPortalAccess(models.Model):
    _name = "hr.skills.portal.access"
    _description = "Portal Skills Timed Access"
    _order = "date_start desc, id desc"
    _rec_name = "user_id"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        index=True,
        ondelete="cascade",
        help="User who may view /all/skills in the given time window.",
    )
    date_start = fields.Datetime(
        required=True,
        default=lambda self: fields.Datetime.now(),
        index=True,
    )
    date_end = fields.Datetime(
        required=True,
        help="Access ends at this timestamp (inclusive).",
        index=True,
    )
    active = fields.Boolean(default=True, index=True)
    notes = fields.Text()

    state = fields.Selection(
        [("future", "Future"), ("active", "Active"), ("expired", "Expired")],
        compute="_compute_state",
        store=False,
    )

    _sql_constraints = [
        ("check_window", "CHECK(date_end > date_start)", "End must be after start."),
    ]

    @api.depends("date_start", "date_end", "active")
    def _compute_state(self):
        now = fields.Datetime.now()
        for rec in self:
            if not rec.active:
                rec.state = "expired"
            elif now < rec.date_start:
                rec.state = "future"
            elif now <= rec.date_end:
                rec.state = "active"
            else:
                rec.state = "expired"

    @api.model
    def user_has_portal_skills_access(self, user):
        """
        Return True if user currently has access to /all/skills.

        - If config parameter 'hr_skills_portal_access.enable' is falsy (missing/'0'),
          access is globally open -> return True.
        - If enabled, require an active grant in the [date_start, date_end] window.
        """
        icp = self.env["ir.config_parameter"].sudo()
        enabled_raw = icp.get_param("hr_skills_portal_access.enable", "0")
        enabled = str(enabled_raw).strip().lower() in ("1", "true", "yes", "on", "y")

        if not enabled:
            return True

        if not user:
            return False
        now = fields.Datetime.now()
        return bool(
            self.sudo().search_count(
                [
                    ("user_id", "=", user.id),
                    ("active", "=", True),
                    ("date_start", "<=", now),
                    ("date_end", ">=", now),
                ]
            )
        )

    @api.model
    def _cron_archive_expired_access(self, batch_size=1000):
        """
        Arkistoi automaattisesti kaikki grantit, joiden date_end on mennyt.
        Ajetaan cronia vasten; käsittelee isoja määriä erissä.
        """
        now = fields.Datetime.now()
        domain = [("active", "=", True), ("date_end", "<", now)]
        while True:
            recs = self.sudo().search(domain, limit=batch_size)
            if not recs:
                break
            recs.write({"active": False})
