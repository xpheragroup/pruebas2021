# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from collections import defaultdict
from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re

from odoo.tools.translate import translate_sql_constraint

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    
    '''
    account_group_1 = fields.Many2one('account.group', string='Grupos de cuentas 1', compute='_get_account_group')
    account_group_2 = fields.Many2one('account.group', string='Grupos de cuentas 2', compute='_get_account_group')
    account_group_3 = fields.Many2one('account.group', string='Grupos de cuentas 3', compute='_get_account_group')
    account_group_4 = fields.Many2one('account.group', string='Grupos de cuentas 4', compute='_get_account_group')
    account_group_5 = fields.Many2one('account.group', string='Grupos de cuentas 5', compute='_get_account_group')
    account_group_6 = fields.Many2one('account.group', string='Grupos de cuentas 6', compute='_get_account_group')
    account_group_7 = fields.Many2one('account.group', string='Grupos de cuentas 7', compute='_get_account_group')
    account_group_8 = fields.Many2one('account.group', string='Grupos de cuentas 8', compute='_get_account_group')
    
    account_group_8 = fields.Many2one('account.group', string='Grupos de cuentas 8', compute='_get_account_group', store='True')
    account_group_1 = fields.Many2one('account.group', string='Grupos de cuentas 1', related='account_group_2.parent_id', store='True')
    account_group_2 = fields.Many2one('account.group', string='Grupos de cuentas 2', related='account_group_3.parent_id', store='True')
    account_group_3 = fields.Many2one('account.group', string='Grupos de cuentas 3', related='account_group_4.parent_id', store='True')
    account_group_4 = fields.Many2one('account.group', string='Grupos de cuentas 4', related='account_group_5.parent_id', store='True')
    account_group_5 = fields.Many2one('account.group', string='Grupos de cuentas 5', related='account_group_6.parent_id', store='True')
    account_group_6 = fields.Many2one('account.group', string='Grupos de cuentas 6', related='account_group_7.parent_id', store='True')
    account_group_7 = fields.Many2one('account.group', string='Grupos de cuentas 7', related='account_group_8.parent_id', store='True')
    '''
    account_group_8 = fields.Many2one('account.group', string='Grupos de cuentas 8', compute='_get_account_group')
    account_group_1 = fields.Many2one('account.group', string='Grupos de cuentas 1', related='account_group_2.parent_id')
    account_group_2 = fields.Many2one('account.group', string='Grupos de cuentas 2', related='account_group_3.parent_id')
    account_group_3 = fields.Many2one('account.group', string='Grupos de cuentas 3', related='account_group_4.parent_id')
    account_group_4 = fields.Many2one('account.group', string='Grupos de cuentas 4', related='account_group_5.parent_id')
    account_group_5 = fields.Many2one('account.group', string='Grupos de cuentas 5', related='account_group_6.parent_id')
    account_group_6 = fields.Many2one('account.group', string='Grupos de cuentas 6', related='account_group_7.parent_id')
    account_group_7 = fields.Many2one('account.group', string='Grupos de cuentas 7', related='account_group_8.parent_id')
    '''
    account_group_1 = fields.Many2one('account.group', string='Grupos de cuentas 1', compute='_get_account_group', store='True')
    account_group_2 = fields.Many2one('account.group', string='Grupos de cuentas 2', compute='_get_account_group', store='True')
    account_group_3 = fields.Many2one('account.group', string='Grupos de cuentas 3', compute='_get_account_group', store='True')
    account_group_4 = fields.Many2one('account.group', string='Grupos de cuentas 4', compute='_get_account_group', store='True')
    account_group_5 = fields.Many2one('account.group', string='Grupos de cuentas 5', compute='_get_account_group', store='True')
    account_group_6 = fields.Many2one('account.group', string='Grupos de cuentas 6', compute='_get_account_group', store='True')
    account_group_7 = fields.Many2one('account.group', string='Grupos de cuentas 7', compute='_get_account_group', store='True')
    account_group_8 = fields.Many2one('account.group', string='Grupos de cuentas 8', compute='_get_account_group', store='True')
    '''
    account_group_lv_1 = fields.Many2one('account.group', string='Grupos de cuentas 1', compute='_get_account_group_lv_1', store='True')
    account_group_lv_2 = fields.Many2one('account.group', string='Grupos de cuentas 2', compute='_get_account_group_lv_2', store='True')
    account_group_lv_3 = fields.Many2one('account.group', string='Grupos de cuentas 3', compute='_get_account_group_lv_3', store='True')
    account_group_lv_4 = fields.Many2one('account.group', string='Grupos de cuentas 4', compute='_get_account_group_lv_4', store='True')
    account_group_lv_5 = fields.Many2one('account.group', string='Grupos de cuentas 5', compute='_get_account_group_lv_5', store='True')
    account_group_lv_6 = fields.Many2one('account.group', string='Grupos de cuentas 6', compute='_get_account_group_lv_6', store='True')
    account_group_lv_7 = fields.Many2one('account.group', string='Grupos de cuentas 7', compute='_get_account_group_lv_7', store='True')
    account_group_lv_8 = fields.Many2one('account.group', string='Grupos de cuentas 8', compute='_get_account_group_lv_8', store='True')
    
    @api.depends('account_id')
    def _get_account_group(self):   
        for line in self:
            if line.account_id.group_id:
                line.account_group_8 = line.account_id.group_id
    
    @api.depends('account_group_8')
    def _get_account_group_lv_8(self):   
        for line in self:
            if line.account_group_8.parent_id:
                line.account_group_lv_8 = line.account_group_8.parent_id

    @api.depends('account_group_7')
    def _get_account_group_lv_7(self):   
        for line in self:
            if line.account_group_7.parent_id:
                line.account_group_lv_7 = line.account_group_7.parent_id

    @api.depends('account_group_6')
    def _get_account_group_lv_6(self):   
        for line in self:
            if line.account_group_6.parent_id:
                line.account_group_lv_6 = line.account_group_6.parent_id

    @api.depends('account_group_5')
    def _get_account_group_lv_5(self):   
        for line in self:
            if line.account_group_5.parent_id:
                line.account_group_lv_5 = line.account_group_5.parent_id


    @api.depends('account_group_4')
    def _get_account_group_lv_4(self):   
        for line in self:
            if line.account_group_4.parent_id:
                line.account_group_lv_4 = line.account_group_4.parent_id

    @api.depends('account_group_3')
    def _get_account_group_lv_3(self):   
        for line in self:
            if line.account_group_3.parent_id:
                line.account_group_lv_3 = line.account_group_3.parent_id

    @api.depends('account_group_2')
    def _get_account_group_lv_2(self):   
        for line in self:
            if line.account_group_2.parent_id:
                line.account_group_lv_2 = line.account_group_2.parent_id

    @api.depends('account_group_1')
    def _get_account_group_lv_1(self):   
        for line in self:
            if line.account_group_1.parent_id:
                line.account_group_lv_1 = line.account_group_1.parent_id

    '''@api.depends('account_id')
    def _get_account_group(self):        
        for line in self:
            line.account_group_8 = None
            line.account_group_7 = None
            line.account_group_6 = None
            line.account_group_5 = None
            line.account_group_4 = None
            line.account_group_3 = None
            line.account_group_2 = None
            line.account_group_1 = None
            if line.account_id.group_id:
                line.account_group_8 = line.account_id.group_id
            if line.account_group_8:
                if line.account_group_8.parent_id:
                    line.account_group_7 = line.account_group_8.parent_id
            if line.account_group_7:
                if line.account_group_7.parent_id:
                    line.account_group_6 = line.account_group_7.parent_id
            if line.account_group_6:
                if line.account_group_6.parent_id:
                    line.account_group_5 = line.account_group_6.parent_id
            if line.account_group_5:
                if line.account_group_5.parent_id:
                    line.account_group_4 = line.account_group_5.parent_id
            if line.account_group_4:
                if line.account_group_4.parent_id:
                    line.account_group_3 = line.account_group_4.parent_id
            if line.account_group_3:
                if line.account_group_3.parent_id:
                    line.account_group_2 = line.account_group_3.parent_id
            if line.account_group_2:
                if line.account_group_2.parent_id:
                    line.account_group_1 = line.account_group_2.parent_id
            line.account_group_8 = None
            line.account_group_7 = None
            line.account_group_6 = None
            line.account_group_5 = None
            line.account_group_4 = None
            line.account_group_3 = None
            line.account_group_2 = None
            line.account_group_1 = None
            group_id=line.account_id.group_id
            while group_id.parent_id:
                if len(group_id.code_prefix)==8:
                    line.account_group_8 = group_id
                    if line.account_group_8.parent_id:
                        group_id = line.account_group_8.parent_id
                elif len(group_id.code_prefix)==7:
                    line.account_group_7 = group_id
                    if line.account_group_7.parent_id:
                        group_id = line.account_group_7.parent_id
                elif len(group_id.code_prefix)==6:
                    line.account_group_6 = group_id
                    if line.account_group_6.parent_id:
                        group_id = line.account_group_6.parent_id
                elif len(group_id.code_prefix)==5:
                    line.account_group_5 = group_id
                    if line.account_group_5.parent_id:
                        group_id = line.account_group_5.parent_id
                elif len(group_id.code_prefix)==4:
                    line.account_group_4 = group_id
                    if line.account_group_4.parent_id:
                        group_id = line.account_group_4.parent_id
                elif len(group_id.code_prefix)==3:
                    line.account_group_3 = group_id
                    if line.account_group_3.parent_id:
                        group_id = line.account_group_3.parent_id
                elif len(group_id.code_prefix)==2:
                    line.account_group_2 = group_id
                    if line.account_group_2.parent_id:
                        group_id = line.account_group_2.parent_id
                elif len(group_id.code_prefix)==1:
                    line.account_group_1 = group_id
                    if line.account_group_1.parent_id:
                        group_id = line.account_group_1.parent_id'''


    '''@api.depends('account_id')
    def _get_account_group_lv(self):
        for line in self:
            if line.account_group_1:
                if len(line.account_group_1.code_prefix)==1:
                    line.account_group_lv_1 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==2:
                    line.account_group_lv_2 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==3:
                    line.account_group_lv_3 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==4:
                    line.account_group_lv_4 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==5:
                    line.account_group_lv_5 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==6:
                    line.account_group_lv_6 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==7:
                    line.account_group_lv_7 = line.account_group_1
                elif len(line.account_group_1.code_prefix)==8:
                    line.account_group_lv_8 = line.account_group_1
            
            if line.account_group_8:
                if len(line.account_group_8.code_prefix)==1:
                    line.account_group_lv_1 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==2:
                    line.account_group_lv_2 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==3:
                    line.account_group_lv_3 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==4:
                    line.account_group_lv_4 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==5:
                    line.account_group_lv_5 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==6:
                    line.account_group_lv_6 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==7:
                    line.account_group_lv_7 = line.account_group_1
                elif len(line.account_group_8.code_prefix)==8:
                    line.account_group_lv_8 = line.account_group_1
'''
            