# -*- coding: utf-8 -*-
import scrapy
import datetime
from ..items import TrudlinkcatcherItem
from itertools import product

class LinkcatcherSpider(scrapy.Spider):

    name = 'linkcatcher'

    allowed_domains = ['trud.ua']

    start_urls = ['https://trud.ua/search.cv/results.html']

    pass_key_words = ['повар']

    # period = {'1' : 'today',
    #           '7' : '7days',
    #            '30': 'month'}

    custom_settings = {'ITEM_PIPELINES': {
        'TrudLinkCatcher.pipelines.TrudlinkcatcherPipeline': 1,
    }}

    def __init__(self, *args, **kwargs):
        super(LinkcatcherSpider, self).__init__(*args, **kwargs)
        self.key_words_start_counter = 2
        self.date = datetime.datetime.now()
        self.key_words_file = open('key_words.txt', 'r')
        self.period = kwargs.get('period', 'today')
        self.loc_file = open('cities.txt')
        with open('cities.txt') as loc_file:
            self.locations = loc_file.readlines()

    def parse(self, response):

        base_url = 'https://trud.ua/search.cv/results.html'

        pass_key_words = []
        for _ in range(self.key_words_start_counter):
            key_word = self.key_words_file.readline().strip()
            if key_word:
                pass_key_words.append(key_word)
        params = list(product(pass_key_words, self.locations))
        for param in params:
            url = 'https://trud.ua/search/search.html?company=0&show=cv'
            url += '&query={}'.format(param[0])

            if param[1] != 'Вся Украина\n':
                url += '&city={}'.format(param[1].strip())
            yield response.follow(url, self.parse_page_2, meta={'key_word': param[0],
                                                                'test': url})
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse_page_2(self, response):

        url = response.url

        if response.css('.msg-cell').get():
            return

        last_slash_index = response.url.rfind('/')
        if response.url[last_slash_index - 1] == 'l' or 'jobcategory' in url:
            return

        period_url = '/period/' + self.period

        if 'queryAlias' in url:
            start_locate_idx = url.find('queryAlias') - 1

            new_url = url[:start_locate_idx] + period_url + url[start_locate_idx:]

        else:
            start_locate_idx = url.find('/q/')

            new_url = url[:start_locate_idx] + period_url + url[start_locate_idx:]

        yield response.follow(new_url, self.parse_page, meta={'key_word': response.meta.get('key_word')})

    def parse_page(self, response):

        if response.css('.msg-cell').get():
            return

        items = TrudlinkcatcherItem()

        items['crawl_date'] = self.date.strftime("%d/%m/%y, %H:%M:%S")
        items['is_parsed'] = False
        items['key_word'] = response.meta['key_word']

        links = response.css('.titl-r a').xpath('@href').getall()
        dates = response.css('.date::text').getall()
        for date, link in zip(dates, links):
            items['url'] = 'https://trud.ua' + link
            items['date_added'] = date
            yield items

        next_page_url = response.css('.next-p').xpath('@href').get()
        if next_page_url:
            base = 'https://trud.ua'
            full_url = base + next_page_url
            yield response.follow(full_url, callback=self.parse_page, meta={'key_word': items['key_word']})