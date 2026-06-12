from odoo import fields, models


class PrivacyActivity(models.Model):
    _inherit = "privacy.activity"

    show_in_skills_networking = fields.Boolean(
        string="Show in skills networking",
        default=False,
        readonly=False,
        help="If enabled, this privacy permission controls whether the user's "
        "profile information is shown on the skills networking page.",
    )
