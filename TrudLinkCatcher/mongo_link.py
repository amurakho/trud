from mongoengine import *

class Urls(Document):
    url = URLField(unique=True)
    crawl_date = DateTimeField()
    key_word = ListField()
    date_added = DateField()
    is_parsed = BooleanField()