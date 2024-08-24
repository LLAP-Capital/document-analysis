
from app import db
from datetime import datetime

class Website:
    @staticmethod
    def add_website(url, content):
        website = {
            'url': url,
            'content': content,
            'created_at': datetime.utcnow()
        }
        return db.websites.insert_one(website)

    @staticmethod
    def get_all_websites():
        return list(db.websites.find())