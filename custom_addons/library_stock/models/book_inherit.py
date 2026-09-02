from odoo import models, fields, api


class LibraryBook(models.Model):
    _inherit = 'library.book'
    _inherits = {'product.template': 'product_tmpl_id'}

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Produk Gudang',
        required=True,
        ondelete='cascade',
        auto_join=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        ProductTemplate = self.env['product.template']
        for vals in vals_list:
            if not vals.get('product_tmpl_id'):
                pt = ProductTemplate.create({
                    'name': vals.get('name', 'New Book'),
                    'type': 'consu',
                    'is_storable': True,
                })
                vals['product_tmpl_id'] = pt.id
        books = super().create(vals_list)
        books._set_initial_stock(10)
        return books

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals:
            for book in self:
                book.product_tmpl_id.name = book.name
        return res

    def _set_initial_stock(self, qty):
        """Set on-hand quantity di warehouse utama."""
        location = self.env.ref('stock.stock_location_stock')
        for book in self:
            product = book.product_tmpl_id.product_variant_id
            if product:
                self.env['stock.quant'].sudo()._update_available_quantity(
                    product, location, qty,
                )
