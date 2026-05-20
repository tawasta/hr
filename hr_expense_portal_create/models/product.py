from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sequence = fields.Integer(
        default=10,
        help="Defines the order of expense products in the portal.",
    )
