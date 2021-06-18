# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import logging
import pytz

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    name = fields.Char(required=True)
    prefix = fields.Char(help="Prefix value of the record for the sequence", trim=False, copy=False, required=True)
    padding = fields.Integer(string='Sequence Size', required=True, default=9,
                             help="Odoo will automatically adds some '0' on the left of the "
                                  "'Next Number' to get the required padding size.")
    number_next_actual = fields.Integer(compute='_get_number_next_actual', inverse='_set_number_next_actual',
                                        string='Actual Next Number',
                                        help="Next number that will be used. This number can be incremented "
                                        "frequently so the displayed value might already be obsolete", default=1)

    @api.model
    def create(self, values):
        seq = super(IrSequence, self).create(values)
        if values.get('name'):
            if values.get('company_id'):
                name_act = values['name']
                company_act = values['company_id']
                ex_name = len(self.env['ir.sequence'].search([('name', '=', name_act),('company_id.id', '=', company_act)]))
                if ex_name > 1:
                    raise UserError(_('El nombre ' + name_act + ' ya existe.'))
            else:
                name_act = values['name']
                ex_name = len(self.env['ir.sequence'].search([('name', '=', name_act)]))
                if ex_name > 1:
                    raise UserError(_('El nombre ' + name_act + ' ya existe.'))
        
        if values.get('prefix'):
            if values.get('company_id'):
                prefix_act = values['prefix']
                company_act = values['company_id']
                ex_prefix = len(self.env['ir.sequence'].search([('prefix', '=', prefix_act),('company_id.id', '=', company_act)]))
                if ex_prefix > 1:
                    raise UserError(_('El prefijo ' + prefix_act + ' ya existe.'))
            else:
                prefix_act = values['prefix']
                ex_prefix = len(self.env['ir.sequence'].search([('prefix', '=', prefix_act)]))
                if ex_prefix > 1:
                    raise UserError(_('El prefijo ' + prefix_act + ' ya existe.'))
        return seq

    def write(self, values):
        res = super(IrSequence, self).write(values)
        if values.get('name'):
            if values.get('company_id'):
                name_act = values['name']
                company_act = values['company_id']
                ex_name = len(self.env['ir.sequence'].search([('name', '=', name_act),('company_id.id', '=', company_act)]))
                if ex_name > 1:
                    raise UserError(_('El nombre ' + name_act + ' ya existe.'))
            else:
                name_act = values['name']
                ex_name = len(self.env['ir.sequence'].search([('name', '=', name_act)]))
                if ex_name > 1:
                    raise UserError(_('El nombre ' + name_act + ' ya existe.'))
        
        if values.get('prefix'):
            if values.get('company_id'):
                prefix_act = values['prefix']
                company_act = values['company_id']
                ex_prefix = len(self.env['ir.sequence'].search([('prefix', '=', prefix_act),('company_id.id', '=', company_act)]))
                if ex_prefix > 1:
                    raise UserError(_('El prefijo ' + prefix_act + ' ya existe.'))
            else:
                prefix_act = values['prefix']
                ex_prefix = len(self.env['ir.sequence'].search([('prefix', '=', prefix_act)]))
                if ex_prefix > 1:
                    raise UserError(_('El prefijo ' + prefix_act + ' ya existe.'))             
        return res
    
    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count([('name','=like',u"Copy of {}%".format(self.name))])
        copied_prefix = self.search_count([('prefix','=like',u"Copy of {}%".format(self.prefix))])
        
        if not copied_count:
            new_name = u"Copia de {}".format(self.name)
        else:
            new_name = u"Copia de {} ({})".format(self.name, copied_count)
        
        if not copied_prefix:
            new_prefix = u"Copia de {}".format(self.prefix)
        else:
            new_prefix = u"Copia de {} ({})".format(self.prefix, copied_prefix)

        default['name'] = new_name
        default['prefix'] = new_prefix

        return super(IrSequence,self).copy(default)