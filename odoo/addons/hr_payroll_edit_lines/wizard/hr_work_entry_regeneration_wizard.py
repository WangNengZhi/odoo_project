# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrWorkEntryRegenerationWizard(models.TransientModel):
    _name = 'hr.work.entry.regeneration.wizard'
    _description = 'Regenerate Employee Work Entries'

    earliest_available_date = fields.Date('Earliest date', compute='_compute_earliest_available_date')
    earliest_available_date_message = fields.Char(readonly=True, store=False, default='')
    latest_available_date = fields.Date('Latest date', compute='_compute_latest_available_date')
    latest_available_date_message = fields.Char(readonly=True, store=False, default='')
    date_from = fields.Date('From', required=True, default=lambda self: self.env.context.get('date_start'))
    date_to = fields.Date('To', required=True, default=lambda self: self.env.context.get('date_end'))
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    validated_work_entry_ids = fields.Many2many('hr.work.entry', string='Work Entries Within Interval',
                                   compute='_compute_validated_work_entry_ids')
    search_criteria_completed = fields.Boolean(compute='_compute_search_criteria_completed')
    valid = fields.Boolean(compute='_compute_valid')

    @api.depends('employee_id')
    def _compute_earliest_available_date(self):
        for wizard in self:
            dates = wizard.mapped('employee_id.contract_ids.date_generated_from')
            wizard.earliest_available_date = min(dates) if dates else None

    @api.depends('employee_id')
    def _compute_latest_available_date(self):
        for wizard in self:
            dates = wizard.mapped('employee_id.contract_ids.date_generated_to')
            wizard.latest_available_date = max(dates) if dates else None

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_validated_work_entry_ids(self):
        for wizard in self:
            validated_work_entry_ids = self.env['hr.work.entry']
            if wizard.search_criteria_completed:
                search_domain = [('employee_id', '=', self.employee_id.id),
                                 ('date_start', '>=', self.date_from),
                                 ('date_stop', '<=', self.date_to),
                                 ('state', '=', 'validated')]
                validated_work_entry_ids = self.env['hr.work.entry'].search(search_domain, order="date_start")
            wizard.validated_work_entry_ids = validated_work_entry_ids

    @api.depends('validated_work_entry_ids')
    def _compute_valid(self):
        for wizard in self:
            wizard.valid = wizard.search_criteria_completed and len(wizard.validated_work_entry_ids) == 0

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_search_criteria_completed(self):
        for wizard in self:
            wizard.search_criteria_completed = self.date_from and self.date_to and self.employee_id

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _check_dates(self):
        for wizard in self:
            wizard.earliest_available_date_message = ''
            wizard.latest_available_date_message = ''
            if wizard.search_criteria_completed:
                if wizard.date_from > wizard.date_to:
                    date_from = wizard.date_from
                    wizard.date_from = wizard.date_to
                    wizard.date_to = date_from
                if wizard.date_from < wizard.earliest_available_date:
                    wizard.date_from = wizard.earliest_available_date
                    wizard.earliest_available_date_message = _('The earliest available date is %s', self._date_to_string(wizard.earliest_available_date))
                if wizard.date_to > wizard.latest_available_date:
                    wizard.date_to = wizard.latest_available_date
                    wizard.latest_available_date_message = _('The latest available date is %s', self._date_to_string(wizard.latest_available_date))

    @api.model
    def _date_to_string(self, date):
        if not date:
            return ''
        user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        return date.strftime(user_date_format)

    def regenerate_work_entries(self):
        self.ensure_one()
        if not self.valid:
            raise ValidationError(_("In order to regenerate the work entries, you need to provide the wizard with an employee_id, a date_from and a date_to. In addition to that, the time interval defined by date_from and date_to must not contain any validated work entries."))

        if self.date_from < self.earliest_available_date or self.date_to > self.latest_available_date:
            raise ValidationError(_("The from date must be >= '%(earliest_available_date)s' and the to date must be <= '%(latest_available_date)s', which correspond to the generated work entries time interval.", earliest_available_date=self._date_to_string(self.earliest_available_date), latest_available_date=self._date_to_string(self.latest_available_date)))
        work_entries = self.env['hr.work.entry'].search([('employee_id', '=', self.employee_id.id),
                                                         ('date_stop', '>=', self.date_from),
                                                         ('date_start', '<=', self.date_to)])
        work_entries.write({'active': False})
        self.employee_id.with_context(force_work_entry_generation=True).generate_work_entries(self.date_from, self.date_to)
        action = self.env.ref('hr_work_entry.hr_work_entry_action').read()[0]
        return action
