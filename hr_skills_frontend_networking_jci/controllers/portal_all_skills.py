from odoo.http import request

from odoo.addons.hr_skills_frontend.controllers.skills_portal import HrSkillPortal


class HrSkillPortalNetworking(HrSkillPortal):
    def _get_skills_networking_employee_ids(self):
        activities = (
            request.env["privacy.activity"]
            .sudo()
            .search([("show_in_skills_networking", "=", True)])
        )
        if not activities:
            return []

        consents = (
            request.env["privacy.consent"]
            .sudo()
            .search(
                [
                    ("activity_id", "in", activities.ids),
                    ("accepted", "=", True),
                    ("state", "=", "answered"),
                ]
            )
        )
        if not consents:
            return []

        users = (
            request.env["res.users"]
            .sudo()
            .search([("partner_id", "in", consents.mapped("partner_id").ids)])
        )
        if not users:
            return []

        employees = (
            request.env["hr.employee"].sudo().search([("user_id", "in", users.ids)])
        )
        return employees.ids

    def _prepare_skill_values(self, page, sortby, search, search_in, groupby):
        values = super()._prepare_skill_values(
            page=page,
            sortby=sortby,
            search=search,
            search_in=search_in,
            groupby=groupby,
        )

        allowed_employee_ids = set(self._get_skills_networking_employee_ids())

        filtered_groups = []
        for records in values.get("grouped_records", []):
            filtered_records = records.filtered(
                lambda rec: rec.employee_id.id in allowed_employee_ids
            )
            if filtered_records:
                filtered_groups.append(filtered_records)

        values["grouped_records"] = filtered_groups
        return values
