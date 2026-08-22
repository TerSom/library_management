from odoo import fields,models,api,Command
from odoo.exceptions import UserError

class Libraryloan(models.Model):
    _inherit = 'library.loan'

    invoice_id = fields.Many2one('account.move', string='Invoice Denda' ,readonly=True)
    invoice_payment_state = fields.Selection(related='invoice_id.payment_state', string='Invoice Payment State', readonly=True)

    def action_create_invoice(self):
        self.ensure_one()

        if self.total_late_fee <= 0:
            raise UserError("Tidak ada denda yang perlu ditagihkan.")
        if self.invoice_id:
            raise UserError("Tagihan (Invoice) untuk dokumen ini sudah dibuat!")

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.member_id.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids' : [
                Command.create({
                    'name': f"Denda Keterlambatan Buku (Ref: {self.name})",
                    'quantity': 1,
                    'price_unit': self.total_late_fee,
                })
            ],
        }

        invoice = self.env['account.move'].create(invoice_vals)

        self.invoice_id = invoice.id

        return self.action_view_invoice()
    
    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError("Belum ada invoice yang terkait dengan record ini.")
        
        return {
            'name': 'Tagihan Denda',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }
