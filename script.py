# -*- coding: utf-8 -*-

import requests
from lxml import html
import time

page_number = 1
url = "https://www.kinopoisk.ru/top/lists/322/filtr/all/sort/votes/page/" + str(page_number)

def getParsedPage(url):
    #Возвращает контент вебсайта по выбранной ссылке и парсит в lxml-формате
    response = requests.get(url)
    parsedPage = html.fromstring(response.content)
    return parsedPage

catalogParsedPage = getParsedPage(url)
#Сохраняет "запарсенную" страницу в переменную

film_urls = catalogParsedPage.xpath('//td[@class="news"]/div/a/@href')
#Находит ссылки на страницы фильмов фильмы
print(film_urls)

for film_page in film_urls:
    film_page_url = "https://www.kinopoisk.ru" + film_page + "reviews/?ord=rating"
    filmParsedPage = getParsedPage(film_page_url)
    
    reviews = filmParsedPage.xpath('//span[@itemprop="reviewBody"]/text()')
    reviews_marks = filmParsedPage.xpath('//div[@itemprop="reviews"]/@class')
    
    time.sleep(60)

time.sleep(60)