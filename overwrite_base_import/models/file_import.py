from odoo import api, fields, models

class file_import(models.Model):

    _name = 'overwrite_base_import.file_import'
    _description = 'Uploaded file information'

    file_name = fields.Char(
        string='Nombre del archivo', 
        index=True, 
        readonly=True
    )

    file_hash = fields.Char(
        string='Valor hash del archivo', 
        help='Valor hash asignado para el contenido del archivo',
        index=True,
        readonly=True
    )

    file = fields.Binary(
        string='Archivo cargado', 
        help='Archivo binario cargado al sistema (no base64)', 
        attachment=True,
        readonly=True # Blockeed?
    )
    
    model = fields.Char(
        string='Modelo objetivo',
        help='Modelo en base de datos afectado',
        readonly=True
    )
