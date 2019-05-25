# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TrudlinkcatcherItem(scrapy.Item):
    url = scrapy.Field()
    crawl_date = scrapy.Field()
    key_word = scrapy.Field()
    date_added = scrapy.Field()
    is_parsed = scrapy.Field()


class TrudPageparserSpiderItem(scrapy.Item):

    raw_html_html = scrapy.Field()
    raw_html_date = scrapy.Field()
    url = scrapy.Field()
    img_src = scrapy.Field() #image link
    photo_storage = scrapy.Field() # photo path
    keywords = scrapy.Field()
    platform = scrapy.Field()
    work_schedule = scrapy.Field()
    fullname = scrapy.Field()  # name
    salary = scrapy.Field()
    currency = scrapy.Field()
    title = scrapy.Field()  # title
    employment_type = scrapy.Field() # vacantion type
    job_location = scrapy.Field()
    adress = scrapy.Field() # location
    job_status = scrapy.Field()
    birth_date = scrapy.Field()
    age = scrapy.Field()
    cv_lang = scrapy.Field()

    # languages
    language_name = scrapy.Field()
    language_level = scrapy.Field()

    contact_phone = scrapy.Field()
    portfolio = scrapy.Field()
    about_me = scrapy.Field()
    updated_by_owner = scrapy.Field()
    another_information_title = scrapy.Field()
    another_information_text = scrapy.Field()

    # work_experience
    work_info = scrapy.Field()

    edu_info = scrapy.Field()

    aedu_info = scrapy.Field()
    # work_start_date = scrapy.Field()
    # work_end_date = scrapy.Field()
    # till_now = scrapy.Field()
    # work_position = scrapy.Field()
    # company_name = scrapy.Field()
    # job_description = scrapy.Field()
    # industry = scrapy.Field()

    # education
    # edu_start_year = scrapy.Field()
    # edu_end_year = scrapy.Field()
    # edu_degree = scrapy.Field()
    # edu_location = scrapy.Field()
    # edu_school_name = scrapy.Field()

    # additional education
    # aedu_start_date = scrapy.Field()
    # aedu_end_date = scrapy.Field()
    # aedu_course_name = scrapy.Field()




