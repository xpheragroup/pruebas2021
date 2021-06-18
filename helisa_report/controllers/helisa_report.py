import ast
import xlwt
import base64
from io import BytesIO
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition

INITIAL_ROW = 0
INCREMENT_ROW = 1
COLUMN_COUNT = 10
COLUMN_WIDTH = 7500
FILE_EXTENSION = '.xls'
DEFAULT_FILENAME = 'Helisa.xls'


class Binary(http.Controller):

    def _init_book(self):
        self.current_row = INITIAL_ROW
        self.book = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.book.add_sheet(u'Reporte')
        for i in range(COLUMN_COUNT):
            self.sheet.col(i).width = COLUMN_WIDTH

    def _finish_book(self):
        bytes_stream = BytesIO()
        self.book.save(bytes_stream)
        finished_book = bytes_stream.getvalue()
        bytes_stream.close()
        return finished_book

    def _next_row(self):
        self.current_row = self.current_row + INCREMENT_ROW

    def _add_row(self, array):
        for i in range(len(array)):
            self.sheet.write(self.current_row, i, str(array[i]))
        self._next_row()

    def _write_sheet(self, account_moves):
        header_row = ['DOCUMENTO', 'FECHA', 'NIT', 'VALOR', 'NATURALEZA',
                      'CENTRO DE COSTO', 'CUENTA', 'No DOCUMENTO', 'DETALLE']
        self._add_row(header_row)
        for account_move in account_moves:
            for invoice_line in account_move.invoice_line_ids:
                self._add_row([
                    'FC',
                    account_move.invoice_date or '',
                    account_move.partner_id.vat or '',
                    invoice_line.debit if invoice_line.debit > 0 else invoice_line.credit,
                    'D' if invoice_line.debit > 0 else 'C',
                    invoice_line.analytic_account_id.name or '',
                    invoice_line.account_id.code,
                    account_move.name,
                    invoice_line.name
                ])

    @http.route('/web/binary/helisa_report', type='http', auth="public")
    @serialize_exception
    def download_document(self, ids, filename=None, **kw):
        self._init_book()

        model = http.request.env['account.move']
        account_moves = model.browse(ast.literal_eval(ids))

        if account_moves:
            self._write_sheet(account_moves)
            filecontent = self._finish_book()
            if not filename:
                filename = DEFAULT_FILENAME
            if not FILE_EXTENSION in filename:
                filename += FILE_EXTENSION
            return request.make_response(
                filecontent,
                [('Content-Type', 'application/octet-bytes_stream'),
                 ('Content-Disposition', content_disposition(filename))
                 ])
        else:
            return request.not_found()
