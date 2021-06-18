from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    name = fields.Char(default='Nuevo')
    is_gift = fields.Boolean('Es regalo')

    user_rev = fields.Many2one('res.users', string='Revisó', required=False)
    date_rev = fields.Datetime(string='Fecha revisó')

    codigo_solicitud_cotizacion = fields.Char()

    order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
        help="This will determine operation type of incoming shipment")

    @ api.onchange('order_line','picking_type_id')
    def variante_producto(self):
        if self.picking_type_id:
            for product in self.order_line:
                location = self.picking_type_id.warehouse_id.name
                product_order = product.product_id.warehouse_id.name
                if (product.product_id.warehouse_id or product.product_id.warehouse_id):
                    if (location != product_order):
                        raise UserError(_('El almacén del producto o variante de producto no corresponde con el almacén de entrega. '
                        'Seleccione la variante de producto correspondiente, asigne el almacén adecuado al producto / variante del producto '
                        'o seleccione el almacen correcto de entrega.'))

    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env.ref('overwrite_purchase.report_purchase_quotation').report_action(self)


    def button_approve(self, force=False):
        if not self.is_gift:
            self.write(
                {'name': self.env['ir.sequence'].next_by_code('purchase.order') or '/'})
        return super(PurchaseOrder, self).button_approve(force=force)

    def get_taxes(self):
        taxes = {}
        for line in self.order_line:
            for tax in line.taxes_id:
                if taxes.get(tax.name) is None:
                    taxes[tax.name] = line.price_unit * \
                        (100 - line.discount)/100 * \
                        tax.amount * line.product_qty / 100
                else:
                    taxes[tax.name] += line.price_unit * \
                        (100 - line.discount)/100 * \
                        tax.amount * line.product_qty / 100
        print([(k, v) for k, v in taxes.items()])
        return [(k, v) for k, v in taxes.items()]

    def button_confirm(self):
        if self.picking_type_id == self._default_picking_type():
            view = self.env.ref('overwrite_purchase.button_confirm_form')
            return {
                'type': 'ir.actions.act_window',
                'name': "Confirmar 'Entregar a'",
                'res_model': 'overwrite_purchase.button.confirm',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {'purchase': self.id}
            }
        else:
            self.button_confirm_second_confirm()

    def button_confirm_second_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            order.write({'state': 'to approve', 'user_rev': self.env.uid,
                         'date_rev': datetime.now()})
        return True

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        # Invoice_ids may be filtered depending on the user. To ensure we get all
        # invoices related to the purchase order, we read them in sudo to fill the
        # cache.
        self.sudo()._read(['invoice_ids'])
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + \
                str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        result['context']['default_date_order'] = self.date_order
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or vals.get('name', 'Nuevo') == 'Nuevo':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date_order']))
            if vals.get('is_gift', False):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.gift', sequence_date=seq_date) or '/'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.order_sdc', sequence_date=seq_date) or '/'
            vals['codigo_solicitud_cotizacion'] = vals['name']
        return super(PurchaseOrder, self).create(vals)
