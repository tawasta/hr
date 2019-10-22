# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import json


class WebsiteTimesheetController(http.Controller):

    @http.route(
        ['/my/timesheet'],
        type='http',
        auth='user',
        website=True)
    def my_timesheet(self, **post):

        analytic_lines = request.env['account.analytic.line'].search([
            ('user_id', '=', request.env.user.id),
        ], order='create_date DESC', limit=5)

        values = {
            'analytic_lines': analytic_lines,
        }

        return request.render("website_hr_timesheet.timesheet", values)

    @http.route(
        ['/my/timesheet/confirm'],
        type='http',
        auth='user',
        website=True)
    def my_timesheet_confirm(self, **post):

        analytic_line = request.env['account.analytic.line']
        project_task = request.env['project.task']
        task_id = int(post.get('task_id'))
        task = project_task.browse([task_id])

        hours = float(post.get('hours', 0))
        minutes = float(post.get('minutes', 0))
        unit_amount = hours + minutes/60

        line_values = {
            'date': fields.Date.today(),
            'name': post.get('name', ''),
            'user_id': request.env.user.id,
            'task_id': task.id,
            'project_id': task.project_id.id,
            'unit_amount': unit_amount,
        }

        analytic_line.create(line_values)

        return request.redirect("/my/timesheet")

    @http.route(
        ['/task/datalist'],
        type='json',
        auth='user',
        website=True)
    def task_datalist(self, **post):
        search_domain = list()

        if post.get('project_id'):
            search_domain.append(
                ('project_id', '=', int(post.get('project_id')))
            )

        tasks = request.env['project.task'].search(
            search_domain,
        )

        tasks_list = []
        for task in tasks:
            task_name = '%s / %s' % (task.project_id.name, task.name)
            tasks_list.append({'id': task.id, 'name': task_name})

        return json.dumps(tasks_list)
