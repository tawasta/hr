from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    optional_message_receiver = fields.Boolean(
        string="Reveice submit message",
        default=False,
    )
