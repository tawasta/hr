
from lxml import etree
from odoo import api, models
import simplejson


class HrAttendance(models.Model):

    _inherit = 'hr.attendance'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Changes all fields to readonly for my_attendances-group"""
        res = super(HrAttendance, self).fields_view_get(view_id=view_id,
                                                        view_type=view_type,
                                                        toolbar=toolbar,
                                                        submenu=submenu)

        if self.env.user.has_group(
                'hr_attendance_my_attendances.my_attendances') and \
                view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field"):
                node.set('readonly', '1')
                node.set('modifiers', simplejson.dumps({"readonly": True}))
            res['arch'] = etree.tostring(doc)
        return res
