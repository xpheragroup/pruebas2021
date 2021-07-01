# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class external_requisitions(models.Model):
#     _name = 'external_requisitions.external_requisitions'
#     _description = 'external_requisitions.external_requisitions'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
