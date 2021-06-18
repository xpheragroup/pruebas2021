from odoo import models, fields, _

# The original definition is done in account/models/account.py !

class AccountJournal(models.Model):
    _inherit = "account.journal"        # Inherit class to make changes on account journal

    code = fields.Char(size=10)       

    def _prepare_liquidity_account(self, name, company, currency_id, type):
        '''
        This function prepares the value to use for the creation of the default debit and credit accounts of a
        liquidity journal (created through the wizard of generating COA from templates for example).

        :param name: name of the bank account
        :param company: company for which the wizard is running
        :param currency_id: ID of the currency in which is the bank account
        :param type: either 'cash' or 'bank'
        :return: mapping of field names and values
        :rtype: dict
        '''
        digits = 6
        acc = self.env['account.account'].search([('company_id', '=', company.id)], limit=1)
        if acc:
            digits = len(acc.code)
        # Seek the next available number for the account code
        if type == 'bank':
            account_code_prefix = company.bank_account_code_prefix or ''
        else:
            account_code_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''

        liquidity_type = self.env.ref('account.data_account_type_liquidity')

        digits = (len(account_code_prefix) + 2) or 6
        return {
                'name': name,
                'currency_id': currency_id or False,
                'code': self.env['account.account']._search_new_account_code(company, digits, account_code_prefix),
                'user_type_id': liquidity_type and liquidity_type.id or False,
                'company_id': company.id,
        }  # Short code is needed larger (size was 5, set 10)

class AccountAccount(models.Model):
    _inherit = "account.account"

    
    def _search_new_account_code(self, company, digits, prefix): 
        for num in range(1, 10000):
            new_code = str(prefix.ljust(digits - 1, '0')) + str(num)
            rec = self.search([('code', '=', new_code), ('company_id', '=', company.id)], limit=1)
            if not rec:
                return new_code
        raise UserError(_('Cannot generate an unused account code.'))


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"


    def _prepare_transfer_account_for_direct_creation(self, name, company):
        """ Prepare values to create a transfer account directly, based on the
        method _prepare_transfer_account_template().

        This is needed when dealing with installation of payment modules
        that requires the creation of their own transfer account.

        :param name:        The transfer account name.
        :param company:     The company owning this account.
        :return:            A dictionary of values to create a new account.account.
        """
        vals = self._prepare_transfer_account_template()
        digits = len(self.code_digits) + 2
        prefix = self.transfer_account_code_prefix or ''
        vals.update({
            'code': self.env['account.account']._search_new_account_code(company, digits, prefix),
            'name': name,
            'company_id': company.id,
        })
        del(vals['chart_template_id'])
        return vals

    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        journal_to_add = [{'name': _('Valoración de Inventarios'), 'type': 'general', 'code': 'STJ', 'favorite': False, 'sequence': 8}]
        return super(AccountChartTemplate, self).generate_journals(acc_template_ref=acc_template_ref, company=company, journals_dict=journal_to_add)


    def _create_bank_journals(self, company, acc_template_ref):
        '''
        This function creates bank journals and their account for each line
        data returned by the function _get_default_bank_journals_data.

        :param company: the company for which the wizard is running.
        :param acc_template_ref: the dictionary containing the mapping between the ids of account templates and the ids
            of the accounts that have been generated from them.
        '''
        self.ensure_one()
        bank_journals = self.env['account.journal']
        # Create the journals that will trigger the account.account creation
        for acc in self._get_default_bank_journals_data():
            bank_journals += self.env['account.journal'].create({
                'name': acc['acc_name'],
                'type': acc['account_type'],
                'company_id': company.id,
                'sequence': 10
            })

        return bank_journals

    def _get_default_bank_journals_data(self):
        """ Returns the data needed to create the default bank journals when
        installing this chart of accounts, in the form of a list of dictionaries.
        The allowed keys in these dictionaries are:
            - acc_name: string (mandatory)
            - account_type: 'cash' or 'bank' (mandatory)
            - currency_id (optional, only to be specified if != company.currency_id)
        """
        return [{'acc_name': _('Caja General'), 'account_type': 'cash'}, {'acc_name': _('Banco'), 'account_type': 'bank'}]
        #return [{'acc_name': _('Banco'), 'account_type': 'bank'}]

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        def _get_default_account(journal_vals, type='debit'):
            # Get the default accounts
            default_account = False
            if journal['type'] == 'sale':
                default_account = acc_template_ref.get(self.property_account_income_categ_id.id)
            elif journal['type'] == 'purchase':
                default_account = acc_template_ref.get(self.property_account_expense_categ_id.id)
            elif journal['type'] == 'general' and journal['code'] == _('EXCH'):
                if type=='credit':
                    default_account = acc_template_ref.get(self.income_currency_exchange_account_id.id)
                else:
                    default_account = acc_template_ref.get(self.expense_currency_exchange_account_id.id)
            return default_account

        journals = [{'name': _('Facturas de Clientes'), 'type': 'sale', 'code': _('INV'), 'favorite': True, 'color': 11, 'sequence': 5},
                    {'name': _('Facturas de Proveedores'), 'type': 'purchase', 'code': _('BILL'), 'favorite': True, 'color': 11, 'sequence': 6},
                    {'name': _('Operaciones Misceláneas'), 'type': 'general', 'code': _('MISC'), 'favorite': True, 'sequence': 7},
                    {'name': _('Diferencia de Cambio'), 'type': 'general', 'code': _('EXCH'), 'favorite': False, 'sequence': 9},
                    {'name': _('Impuestos en Efectivo'), 'type': 'general', 'code': _('CABA'), 'favorite': False, 'sequence': 10}]
        if journals_dict != None:
            journals.extend(journals_dict)

        self.ensure_one()
        journal_data = []
        for journal in journals:
            vals = {
                'type': journal['type'],
                'name': journal['name'],
                'code': journal['code'],
                'company_id': company.id,
                'default_credit_account_id': _get_default_account(journal, 'credit'),
                'default_debit_account_id': _get_default_account(journal, 'debit'),
                'show_on_dashboard': journal['favorite'],
                'color': journal.get('color', False),
                'sequence': journal['sequence']
            }
            journal_data.append(vals)
        return journal_data