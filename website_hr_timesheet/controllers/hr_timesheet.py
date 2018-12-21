# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import json


class WebsiteTimesheetController(http.Controller):

    @http.route(
        ['/my/timesheet'],
        type='http',
        auth='public',
        website=True)
    def my_timesheet(self, **post):

        projects = dict()
        tasks = dict()

        values = {
            'projects': projects,
            'tasks': tasks,
        }

        return request.render("website_hr_timesheet.timesheet", values)

    @http.route(
        ['/project/datalist'],
        type='json',
        auth='public',
        website=True)
    def project_datalist(self, **post):
        ProjectProject = request.env['project.project']
        ProjectTask = request.env['project.task']

        search_domain = list()

        projects = ProjectProject.search_read(
            search_domain,
            ['id', 'name'],
        )

        return json.dumps(projects)

    @http.route(
        ['/task/datalist'],
        type='json',
        auth='public',
        website=True)
    def task_datalist(self, **post):
        search_domain = list()

        if post.get('project_id'):
            search_domain.append(('project_id', '=', post.get('project_id')))

        tasks = request.env['project.task'].search_read(
            search_domain,
            ['id', 'name'],
        )

        return json.dumps(tasks)
