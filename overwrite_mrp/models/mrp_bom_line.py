from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, float_compare

from itertools import groupby

class Override_Bom_Line(models.Model):
    _inherit = 'mrp.bom.line'

    food_group = fields.Many2one(
        string='Grupo de Alimento',
        comodel_name='overwrite_mrp.food_group'
        )


