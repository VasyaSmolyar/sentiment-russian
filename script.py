# -*- coding: utf-8 -*-

import requests
from lxml import html
import time
import csv

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

with open('index.csv', 'w') as csvFile:

    try:

        for film_page in film_urls:
            film_page_url = "https://www.kinopoisk.ru" + film_page + "reviews/?ord=rating"
            filmParsedPage = getParsedPage(film_page_url)
            
            reviews_texts = filmParsedPage.xpath('//span[@itemprop="reviewBody"]')
            print(reviews_texts)
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
        
        time.sleep(60)

    except KeyboardInterrupt:
        pass
