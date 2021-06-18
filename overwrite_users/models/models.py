# -*- coding: utf-8 -*-

from odoo import models, fields, api

#Domain rules for point managers in inventory and purchases. model=res.users
class overwrite_user(models.Model):
     _inherit = 'res.users'

     warehouse_ids = fields.Many2many('stock.warehouse',string='Almacen')
