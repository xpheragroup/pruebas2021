from odoo import models, fields


# Import float compare credit note
from openerp.tools.translate import _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo import api, fields, models
from odoo.tools import float_compare
from re import search
import datetime


# The original definition is done in account/models/account_move.py !

class AccountMove(models.Model):
    _inherit = "account.move"


    date_order = fields.Datetime(
        'Order Date', copy=False, help="Fecha de la orden de compra.")
    register_date = fields.Datetime(
        'Fecha de registro', copy=False, help="Fecha del registro de compra.", readonly=True)

    def get_taxes(self):
        taxes = {}
        for line in self.invoice_line_ids:
            for tax in line.tax_ids:
                if taxes.get(tax.name) is None:
                    taxes[tax.name] = line.price_unit * \
                        tax.amount * line.quantity / 100
                else:
                    taxes[tax.name] += line.price_unit * \
                        tax.amount * line.quantity / 100
        return [(k, v) for k, v in taxes.items()]

    def action_post(self):
        super(AccountMove, self).action_post()
        for account_move in self:
            account_move.write({'register_date': datetime.datetime.now()})




# Avoid rebilling greater than the invoice value

class CreditNote(models.Model):
    _inherit = 'account.move'

    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
        compute='_compute_amount',
        inverse='_inverse_amount_total')
    ref = fields.Char(string='Reference', copy=False)
    name = fields.Char(string='Number', required=True, readonly=True, copy=False, default='/')
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')],
        string='Payment', store=True, readonly=True, copy=False, tracking=True,
        compute='_compute_amount')

    def action_invoice_register_payment(self):

        credit_note_paid = 'Reversión de: '+self.name
        state_credit_note = self.env['account.move'].search([('ref','=',credit_note_paid)],limit=1)
        if state_credit_note.invoice_payment_state == 'paid':
            raise UserError(_("Ya se pagó una nota credito para esta factura."))
        return self.env['account.payment']\
            .with_context(active_ids=self.ids, active_model='account.move', active_id=self.id)\
            .action_register_payment()

    @api.depends('amount_total')
    def action_post(self):

        if self.ref:
            if self.ref.find('Reversión de: ') != -1:
                reversal_of = self.ref[14:]
                limit_credit_note = self.env['account.move'].search([('name','=',reversal_of)])
                if self.amount_total > limit_credit_note.amount_total:
                    raise UserError(_("El valor de la nota credito no puede ser mayor al valor de la factura."))
        if self.filtered(lambda x: x.journal_id.post_at == 'bank_rec').mapped('line_ids.payment_id').filtered(lambda x: x.state != 'reconciled'):
            raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
        if self.env.context.get('default_type'):
            context = dict(self.env.context)
            del context['default_type']
            self = self.with_context(context)


        # super(AccountMove, self).action_post()
        for account_move in self:
            account_move.write({'register_date': datetime.datetime.now()})

        return self.post()


