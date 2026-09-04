from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Title', required=True)
    isbn = fields.Char(string='ISBN')
    pages = fields.Integer(string='Number of Pages')
    active = fields.Boolean(string='Active', default=True)
    cover_image = fields.Image(string="Cover Books", max_width=1024, max_height=1024)

    author_id = fields.Many2one('res.partner', string='Author', domain="[('is_company', '=', False)]")
    publisher_id = fields.Many2one('res.partner', string='Publisher', domain="[('is_company', '=', True)]")
    external_rating = fields.Float(string='Google Books Rating', digits=(3, 1), default=0.0)
    rating = fields.Float(string='Rating', digits=(3, 1), compute='_compute_rating', store=True)
    review_ids = fields.One2many('library.book.review', 'book_id', string='Reviews')
    review_count = fields.Integer(string='Jumlah Review', compute='_compute_rating', store=True)
    loan_line_ids = fields.One2many('library.loan.line', 'book_id', string='Riwayat Peminjaman')
    loan_count = fields.Integer(string='Dipinjam', compute='_compute_loan_count')

    def _compute_loan_count(self):
        for record in self:
            record.loan_count = len(record.loan_line_ids)

    def action_view_loans(self):
        self.ensure_one()
        return {
            'name': f'Peminjaman: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'list,kanban,form',
            'domain': [('loan_line_ids.book_id', '=', self.id)],
        }

    @api.depends('review_ids.rating', 'external_rating')
    def _compute_rating(self):
        for record in self:
            ratings = [float(r.rating) for r in record.review_ids if r.rating]
            record.review_count = len(ratings)
            if ratings:
                record.rating = round(sum(ratings) / len(ratings), 1)
            else:
                record.rating = record.external_rating or 0.0