from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning, RedirectWarning, except_orm
from odoo.tools import float_round, float_compare

from itertools import groupby

class Override_StockMove(models.Model):
    _inherit = 'stock.move'

    fab_product = fields.Many2one('product.product', string='Preparación', readonly=True, check_company=True,
        compute='_compute_custom_values')
    std_quantity = fields.Float(string='Cantidad estándar', readonly=True, digits=(12,4), compute='_compute_custom_values')
    missing = fields.Float(string='Cantidad Faltante', readonly=True, digits=(12,4), compute='_compute_custom_values')
    deviation = fields.Float(string='Desviación', compute='_compute_custom_values', digits=(12,4))
    deviation_per = fields.Float(string='Desviación Porcentual', compute='_compute_custom_values')
    real_cost = fields.Float(string='Costo real', compute='_compute_custom_values', digits=(12,4))
    std_cost = fields.Float(string='Costo estándar', compute='_compute_custom_values', digits=(12,4))
    existence_qty = fields.Float(string='Existencias', compute='_compute_existence_qty', digits=(12,4))

    # Costo promedio movimiento de inventario en fabricación
    cost_unit_lot_fab = fields.Float(string='Costo Promedio de las Existencias',compute='_compute_cost_real')
    real_cost_prom = fields.Float(string='Costo real promerio', compute='_compute_custom_values', digits=(12,4))
    std_cost_prom = fields.Float(string='Costo estándar promedio', compute='_compute_custom_values', digits=(12,4))
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=True,
        check_company=True,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    
    # Costo promedio movimiento de inventario en fabricación
    def _compute_cost_real(self):   
        
        for line in self:
            lugar = self.location_id[0]
            line.cost_unit_lot_fab = 0
            product = line.product_id
            costo_prom = 0
            if lugar:
                for quant in self.env['stock.quant'].search([('product_id.id','=',product.id),('location_id','=',lugar.complete_name)]):
                    costo_prom = quant.cost_unit_average
                if costo_prom:
                    line.cost_unit_lot_fab = costo_prom
                else:
                    line.cost_unit_lot_fab = line.product_id.standard_price

    def to_draft_production_stock_move(self):
        for move in self:
            move.write({'state': 'draft'})
            move.unlink()
        return True

    @api.depends('std_quantity', 'product_qty', 'product_id.standard_price', 'product_uom_qty', 'reserved_availability', 'product_id.qty_available')
    def _compute_custom_values(self):
        """ Calcula los campos añadidos al modelo cruzando información ya existente. 
        fab_product: product.product    - Producto padre del cual proviene el ingrediente
        std_quantity: float             - Cantidad de productos a fabricar x cantidad en la lista de materiales
        missing: float                  - Cantidad necesitada de producto - cantidad reservada
        deviation: float                - Cantidad en que difiere la cantidad digitada de la estándar en la receta
        deviation_per: float            - Razon de la diferencia entre las cantidades digitadas y estandar
        real_cost: float                - Valor total del producto x cantidad digitada
        std_cost: float                 - Valor total del producto x cantidad estándar

        """
        for record in self:
            record.fab_product = record.bom_line_id.bom_id.product_id
            record.std_quantity = record.raw_material_production_id.product_uom_qty * record.bom_line_id.product_qty
            record.missing = record.product_uom_qty - record.reserved_availability
            record.deviation = record.product_uom_qty - record.std_quantity
            record.deviation_per = record.deviation / record.std_quantity if record.std_quantity > 0 else 1
            record.real_cost = record.product_uom_qty * record.product_id.standard_price
            record.std_cost = record.std_quantity * record.product_id.standard_price
            record.real_cost_prom = record.product_uom_qty * record.cost_unit_lot_fab
            record.std_cost_prom = record.std_quantity * record.cost_unit_lot_fab

    @api.depends('product_id.qty_available', 'location_id')
    def _compute_existence_qty(self):
        """
        Calcula las existencias en inventario y las muestra en el stock_move del modelo MRP
        :return:
        existence_qty: float
        """
        for record in self:
            existences_temp = 0

            for product_stock_quant in record.location_id.quant_ids:
                if product_stock_quant.product_id == record.product_id:
                    existences_temp = product_stock_quant.quantity

            record.existence_qty = existences_temp