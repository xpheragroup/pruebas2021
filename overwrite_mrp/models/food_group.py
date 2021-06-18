from odoo import api, fields, models

class FoodGroup(models.Model):

    _name = 'overwrite_mrp.food_group'
    _description = 'Food Group'

    name = fields.Char(string='Nombre')
