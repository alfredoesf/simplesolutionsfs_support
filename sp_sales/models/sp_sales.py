# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SpSaleOrder(models.Model):
    _inherit = "sale.order"

    # Fields declaration
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', store=True)

    # compute and search fields, in the same order that fields declaration
    @api.multi
    @api.depends('user_id')
    def _compute_department_id(self):
        for rec in self:
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            rec.department_id = employee_id and employee_id.department_id and employee_id.department_id.id or False

    # constrains and onchange

    # CRUD methods

    # action methods

    # business methods
