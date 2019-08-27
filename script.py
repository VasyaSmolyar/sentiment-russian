# -*- coding: utf-8 -*-

import requests
from lxml import html, etree
import time
import csv

cookie = "i=TULr5XEKitrpDfzzwenbiQEgyupnPF29DWsE1hcjaDQQH31dADYuPNvWeo++eVokYed+gRJaFzXeko7/+jooCyC3+ZU=; mda_exp_enabled=1; yandexuid=5393565341562700653; _ym_uid=1565960898476401727; _ym_d=1565960898; mda=0; yp=1569525174.oyu.5393565341562700653#1567019574.yu.5393565341562700653; cycada=Zg9wUFPbevFmP94y7LAx/qt5Y8hdT49KHWjgd5CPtpE=; mobile=no; refresh_yandexuid=5393565341562700653; PHPSESSID=8op8h8fanmmv7ikjdcnpojqh73; user_country=ru; yandex_gid=10723; tc=5396; _csrf_csrf_token=QLECv-CT-nMYm9u5IYenxaxMMMUdpTlLkolzNZ9MQCQ; noflash=false; user-geo-region-id=10723; user-geo-country-id=2; desktop_session_key=3346927f09865881e1f858618140e4512210525e57785b10708b64b6019ee44ed614cfe268ff142903fe733a31df501006b90e5963dcf215a654befc5fac0916d93e2330336555d4b2342584dc2186f618077208db5301b25f60681a8cd440c7; desktop_session_key.sig=uy8ws8Cu-RSVKHVYZdOJGzmAUaA; yandex_plus_metrika_cookie=true; _ym_wasSynced=%7B%22time%22%3A1566933173443%2C%22params%22%3A%7B%22eu%22%3A0%7D%2C%22bkParams%22%3A%7B%7D%7D; _ym_isad=2; ya_sess_id=noauth:1566933657; ys=c_chck.344439571; mda2_beacon=1566933657741; _ym_visorc_22663942=b; sso_status=sso.passport.yandex.ru:synchronized; _ym_visorc_52332406=b"

def getParsedPage(url, proxy=None):
    #Возвращает контент вебсайта по выбранной ссылке и парсит в lxml-формате
    global cookie
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Cookie" : cookie,
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers"}
    if not proxy:
        response = requests.get(url, headers=headers)
    else:
        http_proxy = "https://{}:{}".format(proxy['IP'], proxy['PORT'])
        response = requests.get(url, headers=headers, proxies={"https_proxy" : http_proxy})
    #print(response.headers)
    cookie = response.headers.get('Set-Cookie', cookie)
    cookie = response.headers.get('set-cookie', cookie)
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
                time.sleep(1.5)
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
