# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mongoengine
from mongo_link import Urls
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from new_mongo_models_cv import Cv, Location, Title, Name, Platform, \
                                    Salary, Language,Keyword, Portfolio, \
                                    AdditionalEducation, Education,Industry,\
                                    WorkExperience, AnotherInformation, \
                                    RawHtml
import re

class TrudlinkcatcherPipeline(object):

    def process_item(self, item, spider):

        try:
            is_find = Urls.objects.get(url=item['url'])
        except:
            is_find = None
        if is_find:
            if is_find.date_added != item['date_added']:
                is_find.is_parsed = False
                is_find.crawl_date = item['crawl_date']
            if item['key_word'] not in is_find.key_word:
                is_find.key_word.append(item['key_word'])
                is_find.save()
        else:
            self.new_url = Urls()
            self.new_url.url = item['url']
            self.new_url.crawl_date = item['crawl_date']
            self.new_url.is_parsed = item['is_parsed']
            self.new_url.key_word.append(item['key_word'])
            self.new_url.date_added = item['date_added']
            self.new_url.save()

        return item

    def open_spider(self, spider):
        self.conn = mongoengine.connect( db='new_urls',
                username='Artem Murakhovskyi', host='localhost', port=27017)


class TrudPageParserPipeline(ImagesPipeline):

    def process_item(self, item, spider):

        cv = Cv.objects.filter(url=item['url']).first()
        if not cv:
            cv = Cv(url=item['url'],
                    img_src=item['img_src'],
                    updated_by_owner=item['updated_by_owner'],
                    birth_date=item['birth_date'],
                    cv_lang=item['cv_lang'],
                    about_me=item['about_me'],
                    photo_storage=item['photo_storage'],
                    job_status=item['job_status'],
                    employment_type=item['employment_type'],
                    work_schedule=item['work_schedule'],
                    age=item['age'],
                    )

            title = Title(name=item['title'])
            name = Name(fullname=item['fullname'])
            platform = Platform(name=item['platform'])
            salary = Salary(currency=item['currency'],
                                salary=item['salary'])
            location = Location(address=item['adress'])

            platform.save()
            location.save()
            title.save()

            cv.name = name
            cv.title = title
            cv.platform = platform
            cv.salary = salary
            cv.location = location

        else:
            Title.objects(id=cv.title.id).modify(set__name=item['title'])

            cv.name.fullname = item['fullname']

            Platform.objects(id=cv.platform.id).modify(set__name=item['platform'])

            cv.salary.salary = item['salary']
            cv.salary.currency = item['currency']

            Location.objects(id=cv.location.id).modify(set__address=item['adress'])

            for cv_keyword in cv.keywords:
                cv.keywords.remove(cv_keyword)
                Keyword.objects(id=cv_keyword.id).delete()

            for cv_lang in cv.languages:
                cv.languages.remove(cv_lang)
                Language.objects(id=cv_lang.id).delete()

            for cv_edu in cv.education:
                cv.education.remove(cv_edu)

            for cv_aedu in cv.additional_education:
                cv.additional_education.remove(cv_aedu)

            for cv_exp in cv.experience:
                cv.experience.remove(cv_exp)

            for cv_portf in cv.portfolio:
                cv.portfolio.remove(cv_portf)

        for keyword_name in item['keywords']:
            keyword = Keyword()
            keyword.name = keyword_name
            keyword.save()
            cv.keywords.append(keyword)

        for lang_name, lang_level in zip(item['language_name'], item['language_level']):
            language = Language()
            language.name = lang_name
            language.level_grade = lang_level
            language.save()
            cv.languages.append(language)

        for block in item['edu_info']:
            education = Education()
            education.school_name = block['edu_school_name']
            new_location = Location(address=block['edu_location'])
            new_location.save()
            education.location = new_location
            education.start_year = block['edu_start_year']
            education.end_year = block['edu_end_year']
            education.degree = block['edu_degree']
            cv.education.append(education)

        for block in item['aedu_info']:
            additional_education = AdditionalEducation()
            additional_education.start_date = block['aedu_start_date']
            additional_education.end_date = block['aedu_end_date']
            additional_education.course_name = block['aedu_course_name']
            cv.additional_education.append(additional_education)

        for block in item['work_info']:
            experience = WorkExperience()
            experience.start_date = block['work_start_date']
            experience.end_date = block['work_end_date']
            experience.till_now = block['till_now']
            new_title = Title(name=block['work_position'])
            new_title.save()
            experience.position = new_title
            experience.company_name = block['company_name']
            new_industry = Industry(name=block['industry'])
            new_industry.save()
            experience.industry = new_industry
            experience.job_description = block['job_description']
            cv.experience.append(experience)


        raw = RawHtml()
        raw.html = item['raw_html_html']
        raw.created_at = item['raw_html_date']
        raw.save()
        cv.raw_html.append(raw)

        if item['portfolio']:
            new_portfolio = Portfolio(url=item['portfolio'])
            cv.portfolio.append(new_portfolio)

        cv.save()

        return super(ImagesPipeline, self).process_item(item, spider)

    def get_media_requests(self, item, info):
        if item['img_src']:
            yield scrapy.Request(item['img_src'], meta={'item': item})
        else:
            return item

    def image_downloaded(self, response, request, info):
        for path, image, buf in self.get_images(response, request, info):
            file_name = re.search('[0-9]+', response.meta['item']['url']).group(0)
            path = '{}.jpg'.format(file_name)
            self.store.persist_file(
                path, buf, info,
                headers={'Content-Type': 'image/jpeg'})
        return response.meta['item']

