from datetime import datetime
from datetime import timedelta

from odoo import fields
from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Total hours
    user_task_planned_hours = fields.Float(
        string="Planned hours",
        help="Planned hours on open tasks",
        compute="_compute_user_task_hours",
    )

    user_task_effective_hours = fields.Float(
        string="Effective hours",
        help="Effective hours on open tasks",
        compute="_compute_user_task_hours",
    )

    user_task_remaining_hours = fields.Float(
        string="Remaining hours",
        help="Remaining hours on open tasks",
        compute="_compute_user_task_hours",
    )

    # Weekly hours
    user_task_planned_hours_current_week = fields.Float(
        string="Planned hours, current week",
        help="Current week planned hours on open tasks",
        compute="_compute_user_task_hours",
    )

    user_task_effective_hours_current_week = fields.Float(
        string="Effective hours, current week",
        help="Current week effective hours on open tasks",
        compute="_compute_user_task_hours",
    )

    user_task_remaining_hours_current_week = fields.Float(
        string="Remaining hours, current week",
        help="Current week remaining hours on open tasks",
        compute="_compute_user_task_hours",
    )

    employee_hours_current_week = fields.Float(
        string="Available this week", compute="_compute_user_task_hours",
    )

    employee_utilization_current_week = fields.Float(
        string="Current week utilization %",
        help="Percentage of current week utilization, using given working hours",
        compute="_compute_user_task_hours",
    )

    # Next 30 days hours
    user_task_planned_hours_30_days = fields.Float(
        string="Planned hours, 30 days",
        help="30 days planned hours on open tasks",
        compute="_compute_user_task_hours",
    )

    user_task_effective_hours_30_days = fields.Float(
        string="Effective hours, 30 days",
        help="30 days effective hours on open tasks",
        compute="_compute_user_task_hours",
    )

    user_task_remaining_hours_30_days = fields.Float(
        string="Remaining hours, current week",
        help="30 days remaining hours on open tasks",
        compute="_compute_user_task_hours",
    )

    employee_hours_30_days = fields.Float(
        string="Available next 30 days", compute="_compute_user_task_hours",
    )

    employee_utilization_30_days = fields.Float(
        string="Next 30 days utilization %",
        help="Percentage of next 30 days utilization, using given working hours",
        compute="_compute_user_task_hours",
    )

    def _compute_user_task_hours(self):
        for record in self:
            active_tasks = record.user_task_ids.filtered(lambda r: not r.closed)
            today = fields.Date.today()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)

            # Total hours
            record.user_task_planned_hours = sum(active_tasks.mapped("planned_hours"))
            record.user_task_effective_hours = sum(
                active_tasks.mapped("effective_hours")
            )
            record.user_task_remaining_hours = sum(
                active_tasks.mapped("remaining_hours")
            )

            # 30 days
            planned_tasks = active_tasks.filtered(
                lambda r: r.date_deadline
                and r.date_deadline < today + timedelta(days=30)
            )
            record.user_task_planned_hours_30_days = sum(
                planned_tasks.mapped("planned_hours")
            )
            record.user_task_effective_hours_30_days = sum(
                planned_tasks.mapped("effective_hours")
            )
            record.user_task_remaining_hours_30_days = sum(
                planned_tasks.mapped("remaining_hours")
            )

            # Current week
            current_tasks = planned_tasks.filtered(
                lambda r: r.date_deadline and r.date_deadline < week_end
            )
            record.user_task_planned_hours_current_week = sum(
                current_tasks.mapped("planned_hours")
            )
            record.user_task_effective_hours_current_week = sum(
                current_tasks.mapped("effective_hours")
            )
            record.user_task_remaining_hours_current_week = sum(
                current_tasks.mapped("remaining_hours")
            )

            if record.resource_calendar_id:
                start = datetime.combine(week_start, datetime.min.time())
                end = datetime.combine(week_end, datetime.max.time())

                record.employee_hours_current_week = record.get_work_days_data(
                    start, end, True, record.resource_calendar_id
                )["hours"]

                today = datetime.combine(today, datetime.min.time())
                record.employee_hours_30_days = record.get_work_days_data(
                    today, today + timedelta(days=30), True, record.resource_calendar_id
                )["hours"]

                if record.user_task_planned_hours_current_week:
                    record.employee_utilization_current_week = (
                        record.user_task_planned_hours_current_week
                        / record.employee_hours_current_week
                        * 100
                    )

                if record.user_task_planned_hours_30_days:
                    record.employee_utilization_30_days = (
                        record.user_task_planned_hours_30_days
                        / record.employee_hours_30_days
                        * 100
                    )
