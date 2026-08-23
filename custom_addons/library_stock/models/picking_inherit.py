from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    loan_id = fields.Many2one('library.loan', string='Referensi Peminjaman', readonly=True)