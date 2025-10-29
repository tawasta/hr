from odoo import api, fields, models
from datetime import date


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Päivämäärät, joista lasketaan vuodet
    consulting_since = fields.Date(string="Consulting since")
    strategy_since = fields.Date(string="Strategy work since")

    # Lasketut vuodet (store=True -> käytettävissä ryhmittelyyn/raportointiin)
    consulting_years = fields.Float(
        string="Consulting experience (years)",
        compute="_compute_years",
        store=True,
        digits=(16, 1),
    )
    strategy_years = fields.Float(
        string="Strategy experience (years)",
        compute="_compute_years",
        store=True,
        digits=(16, 1),
    )

    # Vapaateksti
    bio = fields.Text(string="About me")

    @api.depends("consulting_since", "strategy_since")
    def _compute_years(self):
        today = date.today()

        def yearfrac(d):
            if not d:
                return 0.0
            days = (today - d).days
            return round(days / 365.25, 1)

        for rec in self:
            rec.consulting_years = yearfrac(rec.consulting_since)
            rec.strategy_years = yearfrac(rec.strategy_since)
