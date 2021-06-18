
from odoo import models, fields, api

class RequisitionReportXlsx(models.AbstractModel):
    _name = 'report.internal_requisitions.reporte_requisition_interna_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':10, 'align':'vcenter','bold':True})
        format2 = workbook.add_format({'font_size':10, 'align':'vcenter',})
        format3 = workbook.add_format({'font_size':10, 'align':'left','num_format': 'dd/mm/yy hh:mm'})
        sheet = workbook.add_worksheet('Requisición Interna')
        sheet.set_column(3,3,50)
        sheet.set_column(2,2,50)
        sheet.write(2,2,'Requisición',format1)
        sheet.write(2,3,lines.name,format2)
        sheet.write(3,2,'Descripción',format1)
        sheet.write(3,3,lines.description,format2)       
        sheet.write(4,2,'Creó',format1)
        sheet.write(4,3,lines.user_cre.name,format2)
        sheet.write(5,2,'Fecha Creación',format1)
        sheet.write(5,3,lines.date_cre,format3)
        sheet.write(6,2,'Aprobó',format1)
        sheet.write(6,3,lines.user_apr.name,format2)        
        sheet.write(7,2,'Fecha Aprobación',format1)
        sheet.write(7,3,lines.date_apr,format3)        
        sheet.write(9,2,'Producto',format1)
        sheet.write(9,3,'Centro de Costos',format1)
        sheet.write(9,4,'Cantidad',format1)        
        sheet.write(9,5,'UoM',format1)
        
        line=10
        for product_line in lines.order_line:
            sheet.write(line,2,product_line.name)
            sheet.write(line,3,"[" + product_line.account_analytic_id.code + "]" + product_line.account_analytic_id.name)
            sheet.write(line,4,product_line.product_qty)
            sheet.write(line,5,product_line.product_uom.name)
            line+=1
