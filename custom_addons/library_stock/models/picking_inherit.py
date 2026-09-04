from odoo import models, fields
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    loan_id = fields.Many2one('library.loan', string='Referensi Peminjaman', readonly=True)

    def button_validate(self):
        for picking in self:
            # Validasi khusus surat jalan pengembalian buku (incoming) dari loan
            if picking.picking_type_code == 'incoming' and picking.loan_id:
                loan = picking.loan_id
                # Cek jika ada invoice/bill denda yang belum lunas
                if hasattr(loan, 'invoice_id') and loan.invoice_id:
                    payment_state = loan.invoice_id.payment_state
                    if payment_state not in ('paid', 'in_payment'):
                        raise UserError(
                            f"Surat jalan pengembalian ({picking.name}) tidak dapat divalidasi! "
                            f"Member memiliki tagihan denda ({loan.invoice_id.name}) dengan status pembayaran '{payment_state}'. "
                            f"Tagihan harus berstatus Lunas (Paid) terlebih dahulu."
                        )
                elif loan.total_late_fee > 0:
                    raise UserError(
                        f"Surat jalan pengembalian ({picking.name}) tidak dapat divalidasi! "
                        f"Transaksi peminjaman {loan.name} memiliki denda Rp {loan.total_late_fee:,.0f} "
                        f"yang belum dibuatkan invoice atau belum dibayar."
                    )

        res = super().button_validate()

        for picking in self:
            if picking.loan_id:
                tipe = "Pengeluaran (Pinjam)" if picking.picking_type_code == 'outgoing' else "Penerimaan Kembali (Gudang)"
                picking.loan_id.message_post(
                    body=f"Surat Jalan Gudang Selesai ({tipe}): Dokumen {picking.name} berhasil divalidasi (Done).",
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )

        return res

    def action_view_loan(self):
        self.ensure_one()
        return {
            'name': 'Peminjaman',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'form',
            'res_id': self.loan_id.id,
        }