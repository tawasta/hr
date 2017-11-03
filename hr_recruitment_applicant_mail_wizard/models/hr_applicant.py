# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, exceptions
import uuid


class HrApplicant(models.Model):

    _inherit = 'hr.applicant'

    @api.multi
    def _get_show_email_button(self):
        ''' Inherit this function to define more intricately when the button should be available '''
        for applicant in self:
            applicant.show_email_button = True

    def _get_email_template(self):
        ''' Inherit to use a custom e-mail template '''
        return False

    def _get_email_context(self):
        ''' Inherit to use a custom context '''
        template_id = self._get_email_template()
        ctx = dict()
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return ctx

    @api.multi
    def launch_wizard(self):
        ''' Open the wizard for composing new e-mail '''
        self.ensure_one()

        try:
            compose_form_id = self.env['ir.model.data'].get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = self._get_email_context()

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    show_email_button = fields.Boolean(compute=_get_show_email_button, string='Show the E-mail Applicant button')