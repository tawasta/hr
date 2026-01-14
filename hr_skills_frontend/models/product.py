from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    skills_portal_days = fields.Integer(
        string="Skills Duration (days)",
        default=0,
        help="Days granted by this attribute value (e.g. 7, 30, 90, 180).",
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    skills_portal_grant = fields.Boolean(
        string="Grants Skills Portal Access",
        default=False,
        help="If enabled, purchasing this variant grants timed access to /all/skills.",
    )

    skills_portal_days = fields.Integer(
        string="Skills Access Duration (days)",
        compute="_compute_skills_days",
        store=True,
        help="Computed from the variant's attribute values (product.attribute.value.skills_portal_days).",
    )

    @api.depends(
        "skills_portal_grant",
        "product_template_attribute_value_ids",
        "product_template_attribute_value_ids.product_attribute_value_id",
        "product_template_attribute_value_ids.product_attribute_value_id.skills_portal_days",
    )
    def _compute_skills_days(self):
        """
        product.product.product_template_attribute_value_ids = PTAV records
        PTAV.product_attribute_value_id = PAV record where skills_portal_days lives
        """
        for p in self:
            if not p.skills_portal_grant:
                p.skills_portal_days = 0
                continue

            p.skills_portal_days = sum(
                p.product_template_attribute_value_ids.mapped(
                    "product_attribute_value_id.skills_portal_days"
                )
            )
