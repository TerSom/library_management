from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='No. Referensi', default='New', readonly=True)
    member_id = fields.Many2one('library.member', string='Member', required=True)
    date_borrow = fields.Date(string='Borrow Date', default=fields.Date.context_today)
    date_return_expected = fields.Date(string='Expected Return Date', required=True, tracking=True)
    loan_line_ids = fields.One2many('library.loan.line', 'loan_id', string='Loan Lines')
    total_late_fee = fields.Float(string='Total Late Fee', compute='_compute_total_late_fee', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
    ], string='Status', default='draft', tracking=True)

    @api.constrains('loan_line_ids')
    def _check_loan_lines(self):
        for record in self:
            if not record.loan_line_ids:
                raise ValidationError("Transaksi peminjaman harus memiliki setidaknya satu buku yang dipinjam.")

    @api.depends('loan_line_ids.late_fee')
    def _compute_total_late_fee(self):
        for record in self:
            record.total_late_fee = sum(line.late_fee for line in record.loan_line_ids)

    @api.onchange('date_borrow')
    def _onchange_date_borrow(self):
        for record in self:
            """Otomatis set tenggat waktu 7 hari dari tanggal pinjam"""
            if record.date_borrow:
                record.date_return_expected = record.date_borrow + timedelta(days=7)

    @api.constrains('date_return_expected','date_borrow')
    def _check_dates(self):
        for record in self:
            if record.date_return_expected and record.date_borrow:
                if record.date_return_expected <= record.date_borrow:
                    raise ValidationError("tanggal tanggat waktu tidak boleh lebih dari awal atau sama dari tanggal pinjaman")

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('library.loan.sequence') or "New"
            
        result = super().create(vals_list)
        return result
    
    @api.model
    def _cron_check_overdue_and_notify(self):
        today = fields.Date.today()
    
        domain = [
            ('state', '=', 'ongoing'),
            ('date_return_expected', '<', today)
        ]
        overdue_loans = self.search(domain)
        
        overdue_loans.loan_line_ids._compute_late_fee()
        
        _logger.info(f"Cron [Library Loan]: Ditemukan {len(overdue_loans)} transaksi terlambat.")
        
        ICP = self.env['ir.config_parameter'].sudo()
        waha_base_url = ICP.get_param('waha.url', 'http://127.0.0.1:3000')
        api_key = ICP.get_param('waha.api_key')
        waha_url = f"{waha_base_url}/api/sendText"
        waha_session = "default"

        for loan in overdue_loans:
            phone_number = loan.member_id.partner_id.mobile or loan.member_id.partner_id.phone

            if not phone_number:
                _logger.warning(f"Cron WAHA: Member {loan.member_id.name} (Ref: {loan.name}) tidak punya nomor HP.")
                continue
            
            phone_number = str(phone_number).replace("+", "").replace("-", "").replace(" ", "")
            chat_id = f"{phone_number}@c.us" 

            total_denda = sum(line.late_fee for line in loan.loan_line_ids if not line.date_return_actual)
            
            _logger.info(f"Debug: Loan {loan.name} - total_denda = {total_denda}")
            if total_denda <= 0:
                continue

            message = (
                f"Halo *{loan.member_id.partner_id.name}*,\n\n"
                f"Ini adalah pengingat otomatis dari Perpustakaan.\n"
                f"Transaksi Peminjaman Anda (*{loan.name}*) telah melewati batas waktu pengembalian pada *{loan.date_return_expected}*.\n\n"
                f"Daftar Buku Belum Kembali:\n"
            )
            
            for line in loan.loan_line_ids:
                if not line.date_return_actual:
                    message += f"- {line.book_id.name}\n"

            message += (
                f"\nEstimasi total denda berjalan Anda saat ini adalah: *Rp. {total_denda:,.0f}*.\n\n"
                f"Mohon segera mengembalikan buku untuk menghindari penambahan denda harian.\n"
                f"Terima kasih."
            )

            payload = {
                "chatId": chat_id,
                "text": message,
                "session": waha_session
            }

            headers = {
                'Content-Type': 'application/json',
                'X-Api-Key': api_key
            }
            
            try:
                response = requests.post(waha_url, json=payload, headers=headers)
                
                if response.status_code == 201 or response.status_code == 200:
                    _logger.info(f"Cron WAHA: Berhasil kirim WA ke {phone_number} (Ref: {loan.name})")
                else:
                    _logger.error(f"Cron WAHA Error [{response.status_code}]: Gagal kirim WA ke {phone_number}. Response: {response.text}")
            
            except Exception as e:
                 _logger.error(f"Cron WAHA Exception: Gagal memanggil API WAHA. Error: {str(e)}")
    
    def action_send_email(self):
        self.ensure_one()

        template = self.env.ref('library_management.email_template_library_loan', raise_if_not_found=False)

        ctx = {
            'default' : 'library.loan',
            'default_res_ids': self.ids,
            'default_template_id':template.id if template else False,
            'default_composition_mode': 'comment',
            'force_email':True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    # action button
    def action_confirm(self):
        for record in self:
            record.write({'state' : 'ongoing'})

    
    def action_return(self):
        for record in self:
            for line in record.loan_line_ids:
                if not line.date_return_actual:
                    line.date_return_actual = fields.Date.today()
            record.write({'state': 'returned'})
            if record.total_late_fee > 0:
                record.action_create_invoice()
            

    def action_draft(self):
        for record in self:
            for line in record.loan_line_ids:
                line.date_return_actual = False
            record.write({'state': 'draft'})