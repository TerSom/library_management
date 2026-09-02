from . import models


def _post_init_hook(env):
    """Migrasi buku existing: buat product.template + set qty=10."""
    books = env['library.book'].search([('product_tmpl_id', '=', False)])
    if not books:
        return

    location = env.ref('stock.stock_location_stock')
    for book in books:
        product_tmpl = env['product.template'].create({
            'name': book.name,
            'type': 'consu',
            'is_storable': True,
        })
        book.product_tmpl_id = product_tmpl.id

        product = product_tmpl.product_variant_id
        if product:
            env['stock.quant'].sudo()._update_available_quantity(
                product, location, 10,
            )
