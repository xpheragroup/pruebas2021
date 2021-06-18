import datetime
from collections import defaultdict
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import date_utils, float_compare, float_round, float_is_zero

class Override_Bom_Production(models.Model):
    _inherit = 'mrp.production'

    cost_center = fields.Many2one(
        string="Centro de Costos",
        comodel_name='account.analytic.account')

    cycle = fields.Integer(string='Ciclo')
    reference = fields.Char(string='Referencia')
    total_real_cost = fields.Float(string='Costo total real receta', compute='_compute_real_cost')
    total_std_cost = fields.Float(string='Costo total estándar receta', compute='_compute_std_cost')
    
    total_real_cost_prom = fields.Float(string='Costo total real receta (promedio almacén)', compute='_compute_real_cost_prom')
    total_std_cost_prom = fields.Float(string='Costo total estándar receta (promedio almacén)', compute='_compute_std_cost_prom')

    total_real_cost_blocked = fields.Float(string='Costo total real receta')
    total_std_cost_blocked = fields.Float(string='Costo total estándar receta')
    
    total_real_cost_prom_blocked = fields.Float(string='Costo total real receta (promedio almacén)')
    total_std_cost_prom_blocked = fields.Float(string='Costo total estándar receta (promedio almacén)')

    add_product_id = fields.Many2many(
        'product.product', string='Productos Adicionales',
        domain="[('bom_ids', '!=', False), ('bom_ids.active', '=', True), ('bom_ids.type', '=', 'normal'), ('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]})
    add_bom_id = fields.Many2many(
        'mrp.bom', string='Lista de materiales de productos adicionales',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',add_product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',add_product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        check_company=True,
        help="Permite agregar las listas de materiales de los productos adicionales a la orden de producción.")

    # Costo promedio en el módulo de fabricación
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        check_company=True,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")


    @api.model
    def _get_default_location_src_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self.env.context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        default=_get_default_location_src_id,
        readonly=True, required=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will look for components.")

    move_raw_ids = fields.One2many(
        'stock.move', 'raw_material_production_id', 'Components',
        copy=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        domain=[('scrapped', '=', False)])

    state = fields.Selection([
        ('draft', 'Elaboración'),
        ('review', 'Revisión'),
        ('approv', 'Aprobación'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True,
        help=" * Draft: The MO is not confirmed yet.\n"
             " * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.\n"
             " * In Progress: The production has started (on the MO or on the WO).\n"
             " * To Close: The production is done, the MO has to be closed.\n"
             " * Done: The MO is closed, the stock moves are posted. \n"
             " * Cancelled: The MO has been cancelled, can't be confirmed anymore.")

    @api.onchange('bom_id')
    def check_state_bom_id(self):
        for line in self.move_raw_ids:
            line.location_src = self.location_src_id

        bom = self.bom_id
        if bom.state == 'Borrador':
            if bom.product_id.name:
                raise UserError(_('La lista de materiales ' + bom.product_id.name + ' está en estado borrador.'))
            elif bom.product_tmpl_id.name:
                raise UserError(_('La lista de materiales ' + bom.product_tmpl_id.name + ' está en estado borrador.'))
            else:
                raise UserError(_('La lista de materiales está en estado borrador.'))

        sub_bom_line = []
        for bom_line in bom.bom_line_ids:
            sub_bom_line += bom_line

        for bom_lines_lists in sub_bom_line:
            for sub_bom_lines in bom_lines_lists:
                sub_sub_lists = self.env['mrp.bom'].search([('product_id.id','=',sub_bom_lines.product_id.id)],limit=1)
                if sub_sub_lists.bom_line_ids and sub_sub_lists.bom_line_ids not in sub_bom_line:
                    sub_bom_line += sub_sub_lists.bom_line_ids

        for state_bom in sub_bom_line:
            bom_list_state = self.env['mrp.bom'].search([('product_id.id','=',state_bom.product_id.id)],limit=1)
            if bom_list_state.state == 'Borrador':
                if bom_list_state.product_id.name:
                    raise UserError(_('La lista de materiales ' + bom_list_state.product_id.name + ' está en estado borrador.'))
                elif bom_list_state.product_tmpl_id.name:
                    raise UserError(_('La lista de materiales ' + bom_list_state.product_tmpl_id.name + ' está en estado borrador.'))
                else:
                    raise UserError(_('La lista de materiales está en estado borrador.'))

    @api.onchange('add_bom_id')
    def check_state_add_bom_id(self):
        for line in self.move_raw_ids:
            line.location_src = self.location_src_id

        for bom in self.add_bom_id:
            if bom.state == 'Borrador':
                if bom.product_id.name:
                    raise UserError(_('La lista de materiales ' + bom.product_id.name + ' está en estado borrador.'))
                elif bom.product_tmpl_id.name:
                    raise UserError(_('La lista de materiales ' + bom.product_tmpl_id.name + ' está en estado borrador.'))
                else:
                    raise UserError(_('La lista de materiales está en estado borrador.'))

            sub_bom_line = []
            for bom_line in bom.bom_line_ids:
                sub_bom_line += bom_line

            for bom_lines_lists in sub_bom_line:
                for sub_bom_lines in bom_lines_lists:
                    sub_sub_lists = self.env['mrp.bom'].search([('product_id.id','=',sub_bom_lines.product_id.id)],limit=1)
                    if sub_sub_lists.bom_line_ids and sub_sub_lists.bom_line_ids not in sub_bom_line:
                        sub_bom_line += sub_sub_lists.bom_line_ids

            for state_bom in sub_bom_line:
                bom_list_state = self.env['mrp.bom'].search([('product_id.id','=',state_bom.product_id.id)],limit=1)
                if bom_list_state.state == 'Borrador':
                    if bom_list_state.product_id.name:
                        raise UserError(_('La lista de materiales ' + bom_list_state.product_id.name + ' está en estado borrador.'))
                    elif bom_list_state.product_tmpl_id.name:
                        raise UserError(_('La lista de materiales ' + bom_list_state.product_tmpl_id.name + ' está en estado borrador.'))
                    else:
                        raise UserError(_('La lista de materiales está en estado borrador.'))

    @api.depends('move_raw_ids.std_quantity', 'move_raw_ids.product_id.standard_price')
    def _compute_std_cost(self):
        """ Calcula el costo estándar a partir de los productos presentes en 'move_raw_ids'. """
        for record in self:
            std_cost = sum(product.std_quantity * product.product_id.standard_price for product in record.move_raw_ids)
            record.total_std_cost = std_cost

    @api.depends('move_raw_ids.std_quantity', 'move_raw_ids.product_id.standard_price')
    def _compute_std_cost_prom(self):
        """ Calcula el costo estándar a partir de los productos presentes en 'move_raw_ids'. """
        for record in self:
            std_cost = sum(product.std_quantity * product.cost_unit_lot_fab for product in record.move_raw_ids)
            record.total_std_cost_prom = std_cost 
      
    @api.depends('move_raw_ids.product_id', 'move_raw_ids.product_id.standard_price')
    def _compute_real_cost(self):
        """ Calcula el costo real a partir de los productos presentes en 'move_raw_ids' y las cantidades digitadas por el usuario. """
        for record in self:
            real_cost = sum(product.product_uom_qty * product.product_id.standard_price for product in record.move_raw_ids)
            record.total_real_cost = real_cost
    
    @api.depends('move_raw_ids.product_id', 'move_raw_ids.product_id.standard_price')
    def _compute_real_cost_prom(self):
        """ Calcula el costo real a partir de los productos presentes en 'move_raw_ids' y las cantidades digitadas por el usuario. """
        for record in self:
            real_cost = sum(product.product_uom_qty * product.cost_unit_lot_fab for product in record.move_raw_ids)
            record.total_real_cost_prom = real_cost

    @api.onchange('total_real_cost','total_real_cost_prom','total_std_cost','total_std_cost_prom')
    def get_cost(self):
        if (self.state != 'done') or (self.state != 'cancel'):
            self.total_real_cost_blocked = self.total_real_cost
            self.total_real_cost_prom_blocked = self.total_real_cost_prom
            self.total_std_cost_blocked = self.total_std_cost
            self.total_std_cost_prom_blocked = self.total_std_cost_prom
    
    @api.constrains('state')
    def get_cost_(self):
        self.total_real_cost_blocked = self.total_real_cost
        self.total_real_cost_prom_blocked = self.total_real_cost_prom
        self.total_std_cost_blocked = self.total_std_cost
        self.total_std_cost_prom_blocked = self.total_std_cost_prom

    def _get_moves_raw_values(self):
        """ @Overwrite: Obtiene los ingredietes de un producto una vez es selccionado.
        En lugar de extraer los productos en la lista de materiales se dirige a sus listas hijas
        'child_line_ids' para poblar la lista de productos

        returns:
        list<stock.move> -- Lista de productos asociados a la orden de producción

        """
        moves = []
        for production in self:
            factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            if production.add_bom_id:
                for add_pro in production.add_bom_id:
                    factor2 = production.product_uom_id._compute_quantity(production.product_qty, add_pro.product_uom_id) / add_pro.product_qty
                    boms2, lines2 = add_pro.explode(production.product_id, factor2, picking_type=add_pro.picking_type_id)
                    boms += boms2
                    lines_aux2=[]
                    lines_aux3=[]
                    for i in range(len(lines2)):
                        lines_aux=[]
                        lines_aux.append(lines2[i][0]._origin)
                        lines_aux.append(lines2[i][1])
                        lines_aux2.append(lines_aux)

                    lines_aux3 = [tuple(e) for e in lines_aux2]
                    lines += lines_aux3
            
            for bom_line, line_data in lines:
                if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom' or\
                        bom_line.product_id.type not in ['product', 'consu']:
                    continue
                
                for p in bom_line.child_line_ids:
                    moves.append(production._get_move_raw_values(p, {'qty': p.product_qty * self.product_uom_qty, 'parent_line': ''})) 
                
                if len(bom_line.child_line_ids) == 0:
                    moves.append(production._get_move_raw_values(bom_line, line_data))

        return moves
    
    @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id')
    def _onchange_move_raw(self):
        self.move_raw_ids=None
        if self.product_id != self._origin.product_id:  
            self.move_raw_ids = [(5,)]
        if self.bom_id and self.product_qty > 0 :
            # keep manual entries
            list_move_raw = [(4, move.id) for move in self.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
            moves_raw_values = self._get_moves_raw_values()
            move_raw_dict = {move.bom_line_id.id: move for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)}
            for move_raw_values in moves_raw_values:
                if move_raw_values['bom_line_id'] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                else:
                    # add new entries
                    list_move_raw += [(0, 0, move_raw_values)]
            self.move_raw_ids = list_move_raw
        else:
            self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)]