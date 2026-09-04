from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryBookReview(models.Model):
    _name = 'library.book.review'
    _description = 'Book Review by Library Member'
    _order = 'review_date desc, id desc'

    book_id = fields.Many2one('library.book', string='Buku', required=True, ondelete='cascade')
    member_id = fields.Many2one('library.member', string='Member', required=True, ondelete='cascade')
    rating = fields.Selection([
        ('1', '1 - Sangat Buruk'),
        ('2', '2 - Kurang'),
        ('3', '3 - Cukup'),
        ('4', '4 - Bagus'),
        ('5', '5 - Sangat Bagus'),
    ], string='Rating', required=True, default='5')
    review_date = fields.Date(string='Tanggal Review', default=fields.Date.context_today)
    comment = fields.Text(string='Ulasan / Komentar')

    _sql_constraints = [
        ('unique_book_member_review', 'UNIQUE(book_id, member_id)', 'Member hanya boleh memberikan satu ulasan per buku!'),
    ]

    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if not record.rating or int(record.rating) not in range(1, 6):
                raise ValidationError("Rating harus antara 1 sampai 5.")
