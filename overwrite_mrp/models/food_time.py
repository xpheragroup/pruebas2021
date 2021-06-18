from odoo import api, fields, models

class FoodTime(models.Model):

    _name = 'overwrite_mrp.food_time'
    _description = 'Food Time defined by the client'

    name = fields.Char(string='Tiempo')
