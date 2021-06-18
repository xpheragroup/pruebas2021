import datetime

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InternalPurchase(models.Model):

     _inherit = "purchase.order"

     @api.model
     def _default_picking_type(self):
          return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

     name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')

     requisicion_interna_purchase = fields.Boolean("Requisición Interna de Compra")
     requisicion_interna_production = fields.Boolean("Requisición Interna de Faltantes Fabricación", default=False, required=True)
     requisicion_interna_inventory = fields.Boolean("Requisición Interna de Requerimiento de Inventario", default=False, required=True)
     consolidate = fields.Boolean("Consolidar Requisiciones", default=False, required=True, copy=False)
     consolidate_requisition = fields.Many2many('purchase.order.line', string='Requisiciones', copy=False)
     consolidate_requisition_reference = fields.Char(string='Códigos de Requisiciónes Consolidadas', copy=False)
     mrp_production_ids = fields.Many2many('stock.move', string='Órdenes de Producción')
     stock_picking_ids = fields.Many2many('stock.move.line', string='Transferencias')
     show_internal_purchase = fields.Boolean("Ocultar Lista", default=False, required=True)
     state = fields.Selection([
        ('borrador compra', 'Borrador'),
        ('Borrador Requisición', 'Requisición'),
        ('modifica', 'Para Revisar'),
        ('revisa', 'Revisando'),
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('anular', 'Anulada')
     ], string='Status', readonly=True, index=True, copy=False, default='borrador compra', tracking=True)
     code_requisition = fields.Char(string='Código Requisición', copy=False)
     account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
     order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
     order_account_analytic_id = fields.Many2one('account.analytic.account', string='Centro de Costos')

     total_insumos = fields.Float(string='Total Insumos', compute='_total_insumos_unidades')
     total_unidades = fields.Float(string='Total Unidades', compute='_total_insumos_unidades')

     razon_anulacion = fields.Char(string='Razón de Anulación', copy=False)

     user_cre = fields.Many2one('res.users', string='Creó', required=False, copy=False)
     date_cre = fields.Datetime(string='Fecha creación', copy=False)
     user_apr = fields.Many2one('res.users', string='Aprobó', required=False, copy=False)
     date_apr = fields.Datetime(string='Fecha aprobó', copy=False)
     user_mod = fields.Many2one('res.users', string='Modificó', required=False, copy=False)
     date_mod = fields.Datetime(string='Fecha modificación', copy=False)
     user_anu = fields.Many2one('res.users', string='Anuló', required=False, copy=False)
     date_anu = fields.Datetime(string='Fecha anulación', copy=False)
     user_gen = fields.Many2one('res.users', string='Generó Reporte', required=False, copy=False)
     date_gen = fields.Datetime(string='Fecha generación último reporte', copy=False)

     user_sol = fields.Many2one('res.users', string='Quien Solicita', required=True)
     area_sol = fields.Many2one('hr.department', string='Área Solicitante')
     date_sol = fields.Datetime(string='Fecha de Solicitud', required=True)

     description = fields.Char(string='Descripción Requisición', copy=False)

     is_gift = fields.Boolean('Es regalo')
     picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
        help="This will determine operation type of incoming shipment")

     READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
     }

     partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
     identification_partner = fields.Char('N° Documento')
     codigo_solicitud_cotizacion = fields.Char(copy=False)

     @api.onchange('partner_id')
     def set_identification(self):
          if self.partner_id:
               numero_id = self.env['res.partner'].search([('id', '=', self.partner_id.id)], limit=1).vat
               self.identification_partner = numero_id

     def _default_partner_id(self):
          return self.env['res.partner'].search([('name', '=', 'Proveedor Default')], limit=1).id

     partner_id = fields.Many2one('res.partner', string='Proveedor', required=True, default=_default_partner_id , tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

     @api.onchange('order_account_analytic_id','order_line')
     def change_all_products_account_analytic_id(self):
          if self.order_account_analytic_id:
               for product in self.order_line:
                    product.account_analytic_id = self.order_account_analytic_id

     @api.onchange('order_line','product_qty')
     def _total_insumos_unidades(self):
          self.total_unidades = 0
          self.total_insumos = 0
          for product in self.order_line:
               self.total_unidades += product.product_qty
               self.total_insumos += 1

     @api.depends('purchase.order')
     def button_continue(self):
          for line in self.order_line:
               line.codigo_rint = self.code_requisition

          if self.requisicion_interna_purchase:
               self.state = 'Borrador Requisición'
               for purchase in self:
                    purchase.write({'user_cre': self.env.uid})
                    purchase.write({'date_cre': datetime.now()})
          if not self.requisicion_interna_purchase:
               self.state = 'draft'
               for purchase in self:
                    purchase.write({'user_apr': self.env.uid})
                    purchase.write({'date_apr': datetime.now()})
          return self.state
     
     @api.depends('purchase.order')
     def button_to_check(self):
          self.state = 'modifica'
          for purchase in self:
               purchase.write({'user_mod': self.env.uid})
               purchase.write({'date_mod': datetime.now()})
          return self.state

     @api.depends('purchase.order')
     def button_check(self):
          self.state = 'revisa'
          for purchase in self:
               purchase.write({'user_rev': self.env.uid})
               purchase.write({'date_rev': datetime.now()})
          return self.state

     @api.depends('purchase.order')
     def button_quote(self):
          self.codigo_solicitud_cotizacion = self.env['ir.sequence'].next_by_code('purchase.order_sdc') or '/'
          self.state = 'draft'
          for purchase in self:
               purchase.write({'user_apr': self.env.uid})
               purchase.write({'date_apr': datetime.now()})
          return self.state

     @api.depends('purchase.order')
     def button_void(self):
          if not self.razon_anulacion:
               raise UserError(_('Debes llenar la razón de anulación para continuar.'))
          for scrap in self:
               scrap.write({'user_anu': self.env.uid})
               scrap.write({'date_anu': datetime.now()})
          self.state = 'anular'
          return self.state

     @api.model
     def create(self, vals):        
          for purchase in self:
               purchase.write({'user_cre': self.env.uid})
               purchase.write({'date_cre': datetime.now()})
          company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
          
          if vals.get('order_line'):
               for account_analytic in vals['order_line']:
                    account_analytic_set = account_analytic[2]
                    account_analytic_get = account_analytic_set['account_analytic_id']
                    if not account_analytic_get:
                         raise UserError(_('Se debe establecer el Centro de Costo en las lineas de Productos.'))

          if vals.get('name', 'New') == 'New':
               seq_date = None
               if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
               if vals.get('requisicion_interna_purchase'):                    
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code('internal.requisition', sequence_date=seq_date) or '/'
                    vals['code_requisition'] = vals['name']
               if vals.get('is_gift', False):
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.gift', sequence_date=seq_date) or '/'
               if not vals.get('requisicion_interna_purchase') and not vals.get('is_gift', False):
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                         'purchase.order_sdc', sequence_date=seq_date) or '/'
                    vals['codigo_solicitud_cotizacion'] = vals['name']
               
               for values in vals:
                    if values == 'consolidate_requisition_reference':
                         if vals['consolidate_requisition_reference']:
                              for product_line_block in vals['order_line']:
                                   block_requisicion=product_line_block[2]
                                   block_requisicion['block_requisicion_interna_purchase_line']=True
                                   
                              for product_line in vals['consolidate_requisition']:
                                   for id_line_order in product_line[2]:
                                        ref_requisition = self.env['purchase.order.line'].search([('id','=',id_line_order)],limit=1)
                                        ref_requisition.code_order_consolidate = vals['name']

          return super(InternalPurchase, self.with_context(company_id=company_id)).create(vals)
          

     def write(self, vals):

          res = super(InternalPurchase, self).write(vals)

          for values in vals:
               if values == 'consolidate_requisition_reference':
                    if vals.get('consolidate_requisition_reference'):
                         for product_line_block in vals['order_line']:
                              if product_line_block[2]:
                                   block_requisicion=product_line_block[2]
                                   block_requisicion['block_requisicion_interna_purchase_line']=True
     
          return res

     def button_confirm(self):

          if self.partner_id.name == 'Proveedor Default':
               raise UserError(_('Debes cambiar el Proveedor Default para continuar.'))
          for line in self.order_line:
               if (line.requisicion_interna_picking_line and self.requisicion_interna_purchase) or (line.requisicion_interna_purchase_line and self.requisicion_interna_purchase):
                    raise UserError(_('No puede continuar con una requisición que contenga un producto que ha sido transferido internamente o que ha sido involucrado en una orden de compra.'))
          
          if self.is_gift:
               if self.picking_type_id == self._default_picking_type():
                    view = self.env.ref('overwrite_purchase.button_confirm_form')
                    return {
                         'type': 'ir.actions.act_window',
                         'name': "Confirmar 'Entregar a'",
                         'res_model': 'overwrite_purchase.button.confirm',
                         'views': [(view.id, 'form')],
                         'target': 'new',
                         'context': {'purchase': self._origin.ids}
                    }
               else:
                    self.button_confirm_second_confirm()
          
          for order in self:
               if order.state not in ['draft', 'sent']:
                    continue
               order._add_supplier_to_product()
               # Deal with double validation process
               if order.company_id.po_double_validation == 'one_step'\
                         or (order.company_id.po_double_validation == 'two_step'\
                         and order.amount_total < self.env.company.currency_id._convert(
                              order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                         or order.user_has_groups('purchase.group_purchase_manager'):
                    order.button_approve()
               else:
                    order.write({'state': 'to approve'})

          return True

     def button_confirm_second_confirm(self):
          for order in self:
               if order.state not in ['draft', 'sent']:
                    continue
               order._add_supplier_to_product()
               order.write({'state': 'to approve', 'user_rev': self.env.uid,
                              'date_rev': datetime.now()})
          return True

     @api.onchange('consolidate_requisition')
     def consolidar_requisition(self):
          codes=[]
          for line in self.order_line:
               if line.code_requisition_line:
                    if line.code_requisition_line.split(", "):
                         for code_split in line.code_requisition_line.split(", "):
                              codes.append(code_split)
                    code=line.code_requisition_line
                    codes.append(code)

                    for code_last_consolidate_requisition in codes:
                         ref_requisition = self.env['purchase.order.line'].search([('code_requisition_line','=',code_last_consolidate_requisition),],limit=1)
                         ref_requisition.code_requisition_line = False
                         ref_requisition.code_order_consolidate = False

          self.order_line=None
          self.consolidate_requisition_reference=None
          list_names_reference=[]
          list_names_reference_char=""

          list_order_lines=[[]]
          consolidate_cuantity=0
          for product_line in self.consolidate_requisition._origin:
               if product_line.order_id.name[0:4] != 'RINT':
                    raise UserError(_('La referencia de la orden debe ser RINT.'))
               rint_line_id=product_line.order_id.name
               state_rint=self.env['purchase.order'].search([('name','=',rint_line_id)],limit=1).state
               if (state_rint != 'draft'):
                    raise UserError(_('La requisición interna debe haber sido aprobada y estar en estado de SOLICITUD DE COTIZACIÓN para poder selecionarla.'))
               if (product_line.code_order_consolidate_block) or (product_line.block_requisicion_interna_purchase_line):
                    raise UserError(_('La referencia de la orden ya ha sido consolidada en una orden de compra o transferencia interna.'))
               product_line.code_requisition_line=product_line.order_id.name + " " + product_line.product_id.name
               product_line._rint()
               list_names_reference.append(product_line.code_requisition_line)

               exist=False
               for consol_line in list_order_lines:
                    if consol_line:
                         if (consol_line[0] == product_line.product_id) and (consol_line[1] == product_line.account_analytic_id):
                              consol_line[2]+=product_line.product_qty
                              consol_line[5]+= ", " + product_line.code_requisition_line
                              exist=True
               if not exist:
                    list_order_lines[consolidate_cuantity].append(product_line.product_id)
                    list_order_lines[consolidate_cuantity].append(product_line.account_analytic_id)
                    list_order_lines[consolidate_cuantity].append(product_line.product_qty)
                    list_order_lines[consolidate_cuantity].append(product_line.product_uom)
                    list_order_lines[consolidate_cuantity].append(product_line.price_unit)
                    list_order_lines[consolidate_cuantity].append(product_line.code_requisition_line)
                    list_order_lines[consolidate_cuantity].append(product_line.date_planned)
                    list_order_lines[consolidate_cuantity].append(product_line.name)
                    list_order_lines.append([])
                    values={}
                    self.order_line += self.env['purchase.order.line'].new(values) 
                    consolidate_cuantity+=1
          position=0
          list_order_lines.pop()      
          for line_consol in self.order_line:
               line_consol.product_id=list_order_lines[position][0]
               line_consol.account_analytic_id=list_order_lines[position][1]
               line_consol.product_qty=list_order_lines[position][2]
               line_consol.product_uom=list_order_lines[position][3]
               line_consol.price_unit=list_order_lines[position][4]
               line_consol.code_requisition_line=list_order_lines[position][5]
               line_consol.date_planned=list_order_lines[position][6]
               line_consol.name=list_order_lines[position][7]
               line_consol.block_requisicion_interna_purchase_line=False
               position+=1

          punto=1
          coma=len(list_names_reference)
          for ref in list_names_reference:
               list_names_reference_char +=ref
               if punto == coma:
                    list_names_reference_char +=". "
               else:
                    list_names_reference_char +=", "
               punto+=1
          self.consolidate_requisition_reference=list_names_reference_char

          if self.name != 'New':
               for product_line in self.consolidate_requisition:
                    id_line_order=product_line._origin.id
                    ref_requisition = self.env['purchase.order.line'].search([('id','=',id_line_order)],limit=1)
                    ref_requisition.code_order_consolidate = self.name
     
     @api.onchange('requisicion_interna_purchase','order_line')
     def get_standard_price(self):
          if not self.codigo_solicitud_cotizacion:
               if self.requisicion_interna_purchase:
                    for line in self.order_line:
                         name=line.product_id.name
                         ref_int=line.product_id.default_code
                         line.price_unit=self.env['product.template'].search([('name','=',name),('default_code','=',ref_int)],limit=1).standard_price

     @api.model
     def _get_picking_type(self, company_id):
          picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
          if not picking_type:
               picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
          return picking_type[:1]

     def set_user_gen(self):
          for purchase in self:
               purchase.write({'user_gen': self.env.uid})
               purchase.write({'date_gen': datetime.now()})

class PurchaseOrderLine(models.Model):
     _inherit = 'purchase.order.line'

     order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')
     requisicion_interna_purchase_line = fields.Boolean("Linea de Requisición Interna de Compra", compute='_rint', copy=False)
     block_requisicion_interna_purchase_line = fields.Boolean("Bloquear de Requisición Interna de Compra", default=False, compute='_block_origin_picking', copy=False)
     
     code_requisition_line = fields.Char(string='Código Requisición Linea', copy=False)
     code_order_consolidate = fields.Char(string='Código de Orden Consolidada', copy=False)
     code_order_consolidate_block = fields.Boolean("Check Block Origin", default=False, compute='_block_origin', copy=False)
     
     requisicion_interna_picking_line = fields.Boolean("Picking de Requisición Interna de Compra", compute='_rint_picking', copy=False)
     code_picking_requisition_line = fields.Char(string='Código Requisición Picking', copy=False)
     code_order_consolidate_picking = fields.Char(string='Código de Transferencia Consolidada', copy=False)

     codigo_rint = fields.Char(string='Código de Requisición Interna', copy=False)

     @api.onchange('code_order_consolidate')
     def _block_origin(self):
          for line in self:
               if not line.code_order_consolidate:
                    line.code_order_consolidate_block=False
               else:
                    line.code_order_consolidate_block=True

     @api.onchange('code_order_consolidate_picking')
     def _block_origin_picking(self):
          for line in self:
               if not line.code_order_consolidate_picking:
                    line.block_requisicion_interna_purchase_line=False
               else:
                    line.block_requisicion_interna_purchase_line=True

     @api.onchange('code_requisition_line')
     def _rint(self):
          for line in self:
               if line.code_requisition_line:
                    if line.code_requisition_line[0:4] == 'RINT':
                         line.requisicion_interna_purchase_line = True
                    else:
                         line.requisicion_interna_purchase_line = False
               else:
                    line.requisicion_interna_purchase_line = False
          return line.requisicion_interna_purchase_line            

     @api.onchange('code_picking_requisition_line')
     def _rint_picking(self):
          for line in self:
               if line.code_picking_requisition_line:
                    if line.code_picking_requisition_line[0:4] == 'RINT':
                         line.requisicion_interna_picking_line = True
                    else:
                         line.requisicion_interna_picking_line = False
               else:
                    line.requisicion_interna_picking_line = False
          return line.requisicion_interna_picking_line
