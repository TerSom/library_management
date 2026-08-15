from odoo import models, fields, api

class LibraryLoanLine(models.Model):
    _name = 'library.loan.line'
    _description = 'Library Loan Line'

    loan_id = fields.Many2one('library.loan', string='Loan Reference', ondelete='cascade')
    book_id = fields.Many2one('library.book', string='Book', required=True)
    
    date_return_actual = fields.Date(string='Return Date',readonly=True)
    late_fee = fields.Float(string='Late Fee', compute='_compute_late_fee', store=True , readonly=True)

    @api.depends('date_return_actual', 'loan_id.date_return_expected')
    def _compute_late_fee(self):
        for line in self:
            fee = 0.0
            if line.date_return_actual and line.loan_id.date_return_expected:
                if line.date_return_actual > line.loan_id.date_return_expected:
                    delta = line.date_return_actual - line.loan_id.date_return_expected
                    fee = delta.days * 5000.0
            line.late_fee = fee