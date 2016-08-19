openerp.hr_timesheet_task = function(instance) { 

    var module = instance.hr_timesheet_sheet

    module.WeeklyTimesheet = module.WeeklyTimesheet.extend({
        onchange_account_id: function() {
            var self = this
            var account_id = self.account_m2o.get_value();
            if (account_id === false) { return; }
            self.task_m2o.node.attrs.domain = [
               // show only tasks linked to the selected project
               ['project_id.analytic_account_id','=',account_id],
               // Don't show closed tasks
               ['stage_id.fold','=', false],
               // ignore tasks already in the timesheet
               ['id', 'not in', _.pluck(self.accounts, "task")],
            ]
            self.task_m2o.node.attrs.context = {'account_id': account_id};
            self.task_m2o.set_value(false);
            self.task_m2o.render_value();
        },
    });
};
