import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class Picking(models.Model):

    _inherit = "stock.picking"

    name = fields.Char(
        'Reference', default='/',
        copy=False, index=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('approved', 'Aprobado'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')])

    consolidate_picking = fields.Boolean("Enviar Requisiciones", default=False, required=True)
    consolidate_requisition_picking = fields.Many2many('purchase.order.line', string='Requisiciones')
    consolidate_requisition_reference_picking = fields.Char(string='Códigos de Requisiciónes Consolidadas')
    move_ids_without_package = fields.One2many('stock.move', 'picking_id', string="Stock moves not in package", compute='_compute_move_without_package', inverse='_set_move_without_package')
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})

    @api.onchange('consolidate_requisition_picking')
    def consolidar_requisition(self):
        codes=[]
        for line in self.move_ids_without_package:
            if line.code_internal_requisition_picking:
                if line.code_internal_requisition_picking.split(", "):
                    for code_split in line.code_internal_requisition_picking.split(", "):
                            codes.append(code_split)
                code=line.code_internal_requisition_picking
                codes.append(code)

                for code_last_consolidate_requisition in codes:
                    ref_requisition = self.env['purchase.order.line'].search([('code_picking_requisition_line','=',code_last_consolidate_requisition),],limit=1)
                    ref_requisition.code_picking_requisition_line = False
                    ref_requisition.code_order_consolidate_picking = False

        self.move_ids_without_package=None
        self.consolidate_requisition_reference_picking=None
        list_names_reference=[]
        list_names_reference_char=""
        qty_location_origin = self.location_id.quant_ids.product_id

        list_order_lines=[[]]
        consolidate_cuantity=0
        for product_line in self.consolidate_requisition_picking._origin:
            if (product_line.order_id.name[0:4] != 'RINT')and(product_line.order_id.name[0:2] != 'OC'):
                raise UserError(_('La referencia de la orden debe ser RINT o OC proveniente de una requisición interna.'))
            elif product_line.order_id.name[0:2] == 'OC':
                if  self.picking_type_id.name != 'Órdenes de Entrega':
                    raise UserError(_('La referencia de la orden es OC, el tipo de operación debe ser una órden de entrega.'))
                if (not product_line.codigo_rint):
                    raise UserError(_('Las lineas a consolidar deben venir de una requisición interna.'))

            if (self.picking_type_id.name != 'Transferencias Internas')and(self.picking_type_id.name != 'Órdenes de Entrega'):
                raise UserError(_('El tipo de operación debe ser una transferencia interna u órden de entrega.'))

            rint_line_id=product_line.order_id.name
            state_rint=self.env['purchase.order'].search([('name','=',rint_line_id)],limit=1).state
            if (state_rint != 'draft')and(state_rint != 'done'):
                raise UserError(_('La requisición interna debe haber sido aprobada y estar en estado de SOLICITUD DE COTIZACIÓN para poder selecionarla.'))               
            if product_line.block_requisicion_interna_purchase_line:
                raise UserError(_('La referencia de la orden ya ha sido consolidada en una orden de compra o transferencia interna.'))
            if product_line.product_id in qty_location_origin:
                qty_product_origin=0
                for qty_location_origin_product in self.env['stock.quant'].search([('product_id.id','=',product_line.product_id.id),(('location_id.id','=',self.location_id.id))]):
                    qty_product_origin += qty_location_origin_product.quantity
                if qty_product_origin < product_line.product_qty:
                    raise UserError(_('La cantidad del producto ' + product_line.name + ' en la ubicación origen '
                                        'no es suficiente para realizar la transferencia de las cantidades de producto'
                                        'que se quiere consolidar.'))
            elif product_line.product_id not in qty_location_origin:
                raise UserError(_('No hay existencias del producto ' + product_line.name + ' en la ubicación origen.'))

            product_line.code_picking_requisition_line=product_line.order_id.name + " " + product_line.product_id.name
            product_line._rint_picking()
            list_names_reference.append(product_line.code_picking_requisition_line)

            exist=False
            for consol_line in list_order_lines:
                if consol_line:
                    if (consol_line[1] == product_line.product_id.id):
                        qty_product_origin=0
                        qty_aux=consol_line[2]
                        for qty_location_origin_product in self.env['stock.quant'].search([('product_id.id','=',product_line.product_id.id),(('location_id.id','=',self.location_id.id))]):
                            qty_product_origin += qty_location_origin_product.quantity
                        qty_aux += product_line.product_qty
                        if qty_product_origin < qty_aux:
                            raise UserError(_('La cantidad del producto ' + product_line.name + ' en la ubicación origen '
                                                'no es suficiente para realizar la transferencia de las cantidades de producto'
                                                'que se quiere consolidar.'))
                        consol_line[2]+=product_line.product_qty
                        consol_line[6]+= ", " + product_line.code_picking_requisition_line
                        exist=True
            if not exist:
                list_order_lines[consolidate_cuantity].append(product_line.name)
                list_order_lines[consolidate_cuantity].append(product_line.product_id.id)
                list_order_lines[consolidate_cuantity].append(product_line.product_qty)
                list_order_lines[consolidate_cuantity].append(product_line.product_uom.id)
                list_order_lines[consolidate_cuantity].append(self.location_id.id)
                list_order_lines[consolidate_cuantity].append(self.location_dest_id.id)
                list_order_lines[consolidate_cuantity].append(product_line.code_picking_requisition_line)
                list_order_lines.append([])
                vals_list={}
                self.move_ids_without_package += self.env['stock.move'].new(vals_list)
                consolidate_cuantity+=1
        
        position=0
        list_order_lines.pop()
        for line_consol in self.move_ids_without_package:
            line_consol.name=list_order_lines[position][0]
            line_consol.product_id=list_order_lines[position][1]
            line_consol.product_uom_qty=list_order_lines[position][2]
            line_consol.product_uom=list_order_lines[position][3]
            line_consol.location_id=list_order_lines[position][4]
            line_consol.location_dest_id=list_order_lines[position][5]
            line_consol.code_internal_requisition_picking=list_order_lines[position][6]
            line_consol.internal_requisition_picking=False
            position+=1

        punto=1
        coma=len(list_names_reference)
        for ref in list_names_reference:
            list_names_reference_char+=ref
            if punto == coma:
                list_names_reference_char +=". "
            else:
                list_names_reference_char +=", "
            punto+=1
        self.consolidate_requisition_reference_picking=list_names_reference_char

        if self.name != "/":  
            for product_line in self.consolidate_requisition_picking:
                id_line_order=product_line._origin.id
                ref_requisition = self.env['purchase.order.line'].search([('id','=',id_line_order)],limit=1)
                ref_requisition.code_order_consolidate_picking = self.name
        
        

    @api.model
    def create(self, vals):

        res = super(Picking, self).create(vals)

        for values in vals:
            if values == 'consolidate_requisition_reference_picking':
                if vals['consolidate_requisition_reference_picking']:
                    for product_line_block in vals['move_ids_without_package']:
                        block_requisicion=product_line_block[2]
                        block_requisicion['internal_requisition_picking']=True

                if vals['consolidate_requisition_reference_picking']:                 
                    for product_line in vals['consolidate_requisition_picking']:
                        for id_line_order in product_line[2]:
                            ref_requisition = self.env['purchase.order.line'].search([('id','=',id_line_order)],limit=1)
                            ref_requisition.code_order_consolidate_picking = vals['name']

        return res

    def write(self, vals):

        res = super(Picking, self).write(vals)

        for values in vals:
            if values == 'consolidate_requisition_reference_picking':
                if vals.get('consolidate_requisition_reference_picking'):
                    for product_line_block in vals['move_ids_without_package']:
                        if product_line_block[2]:
                            block_requisicion=product_line_block[2]
                            block_requisicion['internal_requisition_picking']=True

        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    internal_requisition_picking = fields.Boolean("Picking de Requisición Interna")
    code_internal_requisition_picking = fields.Char("Códigos de Transferencias Consolidada")
