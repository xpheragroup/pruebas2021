from odoo import api, fields, models
import json

import logging
from io import BytesIO, StringIO
import csv
import io
import xlwt
import base64

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug("Can not import xlsxwriter`.")


class BomRegister(models.Model):
    _name = 'overwrite_mrp.bom_register'
    _description = 'A register of material list'
    # _inherit = 'report.report_xlsx.abstract'
    _rec_name = 'name_menu'

    boms_id = fields.Many2many(
        string='Lista',
        comodel_name='mrp.bom'
    )

    name_menu = fields.Char(String='Nombre Menú', index=True)

    def add_product(data, bom, total):
        """Añade los datos relevantes de un producto al diccionario 'data'.

        Parametros:
        data: dict      -- Diccionario de datos
        bom: mrp.bom    -- Lista de materiales de la que proviene el producto
        total:int       -- Cantidad total de veces que se repetira la lista

        """

        warehouse = bom.bom_id.picking_type_id[0].warehouse_id[0]
        warehouse_availible = warehouse.lot_stock_id[0].quant_ids

        warehouse_availible = list(filter(lambda q: q.product_id == bom.product_id, warehouse_availible))
        availible_qty = sum(q.quantity for q in warehouse_availible)

        reserved = sum(q.reserved_quantity for q in warehouse_availible)

        if bom.product_id.id in data:
            data[bom.product_id.id]['qty'] += bom.product_qty * total
            data[bom.product_id.id]['availible_qty'] = availible_qty
            data[bom.product_id.id]['reserved'] = reserved
            data[bom.product_id.id]['warehouse'] = warehouse.name

        else:
            data[bom.product_id.id] = {
                'product': bom.product_id,
                'availible_qty': availible_qty,
                'reserved': reserved,
                'warehouse': warehouse.name,
                'qty': bom.product_qty * total,
                'uom': bom.product_uom_id
            }

    ##TODO: Para la cantidad reservada recorrer los stock_moves de las listas (sacar asi los productos?)
    def get_all_products(self):
        """Extrae toda la información de los productos relacionados en un BomRegister.

        La información aqui extraida está destinada a ser usada en el informe de Necesidad de compra

        """
        boms = []
        products = {}
        for bom in self.boms_id:
            boms.append(bom)
            for child_bom in bom.bom_line_ids:
                for inner_bom in child_bom.child_line_ids:
                    BomRegister.add_product(products, inner_bom, bom.total)

                if len(child_bom.child_line_ids) == 0:
                    BomRegister.add_product(products, child_bom, bom.total)

        data = {'material_lists': boms, 'products': products}
        # print(data)
        return data

    def action_generate_xlxs_ex(self):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('Expenses01.xlsx')
        worksheet = workbook.add_worksheet()

        # Some data we want to write to the worksheet.
        expenses = (
            ['Rent', 1000],
            ['Gas', 100],
            ['Food', 300],
            ['Gym', 50],
        )

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        for item, cost in (expenses):
            worksheet.write(row, col, item)
            worksheet.write(row, col + 1, cost)
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total')
        worksheet.write(row, 1, '=SUM(B1:B4)')

        workbook.close()

    def action_generate_xlxs(self):
        xlsx_data = io.BytesIO()
        csv_data = io.StringIO()  # on Python 2.x use `io.BytesIO()`

        # XLSX part
        workbook = xlsxwriter.Workbook(xlsx_data, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # CSV part
        csv_writer = csv.writer(csv_data)

        # Some data we want to write to the worksheet.
        expenses = (['OriginalURL', 'NormalizedURL', 'Response', 'DuplicateOf',
                     'SourceId', 'RelatedSources'],)

        for row, data in enumerate(expenses):
            # XSLX part
            worksheet.write_row(row, 0, data)  # if needed, add an offset to the row/column

            # CSV part
            csv_writer.writerow(data)

        workbook.close()

    def action_generate_xlxs_ex2(self):
        workbook = xlsxwriter.Workbook('hello.xlsx')
        worksheet = workbook.add_worksheet()

        worksheet.write('A1', 'Hello world')

        workbook.close()

    def action_generate_xlxs_ex4(self):
        workbook = xlsxwriter.Workbook('protection.xlsx')
        worksheet = workbook.add_worksheet()

        # Create some cell formats with protection properties.
        unlocked = workbook.add_format({'locked': False})
        hidden = workbook.add_format({'hidden': True})

        # Format the columns to make the text more visible.
        worksheet.set_column('A:A', 40)

        # Turn worksheet protection on.
        worksheet.protect()

        # Write a locked, unlocked and hidden cell.
        worksheet.write('A1', 'Cell B1 is locked. It cannot be edited.')
        worksheet.write('A2', 'Cell B2 is unlocked. It can be edited.')
        worksheet.write('A3', "Cell B3 is hidden. The formula isn't visible.")

        worksheet.write_formula('B1', '=1+2')  # Locked by default.
        worksheet.write_formula('B2', '=1+2', unlocked)
        worksheet.write_formula('B3', '=1+2', hidden)

        workbook.close()

    def action_generate_xlxs_ex5(self):
        stream = io.StringIO()
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet(u'Sheet1')
        expenses = (['OriginalURL', 'NormalizedURL', 'Response', 'DuplicateOf',
                     'SourceId', 'RelatedSources'],)

        for row, data in enumerate(expenses):
            # XSLX part
            # worksheet.write_row(row, 0, data)
            sheet.write(row, 0, data)

        book.save(stream)
        # base64.encodestring(stream.getvalue())
        # self.nam

    def generate_excel_report(self):
        filename = 'filename.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('font: bold True, name Arial;')
        worksheet.write_merge(0, 1, 0, 3, 'your data that you want to show into excelsheet', style)
        fp = io.StringIO()
        workbook.save(fp)
        record_id = self.env['wizard.excel.report'].create({'excel_file': base64.encodestring(fp.getvalue()),
                                                            'file_name': filename}, )
        fp.close()
        return {'view_mode': 'form',
                'res_id': record_id,
                'res_model': 'wizard.excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new',
                }


class wizard_excel_report(models.Model):
    _name = "wizard.excel.report"
    excel_file = fields.Binary('excel file')
    file_name = fields.Char('Excel File', size=64)


### This model Should not exist
class BomGroup(models.Model):
    _name = 'overwrite_mrp.bom_group'
    _description = 'This model Should not exist'


class BomRegisterXlsx(models.AbstractModel):
    _name = 'report.overwrite_mrp.menu_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # print('lines: ', lines)
        # One sheet by partner
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 12, 'align': 'vcenter', })
        sheet = workbook.add_worksheet('Menús')
        sheet.write(0, 0, 'Menús', format1)
        sheet.write(1, 1, 'Producto', format11)
        sheet.write(1, 2, 'Centro de Costos', format1)
        sheet.write(1, 3, 'Ciclo', format11)
        sheet.write(1, 4, 'Cantidad', format11)
        sheet.write(1, 5, 'Repeticiones', format11)
        sheet.write(1, 6, 'Total', format11)

        index = 0
        for bom in lines.boms_id:
            sheet.write(2 + index, 1, bom.product_id.name, format2)
            sheet.write(2 + index, 2, bom.cost_center.name, format2)
            sheet.write(2 + index, 3, bom.cycle, format2)
            sheet.write(2 + index, 4, bom.quantity, format2)
            sheet.write(2 + index, 5, bom.repetitions, format2)
            sheet.write(2 + index, 6, bom.total, format2)

            index = index + 1


