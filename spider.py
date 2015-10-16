import scrapy

from pyquery import PyQuery

BASE_URL = 'https://github.com/search?o=desc&s=stars&utf8=%%E2%%9C%%93&q=%s'


class GitSpider(scrapy.Spider):
    name = 'gitionary'
    start_urls = ['http://www-01.sil.org/linguistics/wordlists/english/wordlist/wordsEn.txt']

    def parse(self, response):
        for word in response.body.splitlines():
            if len(word) < 4:
                continue
            url = BASE_URL % word
            yield scrapy.Request(url, self.parse_word, meta={'word': word})

    def parse_word(self, response):
        document = PyQuery(response.body)
        item = {'word': response.meta['word'], 'places':{}, 'languages':{}, 'repos': {}}

        places = document(".codesearch-aside .menu a")
        for place in places:
            key = place.itertext().next()
            try:
                value = place.find_class('counter')[0].text_content()
            except IndexError:
                value = 0
            item["places"][key] = value

        languages = document(".filter-list li")
        for language in languages:
            key = language.text_content().strip().split()[1]
            try:
                value = language.find_class('count')[0].text_content()
            except IndexError:
                value = 0
            item["languages"][key] = value

        repos = document(".repo-list li")
        for repo in repos:
            key = repo.find('h3').find_class('repo-list-name')[0].find('a').attrib['href']
            value = repo.find_class('repo-list-stats')[0].find('a').text_content().strip()
            item["repos"][key] = value

        yield item