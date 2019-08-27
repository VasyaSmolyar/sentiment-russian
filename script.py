# -*- coding: utf-8 -*-

import requests
from lxml import html, etree
import time
import csv

def getParsedPage(url, proxy=None):
    #Возвращает контент вебсайта по выбранной ссылке и парсит в lxml-формате
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Host": "www.kinopoisk.ru/",
        "Origin": "https://www.kinopoisk.ru/",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers"}
    if not proxy:
        response = requests.get(url, headers=headers)
    else:
        http_proxy = "https://{}:{}".format(proxy['IP'], proxy['PORT'])
        response = requests.get(url, headers=headers, proxies={"https_proxy" : http_proxy})
    parsedPage = html.fromstring(response.content)
    return parsedPage

proxies = []

params = {"l": "en",
          "t": "https"}

proxy_url = "https://www.proxy-list.download/api/v0/get"
proxy_page = requests.get(proxy_url, params=params)

parsedString = proxy_page.json()
parsedStringIncluded = parsedString[0]["LISTA"]

for proxy in parsedStringIncluded:
    address = {"IP" : proxy["IP"], "PORT" : proxy["PORT"]}
    proxies.append(address)
    
proxy_num = 0
page_number = 1
url = "https://www.kinopoisk.ru/top/lists/322/filtr/all/sort/votes/page/" + str(page_number)

test = getParsedPage("https://httpbin.org/get", proxies[proxy_num])
print(test)

while True:
    try:
        catalogParsedPage = getParsedPage(url, proxies[proxy_num])
        break
        #Сохраняет "запарсенную" страницу в переменную
    except etree.ParserError:
        proxy_num += 1
        if proxy_num == len(proxies):
            proxy_num = 0
            print('The end of proxie list...')
            time.sleep(60)
        continue

film_urls = catalogParsedPage.xpath('//td[@class="news"]/div/a/@href')
#Находит ссылки на страницы фильмов фильмы
print(film_urls)

with open('index.csv', 'w') as csvFile:

    try:

        for film_page in film_urls:
            film_page_url = "https://www.kinopoisk.ru" + film_page + "reviews/?ord=rating"

            while True:
                filmParsedPage = getParsedPage(film_page_url, proxies[proxy_num])
                reviews_texts = filmParsedPage.xpath('//span[@itemprop="reviewBody"]')
                print(reviews_texts)
                if len(reviews_texts) == 0:
                    proxy_num += 1
                    if proxy_num == len(proxies):
                        proxy_num = 0
                        print('The end of proxie list...')
                        time.sleep(60)
                    continue
                break

            reviews_marks = filmParsedPage.xpath('//div[@itemprop="reviews"]/@class')
            print(reviews_marks)
            
            reviews = []
            
            for i in reviews_texts:
                index = reviews_texts.index(i)
                print(index)
                reviews_text = ""
                
                text_parts = i.xpath('text()')
                print(text_parts)
                
                for t in text_parts:
                    reviews_text += t
                    print(t)
                
                review = reviews_text.replace("\"","'")
                review = review.replace("\r\n"," ")
                review = review.replace("\n"," ")
                print(review)
                    
                grade = "1"
                
                if reviews_marks[index] == "response good":
                    grade = "2"
                elif reviews_marks[index] == "response neutral":
                    grade = "1"
                else:
                    grade = "0"
                    
                newArray = [review, grade]
                print(newArray)
                
                csvFile.write('"{}",{}\n'.format(review, grade))

    except KeyboardInterrupt:
        pass
