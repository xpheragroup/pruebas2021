# No member error in this file are for inheritance in Odoo!
# pylint: disable=E1101

from odoo import models, _
from odoo.exceptions import ValidationError, UserError

# The original definition is done in account_report_cash_basis/models/account_report.py !


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    MOST_SORT_PRIO = 0
    LEAST_SORT_PRIO = 99

    # Create codes path in the hierarchy based on account.
    def get_account_codes(self, account):
        # A code is tuple(sort priority, actual code)
        codes = []
        if account.group_id:
            group = account.group_id
            while group:
                code = '%s %s' % (group.code_prefix or '', group.name)
                codes.append((self.MOST_SORT_PRIO, code))
                group = group.parent_id
        else:
            codes.append((self.MOST_SORT_PRIO, account.code[:4]))
            codes.append((self.MOST_SORT_PRIO, account.code[:2]))
            codes.append((self.MOST_SORT_PRIO, account.code[:1]))
        return list(reversed(codes))

    def _init_filter_multi_company(self, options, previous_options=None):
        if not self.filter_multi_company:
            return

        companies = self.env.user.company_ids
        if len(companies) > 1:
            allowed_company_ids = self._context.get(
                'allowed_company_ids', self.env.company.ids)
            options['multi_company'] = [
                {'id': c.id, 'name': c.name, 'selected': c.id in allowed_company_ids, 'vat': c.vat} for c in companies
            ]
