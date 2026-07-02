from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    talenom_company_code = fields.Char(
        help="Numeric code assigned by Talenom to this company. Used as "
        "the prefix of generated Talenom CSV export filenames.",
    )
