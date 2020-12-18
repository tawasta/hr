from datetime import datetime
from datetime import timedelta

from odoo import fields
from odoo import models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


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

    def _compute_user_task_hours(self):
        for record in self:
            active_tasks = record.user_task_ids.filtered(lambda r: not r.closed)
            today = datetime.today()
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

            # Current week
            current_tasks = active_tasks.filtered(
                lambda r: r.date_deadline and datetime.strptime(r.date_deadline, DEFAULT_SERVER_DATE_FORMAT) < week_end
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

            if record.calendar_id:
                start = datetime.combine(week_start, datetime.min.time())
                end = datetime.combine(week_end, datetime.max.time())

                record.employee_hours_current_week = record.get_work_days_data(
                    start, end, True, record.calendar_id
                )["hours"]

                if record.user_task_planned_hours_current_week:
                    record.employee_utilization_current_week = (
                        record.user_task_planned_hours_current_week
                        / record.employee_hours_current_week
                        * 100
                    )

