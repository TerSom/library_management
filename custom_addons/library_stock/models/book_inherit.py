from odoo import models, fields

class LibraryBook(models.Model):
    _inherit = 'library.book'

    product_id = fields.Many2one('product.product', string='Link ke Produk Gudang')