from odoo import api, models, fields
import datetime


class Employee(models.Model):

    _inherit = 'hr.employee'

    # TODO: refactor this to work with resource.calendar

    def get_hours_worked(self, today):
        """
        Fetch all timesheet lines the user has logged between calculation
        start date and today, and get the sum of hours.

        Override this function if there is need for more complex calculation
        that takes into account e.g. public holidays.
        """

        today_str = datetime.datetime.strftime(today, '%Y-%m-%d')

        timesheet_line_ids = self.env['account.analytic.line'].\
            search(args=[('user_id', '=', self.id),
                         ('date', '>=', self.hour_balance_start),
                         ('date', '<=', today_str)])

        hours_worked = sum(
            timesheet_line.unit_amount for timesheet_line in timesheet_line_ids
        )

        return hours_worked

    def get_hours_needed(self, date_to_check, today, daily_hours):
        """
        Iterate through all dates from start date to today. If the date
        is not Saturday or Sunday, increase the hours_needed counter by the
        employee's weekly working hours divided by number of weekly working
        days(=5).

        Override this function if there is need for more complex calculation
        that takes into account e.g. public holidays.
        """

        hours_needed = 0

        while True:
            if date_to_check.weekday() not in [5, 6]:
                hours_needed += daily_hours
            date_to_check += datetime.timedelta(days=1)
            if date_to_check > today:
                break

        return hours_needed

    @api.depends('weekly_working_time', 'hour_balance_start', 'timesheet_ids',
                 'timesheet_ids.timesheet_ids')
    def _compute_hour_balance(self):
        """
        Calculates how many hours the employee has logged from
        hour_balance_start date onwards and compares it to how
        many hours they should have logged according to their
        weekly working hour time. The calculation is redone each
        time a user's timesheet gets updated.

        Don't calculate if required employee info is missing or they do
        not have a fixed weekly working time.
        """
        for record in self:
            if record.weekly_working_time != 'hour_worker' and \
                    record.hour_balance_start:

                date_to_check = datetime.datetime.strptime(str(
                    record.hour_balance_start), "%Y-%m-%d").date()
                today = datetime.datetime.now().date()
                daily_hours = float(record.weekly_working_time) / 5

                hours_worked = record.get_hours_worked(today)
                hours_needed = record.get_hours_needed(
                    date_to_check, today, daily_hours
                )

                record.hour_balance = hours_worked - hours_needed
            else:
                record.hour_balance = 0

    def _compute_show_balance(self):
        for record in self:
            record.show_balance = \
                record.user_id.id == record.env.uid and True or False

    weekly_working_time = fields.Selection(
        [('30', '30'), ('37.5', '37,5'),
         ('hour_worker', 'No fixed working time')], 'Weekly working time (h)',
        default='hour_worker'
    )

    hour_balance_start = fields.Date(
        string='Hour Balance Start Date',
        help=('Date from which onwards the hour balance is calculated. Set '
              'this as the date when the user started filling out timesheets.')
    )

    hour_balance = fields.Float(
        string='Hour Balance',
        compute=_compute_hour_balance,
        store=True
    )

    # Fill the existing m2o relation between employees and timesheets so that
    # it can be used in api.depends
    timesheet_ids = fields.One2many(
        comodel_name='hr_timesheet_sheet.sheet',
        inverse_name='employee_id',
        string='Timesheets'
    )

    # A helper field that is used to restrict that the user can only see their
    # own hour balance in the employee form view
    show_balance = fields.Boolean(
        string='Show Hour Balance',
        compute=_compute_show_balance
    )
