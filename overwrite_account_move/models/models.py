# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class overwrite_account_move(models.Model):
#     _name = 'overwrite_account_move.overwrite_account_move'
#     _description = 'overwrite_account_move.overwrite_account_move'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
