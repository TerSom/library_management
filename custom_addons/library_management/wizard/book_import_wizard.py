import requests
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError

class BookImportWizard(models.TransientModel):
    _name = 'book.import.wizard'
    _description = 'Import Books from Google API'

    keyword = fields.Char(string="Kata Kunci Pencarian", required=True, default="Python")

    def _get_or_create_partner(self, name, is_company=False):
        """Return a res.partner record for the given name, creating it if needed."""
        if not name or not name.strip():
            name = 'Unknown Author' if not is_company else 'Unknown Publisher'

        partner = self.env['res.partner'].search([
            ('name', '=', name.strip()),
            ('is_company', '=', is_company),
        ], limit=1)

        if not partner:
            partner = self.env['res.partner'].create({
                'name': name.strip(),
                'is_company': is_company,
            })

        return partner

    def action_import_books(self):
        """Fungsi untuk nge-hit Google Books API dan create data ke database"""
        
        api_key = self.env['ir.config_parameter'].sudo().get_param('books.api_key')
        if not api_key:
            raise UserError("API Key tidak ditemukan! Pastikan 'books.api_key' sudah ada di menu Settings > Technical > System Parameters.")

        url = self.env['ir.config_parameter'].sudo().get_param('url.books')
        params = {
            'q': self.keyword,
            'maxResults': 30,
            'key': api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise UserError(f"Gagal menghubungi Google Books API: {str(e)}")

        items = data.get('items', [])
        if not items:
            raise UserError("Tidak ada buku yang ditemukan untuk kata kunci tersebut.")

        book_env = self.env['library.book']
        created_count = 0

        for item in items:
            volume_info = item.get('volumeInfo', {})
            identifiers = volume_info.get('industryIdentifiers', [])
            image_link = volume_info.get('imageLinks')
            thumbnail_url = image_link.get('thumbnail') or image_link.get('smallThumbnail')
            title = volume_info.get('title', 'No Title')
            pages = volume_info.get('pageCount') or 0
            rating = float(volume_info.get('averageRating') or 0.0)
            authors = volume_info.get('authors') or ['Unknown Author']
            publisher_name = volume_info.get('publisher') or 'Unknown Publisher'
            isbn_13 = None
            image_base64 = False

            if thumbnail_url:
                try:
                    img_response = requests.get(thumbnail_url, timeout=5)
                    if img_response.status_code == 200:
                        image_base64 = base64.b64encode(img_response.content)
                except Exception:
                    pass

            for identifier in identifiers:
                if identifier.get("type") == 'ISBN_13':
                    isbn_13 = identifier.get('identifier')
                    break
                elif identifier.get("type") == 'ISBN_10' and not isbn_13:
                    isbn_13 = identifier.get('identifier')
                    break

            author_name = authors[0].strip() if authors and authors[0] else 'Unknown Author'
            author_partner = self._get_or_create_partner(author_name, is_company=False)
            publisher_partner = self._get_or_create_partner(publisher_name, is_company=True)

            existing_book = book_env.search([('name', '=', title)], limit=1)

            if not existing_book:
                book_env.create({
                    'name': title,
                    'pages': pages,
                    'author_id': author_partner.id,
                    'publisher_id': publisher_partner.id,
                    'isbn': isbn_13,
                    'cover_image': image_base64,
                    'external_rating': rating,
                })
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Sukses!',
                'message': f'Berhasil menyedot {created_count} buku baru dari Google API.',
                'type': 'success',
                'sticky': False,
            }
        }