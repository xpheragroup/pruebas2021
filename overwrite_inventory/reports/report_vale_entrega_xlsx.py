
from odoo import models, fields, api

class RequisitionReportXlsx(models.AbstractModel):
    _name = 'report.overwrite_inventory.report_vale_entrega_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':10, 'align':'vcenter','bold':True})
        format2 = workbook.add_format({'font_size':10, 'align':'vcenter',})
        format3 = workbook.add_format({'font_size':10, 'align':'left','num_format': 'dd/mm/yy hh:mm'})
        sheet = workbook.add_worksheet('Vale de Entrega')
        sheet.set_column(3,3,50)
        sheet.set_column(2,2,50)
        sheet.set_column(5,5,50)
        sheet.set_column(4,4,50)
        sheet.set_column(6,6,50)
        sheet.set_column(7,7,50)
        sheet.write(1,2,'Vale de Entrega',format1)
        sheet.write(1,3,lines.name,format2)
        sheet.write(3,2,'Información General',format1)
        sheet.write(4,2,'Nombre: ',format2)
        sheet.write(4,3,lines.company_id.partner_id.name,format2)
        sheet.write(5,2,'NIT: ',format2)
        sheet.write(5,3,lines.company_id.partner_id.vat,format2)
        sheet.write(6,2,'Dirección: ',format2)
        sheet.write(6,3,lines.company_id.partner_id.street,format2)
        sheet.write(7,2,'Ciudad: ',format2)
        sheet.write(7,3,lines.company_id.partner_id.city,format2)
        sheet.write(8,2,'Telefono: ',format2)
        sheet.write(8,3,lines.company_id.partner_id.phone,format2)
        sheet.write(9,2,'Móvil: ',format2)
        sheet.write(9,3,lines.company_id.partner_id.mobile,format2)
        sheet.write(10,2,'Correo Electronico: ',format2)
        sheet.write(10,3,lines.company_id.partner_id.email,format2)
        
        sheet.write(3,4,'Proveedor',format1)
        sheet.write(4,4,'Nombre: ',format2)
        sheet.write(4,5,lines.partner_id.name,format2)
        sheet.write(5,4,'NIT: ',format2)
        sheet.write(5,5,lines.partner_id.vat,format2)
        sheet.write(6,4,'Dirección: ',format2)
        sheet.write(6,5,lines.partner_id.street,format2)
        sheet.write(7,4,'Ciudad: ',format2)
        sheet.write(7,5,lines.partner_id.city,format2)
        sheet.write(8,4,'Telefono: ',format2)
        sheet.write(8,5,lines.partner_id.phone,format2)
        sheet.write(9,4,'Móvil: ',format2)
        sheet.write(9,5,lines.partner_id.mobile,format2)
        sheet.write(10,4,'Correo Electronico: ',format2)
        sheet.write(10,5,lines.partner_id.email,format2)

        sheet.write(12,2,'Fechas',format1)
        sheet.write(13,2,'Fecha de pedido: ',format2)
        sheet.write(13,3,lines.date,format3)
        sheet.write(14,2,'Fecha de recepción: ',format2)
        sheet.write(14,3,lines.scheduled_date,format3)
        sheet.write(15,2,'Documento Origen: ',format2)
        sheet.write(15,3,lines.origin_order,format2)

        sheet.write(12,4,'Almacén',format1)
        sheet.write(13,4,'Ubicación Destino: ',format2)
        sheet.write(13,5,lines.location_dest_id.complete_name,format2)
        
        sheet.write(17,2,'Detalle',format1)
        sheet.write(18,2,'Item',format1)
        sheet.write(18,3,'Producto',format1)
        sheet.write(18,4,'Cantidad',format1)
        sheet.write(18,5,'Unidad de Medida',format1)
        sheet.write(18,6,'Lote',format1)
        sheet.write(18,7,'Fecha de Vencimiento',format1)

        line=19
        for product_line in lines.move_line_ids:
            sheet.write(line,2,line-18)
            if product_line.move_id.description_picking != product_line.product_id.name:
                sheet.write(line,3,product_line.move_id.description_picking)
            else:
                sheet.write(line,3,product_line.product_id.name)
            sheet.write(line,4,product_line.qty_done)
            sheet.write(line,5,product_line.product_uom_id.name)
            if product_line.lot_name:
                sheet.write(line,6,product_line.lot_name)
                sheet.write(line,7,product_line.lot_name.x_studio_fecha_de_vencimiento_1,format3)
            elif product_line.lot_id.name:
                sheet.write(line,6,product_line.lot_id.name)
                sheet.write(line,7,product_line.lot_id.x_studio_fecha_de_vencimiento_1,format3)  
            line+=1

        sheet.write(line+1,2,'Trazabilidad',format1)
        sheet.write(line+2,2,'Realizado por:',format1)
        sheet.write(line+3,2,'Nombre: ',format2)
        sheet.write(line+3,3,lines.x_studio_quien_termina.name,format2)
        sheet.write(line+4,2,'Fecha y hora: ',format2)
        sheet.write(line+4,3,lines.x_studio_fecha_termin,format3)
        
        sheet.write(line+2,4,'Quien entrega/recibe:',format1)
        sheet.write(line+3,4,'Nombre: ',format2)
        sheet.write(line+3,5,'_______________________________',format2)
        sheet.write(line+4,4,'Cargo: ',format2)
        sheet.write(line+4,5,'_______________________________',format2)
        sheet.write(line+5,4,'Fecha: ',format2)
        sheet.write(line+5,5,'_______________________________',format2)
        sheet.write(line+6,4,'Hora: ',format2)
        sheet.write(line+6,5,'_______________________________',format2)