from odoo import models


class button_confirm(models.TransientModel):
    _name = "overwrite_purchase.button.confirm"

    def button_confirm(self):
        query = [['id', '=', self._context['purchase']]]
        purchase_order = self.env['purchase.order'].search(query)
        purchase_order.button_confirm_second_confirm()
        return {
            'type': 'ir.actions.act_window_close'
        }