class BomRegisterProductsXlsx(models.AbstractModel):
    _name = 'report.overwrite_mrp.productos_menu_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # print('lines: ', lines)
        # One sheet by partner
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 12, 'align': 'vcenter', })
        sheet = workbook.add_worksheet('Menú ' + str(lines.name_menu))
        # DATA POR FILA
        sheet.write(0, 0, 'Productos', format1)
        sheet.write(1, 1, 'Almacén', format11)
        sheet.write(1, 2, 'Producto', format11)
        sheet.write(1, 3, 'Total Requerido', format11)
        sheet.write(1, 4, 'Reservado', format11)
        sheet.write(1, 5, 'Disponible', format11)
        sheet.write(1, 6, 'Por comprar', format11)
        sheet.write(1, 7, 'Unidades de Medida', format11)

        products = {}

        for bom in lines.boms_id:
            for child_bom in bom.bom_line_ids:
                for inner_bom in child_bom.child_line_ids:
                    BomRegister.add_product(products, inner_bom, bom.total)

                if len(child_bom.child_line_ids) == 0:
                    BomRegister.add_product(products, child_bom, bom.total)

        data = lines.get_all_products()

        index = 0
        for product in data['products']:
            sheet.write(2 + index, 1, data['products'][product]['warehouse'], format2)
            sheet.write(2 + index, 2, data['products'][product]['product'].name, format2)
            sheet.write(2 + index, 3, data['products'][product]['qty'], format2)
            sheet.write(2 + index, 4, data['products'][product]['reserved'], format2)
            sheet.write(2 + index, 5, data['products'][product]['availible_qty'], format2)
            sheet.write(2 + index, 6, max(0, data['products'][product]['qty'] - data['products'][product]['availible_qty']), format2)
            sheet.write(2 + index, 7, data['products'][product]['uom'].name, format2)
            index = index + 1