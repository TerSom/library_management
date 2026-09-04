from odoo import models, fields, api
from odoo.exceptions import UserError

class LibraryLoan(models.Model):
    _inherit = 'library.loan'

    picking_ids = fields.One2many('stock.picking', 'loan_id', string='Surat Jalan Gudang')
    
    picking_count = fields.Integer(compute='_compute_picking_count')

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for record in self:
            record.picking_count = len(record.picking_ids)

    def _create_stock_transfer(self, picking_type_code):
        """Fungsi rahasia pembuat Stock Picking otomatis"""
        self.ensure_one()
        
        if picking_type_code == 'outgoing':
            picking_type = self.env.ref('stock.picking_type_out')
            location_id = picking_type.default_location_src_id.id
            location_dest_id = self.member_id.partner_id.property_stock_customer.id
        else:

            picking_type = self.env.ref('stock.picking_type_in')
            location_id = self.member_id.partner_id.property_stock_customer.id
            location_dest_id = picking_type.default_location_dest_id.id

        picking = self.env['stock.picking'].create({
            'partner_id': self.member_id.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'loan_id': self.id,
            'origin': self.name, 
        })

        for line in self.loan_line_ids:
            product = line.book_id.product_tmpl_id.product_variant_id
            self.env['stock.move'].create({
                'name': line.book_id.name,
                'product_id': product.id,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'picking_id': picking.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            })
            
        picking.action_confirm()

    def action_confirm(self):
        res = super().action_confirm()
        for record in self:
            record._create_stock_transfer('outgoing')
        return res

    def action_return(self):
        for record in self:
            unvalidated_outgoing = record.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing' and p.state != 'done'
            )
            if unvalidated_outgoing:
                picking_names = ", ".join(unvalidated_outgoing.mapped('name'))
                raise UserError(
                    f"Buku belum bisa dikembalikan! Surat jalan pengeluaran ({picking_names}) "
                    f"harus divalidasi (status Done) terlebih dahulu oleh bagian gudang."
                )

        res = super().action_return()
        for record in self:
            record._create_stock_transfer('incoming')
        return res

    def action_view_pickings(self):
        """Membuka daftar Surat Jalan Gudang"""
        self.ensure_one()
        return {
            'name': 'Surat Jalan Gudang',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('loan_id', '=', self.id)],
        }