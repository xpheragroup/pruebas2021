import json
import datetime
from collections import defaultdict
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import date_utils, float_compare, float_round, float_is_zero

class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        if docids is None and data.get('docids', False):
            docids = data.get('docids')
        for bom_id in docids:
            bom = self.env['mrp.bom'].browse(bom_id)
            candidates = bom.product_id or bom.product_tmpl_id.product_variant_ids
            quantity = float(data.get('quantity', 1))
            for product_variant_id in candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
            if not candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    parent_id = fields.Many2one(comodel_name='mrp.production')
    children_ids = fields.One2many(comodel_name='mrp.production', inverse_name='parent_id')

    user_rev = fields.Many2one('res.users', string='Revisó', required=False)
    date_rev = fields.Datetime(string='Fecha revisó')
    user_apr = fields.Many2one('res.users', string='Aprobó', required=False)
    date_apr = fields.Datetime(string='Fecha aprobó')
    user_con = fields.Many2one('res.users', string='Confirmó', required=False)
    date_con = fields.Datetime(string='Fecha confirmó')
    user_ter = fields.Many2one('res.users', string='Terminó', required=False)
    date_ter = fields.Datetime(string='Fecha terminó')

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

    def to_draft(self):
        self._check_company()
        for mrp in self:
            mrp.write({'state': 'draft'})
            (mrp.move_raw_ids | mrp.move_finished_ids).to_draft_production_stock_move()
            mrp.write({'user_rev': False})
            mrp.write({'user_apr': False})
            mrp.write({'date_rev': False})
            mrp.write({'date_apr': False})
        return True
    
    def to_review(self):
        self._check_company()
        for mrp in self:
            mrp.write({'state': 'review'})
            mrp.write({'user_rev': self.env.uid})
            mrp.write({'date_rev': datetime.datetime.now()})
        return True
    
    def to_approv(self):
        self._check_company()
        for mrp in self:
            mrp.write({'state': 'approv'})
            mrp.write({'user_apr': self.env.uid})
            mrp.write({'date_apr': datetime.datetime.now()})
        return True
    
    def action_confirm(self):
        self._check_company()
        for mrp in self:
            mrp.write({'date_con': datetime.datetime.now()})
        for production in self:
            production.write({'user_con': self.env.uid})
            if not production.move_raw_ids:
                raise UserError(_("Add some materials to consume before marking this MO as to do."))
            for move_raw in production.move_raw_ids:
                move_raw.write({
                    'unit_factor': move_raw.product_uom_qty / production.product_qty,
                })
            production._generate_finished_moves()
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids)._action_confirm()
            for picking in self.env['stock.picking'].search([['origin', '=', production.name]]):
                if picking.location_dest_id and picking.location_dest_id.name and 'Pre-Producción' in picking.location_dest_id.name:
                    picking.action_assign() # Doing action assign on created stock picking
        return True

    def action_print_bom(self):
        data = dict(quantity=self.product_qty, docids=[self.bom_id.id], no_price=True, report_type='bom_structure')
        report = self.env.ref('mrp.action_report_bom_structure').with_context(discard_logo_check=True)
        report.name = 'Estructura de materiales - {}'.format(self.name)
        return report.report_action(self.bom_id, data)
        
    @api.model
    def create(self, values):
        if values.get('origin', False):
            parent = self.env['mrp.production'].search([['name', '=', values['origin']]])
            if parent:
                prods = self.env['mrp.production'].search([['name', 'like', values['origin'] + '.']])
                if len(prods) == 0:
                    index = '0'
                else:
                    index = max(list(map(lambda prod: prod.name.split('.')[-1], prods)))
                values['name'] = parent.name + '.' + str(int(index) + 1)
                values['parent_id'] = parent.id
        
        if not values.get('name', False) or values['name'] == _('New'):
            picking_type_id = values.get('picking_type_id') or self._get_default_picking_type()
            picking_type_id = self.env['stock.picking.type'].browse(picking_type_id)
            if picking_type_id:
                values['name'] = picking_type_id.sequence_id.next_by_id()
            else:
                values['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
        if not values.get('procurement_group_id'):
            procurement_group_vals = self._prepare_procurement_group_vals(values)
            values['procurement_group_id'] = self.env["procurement.group"].create(procurement_group_vals).id
        production = super(MrpProduction, self).create(values)
        
        production.move_raw_ids.write({
            'group_id': production.procurement_group_id.id,
            'reference': production.name,  # set reference when MO name is different than 'New'
        })
        # Trigger move_raw creation when importing a file
        if 'import_file' in self.env.context:
            production._onchange_move_raw()
        return production

class MrpBomLineOver(models.Model):
    _inherit = 'mrp.bom.line'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id
    
    product_qty_display = fields.Float('Cantidad', default=1.0, digits='Unit of Measure', required=False)
    product_uom_id_display = fields.Many2one(
        'uom.uom', 'Unidad de medida',
        default=_get_default_product_uom_id, required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'product_id' in values and 'product_uom_id' not in values:
                values['product_uom_id'] = self.env['product.product'].browse(values['product_id']).uom_id.id
        mrp_bom_line = super(MrpBomLineOver, self).create(vals_list)
        mrp_bom_line.onchange_product_uom_id_display()
        mrp_bom_line.onchange_product_qty_display()
        return mrp_bom_line

    @api.onchange('product_uom_id_display')
    def onchange_product_uom_id_display(self):
        for mbl in self:
            res = {}
            if not mbl.product_uom_id_display or not mbl.product_id:
                return res
            if mbl.product_uom_id_display.category_id != mbl.product_id.uom_id.category_id:
                mbl.product_uom_id_display = self.product_id.uom_id.id
                res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
        return res

    @api.onchange('product_id')
    def onchange_product_id_display(self):
        for mbl in self:
            if mbl.product_id:
                mbl.product_uom_id_display = mbl.product_id.uom_id.id

    @api.onchange('product_qty_display', 'product_uom_id_display')
    def onchange_product_qty_display(self):
        for mbl in self:
            if mbl.product_qty_display and mbl.product_uom_id_display:
                mbl.product_qty = mbl.product_qty_display * mbl.product_uom_id_display.factor_inv * mbl.product_id.uom_id.factor

class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    def do_produce(self):
        """ Save the current wizard and go back to the MO. """
        self.ensure_one()
        self._record_production()
        self._check_company()
        for mrp in self.production_id:
            mrp.write({'user_ter': self.env.uid})
            mrp.write({'date_ter': datetime.datetime.now()})
        return {'type': 'ir.actions.act_window_close'}