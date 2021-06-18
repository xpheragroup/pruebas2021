from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, float_compare

from itertools import groupby

class Override_Bom(models.Model):
    _inherit = 'mrp.bom'

    cost_center = fields.Many2one(
        string="Centro de Costos",
        comodel_name='account.analytic.account')

    cycle = fields.Integer(string='Ciclo')
    
    food_time = fields.Many2one(
        string='Tiempo de comida',
        comodel_name='overwrite_mrp.food_time'
        )
    
    state = fields.Selection(
        string='Estado', 
        selection=[('Borrador', 'Borrador'), ('Aprobado', 'Aprobado')],
        default='Borrador',
        tracking=True)

    approval_user = fields.Many2one(
        string='Usuario que aprueba',
        comodel_name='res.users'
        )
    
    approval_date = fields.Datetime(string='Fecha de aprobación')

    repetitions = fields.Integer(string='Repeticiones', default=0)
    quantity = fields.Integer(string='Cantidad', default=0)
    total = fields.Integer(string='Total', compute='_calc_total')

    @api.depends('repetitions', 'quantity')
    def _calc_total(self):
        """ Calcula la multiplicacion de repeticiones y cantidad. """
        for record in self:
            record.total = record.repetitions * record.quantity

    def approve_list(self):
        """ Permite poner en estado aprobado una lista de materiales. """
        register = self.env['mrp.bom'].search([('id', '=', self.id)])
        if register.state != 'Aprobado':
            register.write({
                'state': 'Aprobado',
                'approval_user': self.env.user,
                'approval_date': fields.Datetime.now()
            })
    
    @api.onchange(
        'code', 'active', 'type', 'product_tmpl_id', 'product_id', 'product_qty', 'picking_type_id',
        'bom_line_ids', 'consuption', 'create_uid', 'create_date',
        'cost_center', 'cycle', 'state', 'food_time', 'approval_user', 'approval_date' 
        )
    def _onchange_anything(self):
        """ Hace que cuando haya un cambio en cualquiera de los campos vuelva al estado borrador. """
        self.state = 'Borrador'
        self.approval_user = None
        self.approval_date = None
