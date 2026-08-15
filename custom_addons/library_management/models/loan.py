from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'

    name = fields.Char(string='No. Referensi', default='New', readonly=True)
    member_id = fields.Many2one('library.member', string='Member', required=True)
    date_borrow = fields.Date(string='Borrow Date', default=fields.Date.context_today)
    date_return_expected = fields.Date(string='Expected Return Date', required=True)
    loan_line_ids = fields.One2many('library.loan.line', 'loan_id', string='Loan Lines')
    total_late_fee = fields.Float(string='Total Denda', compute='_compute_total_late_fee', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
    ], string='Status', default='draft')

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

    def action_draft(self):
        for record in self:
            for line in record.loan_line_ids:
                line.date_return_actual = False
            record.write({'state': 'draft'})