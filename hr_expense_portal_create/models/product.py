from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Defines the order of expense products in the portal.",
    )