from odoo import models


class button_confirm(models.TransientModel):
    _name = "overwrite_accounting.button.confirm"

    def button_confirm(self):
        query = [['id', '=', self._context['payment']]]
        payment = self.env['account.payment'].search(query)
        payment.post_confirmed()
        return {
            'type': 'ir.actions.act_window_close'
        }
