# -*- coding: utf-8 -*-
import scrapy
import mongoengine
from mongo_link import Urls
from ..items import TrudPageparserSpiderItem
import re
import datetime
import json
from scrapy import Selector

class PageparserSpider(scrapy.Spider):
    name = 'pageparser'

    allowed_domains = ['trud.ua']

    start_urls = ['http://trud.ua/']

    custom_settings = {'ITEM_PIPELINES': {
        'TrudLinkCatcher.pipelines.TrudPageParserPipeline': 1,
    }}

    work_schedule_types = ('Полный рабочий день',
                            'Неполный рабочий день',
                            'Свободный график',
                            'Удаленная работа'
                           )

    language_levels = {'В совершенстве': 6,
                      'Средний': 3,
                      'Начинающий': 1}

    letter_dict = {
        'urk': ['а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л',
                'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я'],
        'rus': ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п',
                'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'],
        'eng': ['a', 'e', 'i', 'o', 'u', 'y', 'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm',
                'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']
    }
    letter_dict['ukr_diff'] = list(set(letter_dict['urk']) - set(letter_dict['rus']))

    def detect_language(self, text):
        if any(i in self.letter_dict['ukr_diff'] for i in list(text)):
            return 'uk'
        elif any(i in self.letter_dict['rus'] for i in list(text)):
            return 'ru'
        else:
            return 'en'

    def parse(self, response):
        conn = mongoengine.connect(db='new_urls',
                                   username='Artem Murakhovskyi', host='localhost', port=27017)
        for row in Urls.objects:
            if row.is_parsed is False:
                yield scrapy.Request(row.url, self.parse_page, meta={'db_row': row})


    def take_number(self, response):
        items = response.meta['items']
        contact_json = json.loads(response.body)
        items['portfolio'] = Selector(text=contact_json['links']).response.xpath('//a/@href').get()
        items['contact_phone'] = Selector(text=contact_json['phone']).response.css('td::text')[1].get().strip()
        yield items

    def parse_page(self, response):

        row = response.meta['db_row']
        row.is_parsed = True
        row.save()

        profile_id = re.search('[0-9]+', response.url).group(0)

        base = 'https://trud.ua'

        items = TrudPageparserSpiderItem()

        block = response.css('.info-wrap')

        items['platform'] = 'trud.ua'
        items['keywords'] = response.meta['db_row'].key_word

        items['raw_html_html'] = str(response.body)
        items['raw_html_date'] = datetime.datetime.now().date()
        items['url'] = response.url

        img_src = base + response.css('.photo-wrap').xpath('img/@src').get()[1:]
        if img_src == 'https://trud.ua/office/photo/0/':
            items['img_src'] = None
            items['photo_storage'] = None
        else:
            items['img_src'] = base + response.css('.photo-wrap').xpath('img/@src').get()[1:]
            items['photo_storage'] = '/images/{}.jpg'.format(profile_id)

        items['job_status'] = block.css('.cv-status::text').get()
        items['fullname'] = block.css('.head-titl::text').get().strip()
        items['title'] = block.css('.position-t::text').get().strip()

        salary = block.css('.salary::text').get()
        if salary:
            items['salary'] = re.search('[0-9]+', salary).group(0)
            items['currency'] = re.search('[a-zа-я]+', salary).group(0)
        else:
            items['salary'] = None
            items['currency'] = ''

        main_info = block.css('.info-table .lbl-gray+ td::text').getall()
        items['employment_type'] = main_info[0].strip().split(', ')
        items['job_location'] = main_info[1]
        items['updated_by_owner'] = main_info[2].strip()
        items['birth_date'] = main_info[3][:10]
        items['age'] = re.search('[0-9]+', main_info[3][12:]).group(0)
        items['adress'] = main_info[4].strip()

        items['work_schedule'] = []
        meta_content = response.xpath('//meta[@name="description"]/@content').get()
        work_conditions = meta_content[meta_content.index('Условия работы') + 16:].split(', ')
        for word in work_conditions:
            if word not in self.work_schedule_types:
                break
            items['work_schedule'].append(word)

        items['about_me'] = ''
        items['language_name'] = []
        items['language_level'] = []


        items['another_information_text'] = []
        items['another_information_title'] = []

        items['work_info'] = []

        items['edu_info'] = []

        items['aedu_info'] = []

        text = ''

        extra_blocks = block.css('.info-block~ .info-block+ .info-block')
        for extra_block in extra_blocks:
            title_name = extra_block.css('.inf-titl::text').get().strip()
            if title_name == 'Цель' or title_name == 'Военная служба':
                items['another_information_text'].append(extra_block.css('.txt-inf::text').get().strip())
                items['another_information_title'].append(extra_block.css('.inf-titl::text').get().strip())
                text += ' '.join(items['another_information_text'])

            elif title_name == 'О себе':
                items['about_me'] = extra_block.css('.txt-inf::text').get().strip()
                text += items['about_me']

            elif title_name == 'Опыт работы':
                edublocks = extra_block.css('.sub-item')
                for edublock in edublocks:
                    part_block = {}
                    years = edublock.css('.lbl-gray::text').get()
                    part_block['work_start_date'] = '01.' + years[3:10]
                    if 'настоящее время' in years:
                        part_block['work_end_date'] = datetime.datetime.now()
                        part_block['till_now'] = True
                    else:
                        part_block['work_end_date'] = '01.' + years[14:21]
                        part_block['till_now'] = False
                    part_block['work_position'] = edublock.css('.sub-titl::text').get().strip()
                    company_info = edublock.css('.view-bold::text').get().strip()
                    part_block['company_name'] = company_info[:company_info.rindex('(')]
                    part_block['job_description'] = extra_block.css('.txt-inf::text').get().strip()
                    part_block['industry'] = company_info[company_info.rindex('(') + 1:company_info.rindex(')')]

                    text += ' '.join(part_block['job_description'])
                    items['work_info'].append(part_block)

            elif title_name == 'Образование':
                edublocks = extra_block.css('.sub-item')
                for edublock in edublocks:
                    part_block = {}
                    years = edublock.css('.lbl-gray::text').get()
                    part_block['edu_start_year'] = '01.' + years[6:10]
                    if 'настоящее время' in years:
                        part_block['edu_end_year'] = datetime.datetime.now().year
                    else:
                        part_block['edu_end_year'] = years[17:21]
                    part_block['edu_degree'] = edublock.css('.sub-titl::text').get().strip()
                    last = edublock.css('.view-bold::text').get().strip()
                    part_block['edu_location'] = last[:last[1:].find(' ') + 1]
                    part_block['edu_school_name'] = last[last[1:].find(' ') + 2:]

                    items['edu_info'].append(part_block)

            elif title_name == 'Дополнительное образование или курсы':
                edublocks = extra_block.css('.sub-item')
                for edublock in edublocks:
                    part_block = {}

                    years = edublock.css('.lbl-gray::text').get()
                    part_block['aedu_start_date'] = years[6:10]
                    if 'настоящее время' in years:
                        part_block['aedu_end_date'] = datetime.datetime.now().year
                    else:
                        part_block['aedu_end_date'] = years[17:21]
                    part_block['aedu_course_name'] = edublock.css('.sub-titl::text').get().strip()

                    items['aedu_info'].append(part_block)


            elif title_name == 'Знание языков':
                lang_blocks = extra_block.css('.sub-item div::text').getall()
                for lang_block in lang_blocks:
                    lang_block = lang_block.strip()
                    name_idx = lang_block.find(' ')
                    items['language_name'].append(lang_block[:name_idx])
                    items['language_level'].append(self.language_levels[lang_block[name_idx + 1:]])

            if not text:
                items['cv_lang'] = 'ru'
            else:
                items['cv_lang'] = self.detect_language(text)

        yield scrapy.FormRequest(url='https://trud.ua/ajax/getContacts/',
                                    callback=self.take_number,
                                    formdata={'jobId': profile_id},
                                    headers={'X-Requested-With': 'XMLHttpRequest'},
                                    meta={'items': items})
