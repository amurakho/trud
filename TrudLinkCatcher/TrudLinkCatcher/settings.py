# -*- coding: utf-8 -*-

# Scrapy settings for TrudLinkCatcher project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'TrudLinkCatcher'

SPIDER_MODULES = ['TrudLinkCatcher.spiders']
NEWSPIDER_MODULE = 'TrudLinkCatcher.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# PROXY_POOL_ENABLED = True
#
# DOWNLOADER_MIDDLEWARES = {
#     # ...
#     'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
#     'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
#     # ...
# }

IMAGES_STORE = 'images'