from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    loan_id = fields.Many2one('library.loan', string='Referensi Peminjaman', readonly=True)

    def action_view_loan(self):
        self.ensure_one()
        return {
            'name': 'Peminjaman',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'form',
            'res_id': self.loan_id.id,
        }