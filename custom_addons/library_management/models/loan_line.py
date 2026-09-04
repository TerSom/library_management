from odoo import models, fields, api

class LibraryLoanLine(models.Model):
    _name = 'library.loan.line'
    _description = 'Library Loan Line'

    loan_id = fields.Many2one('library.loan', string='Loan Reference', ondelete='cascade')
    book_id = fields.Many2one('library.book', string='Book', required=True)
    author_id = fields.Many2one(related='book_id.author_id', string='Penulis', readonly=True)
    cover_image = fields.Image(related='book_id.cover_image', string='Cover', readonly=True)
    isbn = fields.Char(related='book_id.isbn', string='ISBN', readonly=True)

    date_return_actual = fields.Date(string='Return Date',readonly=True)
    late_fee = fields.Float(string='Late Fee', compute='_compute_late_fee', store=True , readonly=True)

    @api.depends('date_return_actual', 'loan_id.date_return_expected')
    def _compute_late_fee(self):
        today = fields.Date.today()
        for line in self:
            fee = 0.0
            expected = line.loan_id.date_return_expected
            if expected:
                reference_date = line.date_return_actual or today
                if reference_date > expected:
                    delta = reference_date - expected
                    fee = delta.days * 5000.0
            line.late_fee = fee