# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SpPicking(models.Model):
    _inherit = "stock.picking"

    def _default_department(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_id and employee_id.department_id and employee_id.department_id.id or False

    # Fields declaration
    department_id = fields.Many2one('hr.department', string='Department', default=_default_department, readonly=True)

    # compute and search fields, in the same order that fields declaration

    # constrains and onchange

    # CRUD methods

    # action methods

    # business methods
