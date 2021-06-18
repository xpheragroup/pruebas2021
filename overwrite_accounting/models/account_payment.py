# No member error in this file are for inheritance in Odoo!
# pylint: disable=E1101

from odoo import models, fields, _
from odoo.exceptions import ValidationError, UserError

# The original definition is done in account_check_printing/models/account_payment.py !

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    consecutivo_de_caja = fields.Char(string='Consecutivo de caja')

    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices/bills to pay. In case of multiple
            documents, they need to be grouped by partner, bank, journal and
            currency.
        :return: The payment values as a dictionary.
        '''
        amount = self.env['account.payment']._compute_payment_amount(
            invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
        values = {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self._prepare_communication(invoices),
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': ('inbound' if amount > 0 else 'outbound'),
            'amount': abs(amount),
            'currency_id': invoices[0].currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
            'x_studio_consecutivo_de_caja': self.consecutivo_de_caja,
        }
        return values


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    def post(self):
        account_ids = tuple(ac for ac in [
            self.journal_id.default_debit_account_id.id, self.journal_id.default_credit_account_id.id] if ac)
        query = """SELECT sum(aml.balance) as sum FROM account_move_line aml
                    LEFT JOIN account_move move ON aml.move_id = move.id
                    WHERE aml.account_id in %%s 
                    AND move.date <= %%s AND move.state = 'posted';""" % ()
        self.env.cr.execute(
            query, (account_ids, fields.Date.context_today(self),))
        query_results = self.env.cr.dictfetchall()
        if query_results and query_results[0].get('sum') != None:
            account_sum = query_results[0].get('sum')
        else:
            account_sum = float('inf')
        payment_out = self.payment_type in ('transfer', 'outbound')
        balance_negative = account_sum - self.amount < 0
        if payment_out and balance_negative:
            raise UserError(
                'No es posible deducir el diario ya que tendría saldos negativos .')
        else:
            self.post_confirmed()

    def post_confirmed(self):
        AccountMove = self.env['account.move'].with_context(
            default_type='entry')
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(
                    _("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(
                    sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(
                        _("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(
                lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids')\
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
                    .reconcile()
            if rec.invoice_ids:
                for invoice in rec.invoice_ids:
                    # TODO: Define x_studio_consecutivos_de_caja as invoice model field
                    invoice.x_studio_consecutivos_de_caja = rec.x_studio_consecutivo_de_caja
        return True
