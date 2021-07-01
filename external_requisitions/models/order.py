

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class InternalOrder(models.Model):

     _inherit = "sale.order"

     analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        readonly=True, copy=True, check_company=True,  # Unrequired company
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.")
     partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
     invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", readonly=True, copy=False, search="_search_invoice_ids")
     order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
     invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced', readonly=True)

     automatic_confirm = fields.Boolean("Confirmación Automatica", copy=False)
     date_confirm = fields.Datetime("Fecha y hora confirmación automática", copy=False)

     @api.onchange('partner_shipping_id')
     def set_analytic_account(self):
          if self.partner_shipping_id:
               if self.env['account.analytic.account'].search([('partner_id.id','=',self.partner_shipping_id.id)],limit=1):
                    self.analytic_account_id = self.env['account.analytic.account'].search([('partner_id.id','=',self.partner_shipping_id.id)],limit=1)
               else:
                    self.analytic_account_id = None

     @api.onchange('automatic_confirm')
     def reset_date_confirm(self):
          if not self.automatic_confirm:
               self.date_confirm = False

     def action_confirm(self):
          if self.partner_shipping_id:
               if self.date_order.date() >= self.partner_shipping_id.actual_date_end:
                    while self.date_order.date() >= self.partner_shipping_id.actual_date_end:
                         self.partner_shipping_id.periodos_transcurridos += 1
                         self.partner_shipping_id.ordenes = None

               gasto_adicional = self.partner_shipping_id.gasto_periodo + (self.partner_shipping_id.last_approved_order - self.partner_shipping_id.last_invoiced_order) + self.amount_total
               if self.partner_shipping_id.presupuesto < gasto_adicional:
                    raise UserError(_('El presupuesto del cliente ' + self.partner_shipping_id.name + ' es de $' + str(self.partner_shipping_id.presupuesto) + ' por ' + self.partner_shipping_id.periodicidad + ', con la '
                                        'requisición actual tendría un gasto en el periodo de $' + str(gasto_adicional) + '.'))
               
               for line in self.order_line:
                    self.partner_shipping_id.ordenes += line
          
          if self._get_forbidden_state_confirm() & set(self.mapped('state')):
               raise UserError(_(
                    'No está permitido confirmar un pedido en los siguientes estados: %s'
               ) % (', '.join(self._get_forbidden_state_confirm())))

          for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
               order.message_subscribe([order.partner_id.id])
          self.write({
               'state': 'sale',
               'date_order': fields.Datetime.now()
          })

          # Context key 'default_name' is sometimes propagated up to here.
          # We don't need it and it creates issues in the creation of linked records.
          context = self._context.copy()
          context.pop('default_name', None)

          self.with_context(context)._action_confirm()
          if self.env.user.has_group('sale.group_auto_done_setting'):
               self.action_done()
          return True

     @api.depends('order_line.invoice_lines')
     def _get_invoiced(self):
          # The invoice_ids are obtained thanks to the invoice lines of the SO
          # lines, and we also search for possible refunds created directly from
          # existing invoices. This is necessary since such a refund is not
          # directly linked to the SO.
          for order in self:
               invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
               order.invoice_ids = invoices
               order.invoice_count = len(invoices)