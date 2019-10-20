odoo.define('hr_timesheet', function (require) {
    var _t = require('web.core')._t;

    var ajax = require('web.ajax');

    $(function() {

        $('#project_id').select2({
            placeholder: _t('Select project'),
            allowClear: true
        });

        $('#task_id').select2({
            placeholder: _t('Select task'),
            allowClear: false
        });

        // Creates project datalist
        function create_project_datalist() {
            var action = "/project/datalist";
            console.log(action);

            // Remove old project options
            $('#project-datalist').empty();

            var task = $('#select-task');
            var task_id = $('#task-datalist option').filter(function() {
                return this.value == task.val();
            }).data('id');

            values = {
                'task_id': task_id,
            };

            ajax.jsonRpc(action, 'call', values).then(function(result){
                var response=JSON.parse(result);

                // Add projects
                $.each(response, function() {
                    //<option t-att-data-value="project.id" t-att-value="project.name"><span t-if="project.partner_id" t-field="project.partner_id.name"/></option>
                    $('#project-datalist').append(
                        $("<option />").val(this.name).attr('data-id', this.id)
                    );
                });
            });
        }

        // Creates task datalist
        function create_task_datalist() {
            var action = "/task/datalist";

            var task = $('#task_id');

            // Remove old task selections
            task.empty().trigger("change");
            var project_id = $('#project_id').val();

            values = {
                'project_id': project_id,
            };

            ajax.jsonRpc(action, 'call', values).then(function(result){
                var response=JSON.parse(result);

                // Add tasks
                $.each(response, function() {
                    var option = new Option(this.name, this.id, true, true);
                    task.append(option).trigger('change');
                });

            });
        }

        function round(number, increment, offset) {
            return Math.ceil((number - offset) / increment ) * increment + offset;
        }

        $('#timer').timer({
            duration: '1m',
            callback: function() {
                var seconds = $('#timer').data('seconds')
                var minutes = Math.floor(seconds % 3600 / 60);
                var hours = Math.floor(seconds / 3600);

                $('#select-hours').val(hours);
                // Round up to nearest 5
                var increment = 5;
                var rounded = Math.ceil((+minutes + 1) / increment) * increment

                /*
                console.log(seconds);
                console.log(minutes);
                console.log(hours);
                console.log(rounded);
                console.log('-');
                */

                $('#select-minutes').val(rounded);
            },
            repeat: true
        });

        create_task_datalist();
        $('#project_id').change(function() {
            create_task_datalist();
        });

    });
});