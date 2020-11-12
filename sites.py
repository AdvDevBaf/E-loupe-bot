import requests
from bs4 import BeautifulSoup
from json import loads, decoder
from Settings import header, cookies, soup_type, logger,error_logger, telegram_bot
import pandas as pd
from fuzzywuzzy import fuzz
import time

class MasterClass(object):
    def __init__(self):
        self.header = header
        self.cookies = cookies
        self.soup_type = soup_type
        self.info = ''
        self.price = ''
        self.link = ''

    def price_changes(self, links, chat_id, message_id):
        return self.price

    def get_sku(self, url, chat_id, message_id):
        return self.link

    def item_in_stock(self,url, chat_id, message_id):
        return self.link

    def reviews_rating(self,url, chat_id, message_id):
        return self.link

    def perfect_name(self,url, chat_id, message_id):
        return self.link

    def description(self,url, chat_id, message_id):
        return self.link

    def get_certificate(self,url, chat_id, message_id):
        return self.link

    def product_image(self,url, chat_id, message_id):
        return self.link

    def product_video(self,url, chat_id, message_id):
        return self.link

    def get_brand(self,url,brand_name):
        return self.link

    def get_categories(self,brand, chat_id, message_id):
        return self.link

    def parse_data(self, url, chat_id, message_id, brand_name):
        if 'goods' in str(url):
            brand = {'href': url}
        elif 'http' not in str(brand_name):
            brand = self.get_brand(url, brand_name)
        else:
            brand = {'href':brand_name}
        data = self.get_categories(brand, chat_id, message_id)
        price = []
        sku = []
        crw = []
        cr = []
        i_stock = []
        name = []
        descript = []
        cert = []
        img = []
        video = []
        for i,v in enumerate(data):
            soap = self.parse_link(v)
            price.append(self.price_changes(soap, chat_id, message_id))
            sku.append(self.get_sku(soap, chat_id, message_id))
            review, rating = self.reviews_rating(soap, chat_id, message_id)
            crw.append(review)
            cr.append(rating)
            i_stock.append(self.item_in_stock(soap, chat_id, message_id))
            name.append(self.perfect_name(soap, chat_id, message_id))
            descript.append(self.description(soap, chat_id, message_id))
            cert.append(self.get_certificate(soap, chat_id, message_id))
            img.append(self.product_image(soap, chat_id, message_id))
            video.append(self.product_video(soap, chat_id, message_id))
            telegram_bot.edit_message_text('Идет обработка: '+str(round(((i + 1) / len(data))*100,2))+'%', chat_id, message_id)

        return self.save_to_excel(data, price, sku, crw, cr, i_stock, name, descript, cert, img, video,
                                  chat_id)

    def save_to_excel(self, data, price, sku, crw, cr, i_stock, name, descript, cert, img, video, chat_id):
        telegram_bot.send_message(chat_id, 'Сохраняем..')
        table = {'Заголовок': name, 'Артикул': sku, 'Рейтинг': cr, 'Обзоры': crw, 'Цена': price, 'Link': data,
                 'Наличие товара': i_stock, 'Описание': descript, 'Сертификаты или др плашки': cert,
                 'Изображение продукта': img, 'Видео': video}

        frame = pd.DataFrame(table, columns=['Заголовок', 'Артикул', 'Рейтинг', 'Обзоры', 'Цена', 'Link',
                                             'Наличие товара', 'Описание', 'Сертификаты или др плашки',
                                             'Изображение продукта', 'Видео'])
        frame.to_excel('e-loupe.xlsx', index=False, header=True)
        return 'ok'

    def parse_link(self, url):
        response = requests.get(url, headers=self.header, cookies=self.cookies)
        soup = BeautifulSoup(response.text, str(self.soup_type))
        return soup


class OzonSite(MasterClass):
    def price_changes(self,soup, chat_id, message_id):
        price = ''
        script_id = str(soup)[str(soup).find("state-webProductMainWidget-"):str(soup).find("state-webProductMainWidget-") +
                                                                   len('state-webProductMainWidget-??????-default-1')]
        for script in soup.findAll('div', attrs={'id': script_id}): #'state-webProductMainWidget-347746-default-1',}):
            try:
                old = loads(script['data-state'])['cellTrackingInfo']['product']['price']
                new = loads(script['data-state'])['cellTrackingInfo']['product']['finalPrice']
                if old == new:
                    logger.info(loads(script['data-state'])['cellTrackingInfo']['product']['price'])
                    logger.info(loads(script['data-state'])['cellTrackingInfo']['product']['finalPrice'])
                    logger.info('Цена на товар составляет {0} руб'.format(old))
                    price = 'Цена на товар составляет {0} руб'.format(old)
                else:
                    logger.info('Цена на товар изменилась с {} на {}'.format(old, new))
                    price = 'Цена на товар изменилась с {} на {}'.format(old, new)
            except (KeyError, TypeError) as exp:
                error_logger.error('Error was occurred by price handling: ' + str(exp.args[0]))
                price = old
            logger.info(price)
        return price

    def get_sku(self, soup, chat_id, message_id):
        try:
            span = soup.find('span', attrs={'class': 'b2d7 b2d9'}).text
            sku = str(span)
            logger.info(str(span))
        except AttributeError as ex:
            sku = 'Артикул отсутствует'
            error_logger.error('Error was occurred by sku handling: ' + ex.args[0])
        return sku

    def item_in_stock(self, soup, chat_id, message_id):
        information = 'В наличии'
        logger.info('В наличии')
        for h2 in soup.findAll('h2'):
            if "Этот товар закончился" in str(h2.text).replace("\n", "").replace("    ", ""):
                information = "Товар закончился, либо остались только некоторые размеры"
                error_logger.warning("Товар закончился, либо остались только некоторые размеры")
        return information

    def reviews_rating(self, soup, chat_id, message_id):
        reviews = ''
        rating = ''
        try:
            script_id = str(soup)[str(soup).find("state-webReviewProductScore-"):str(soup).find("state-webReviewProductScore-") +
                                                                   len('state-webReviewProductScore-??????-default-1')]
            scr = soup.find('div', attrs={'id': script_id})#'state-webReviewProductScore-404491-default-1'})
                                             #'type': 'application/json'})
            reviews = str(loads(scr['data-state'])['reviewsCount'])
            rating = str(round(float(loads(scr['data-state'])['totalScore']), 2))
            logger.info('отзыв: ' + str(loads(scr['data-state'])['reviewsCount']))
            logger.info('оценка: '+ str(round(float(loads(scr['data-state'])['totalScore']), 2)))
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by review/rating handling: ' + ex.args[0])
            reviews = ''
            rating = ''
        return reviews, rating

    def perfect_name(self, soup, chat_id, message_id):
        name = ''
        try:
            script_id = str(soup)[str(soup).find("state-webSale-"):str(soup).find("state-webSale-") +
                                                                           len('state-webSale-??????-default-1')]
            scr = soup.find('div', attrs={'id': script_id,})
                                             #'type': 'application/json'})
            logger.info(str(loads(scr['data-state'])['cellTrackingInfo']['product']['title']))
            name = str(loads(scr['data-state'])['cellTrackingInfo']['product']['title'])
            logger.info('имя добавлено')
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by name handling: ' + ex.args[0])
            name  = ''
        return name

    def description(self, soup, chat_id, message_id):
        desc = ''
        try:
            scr = soup.find('script', attrs={'data-n-head': True,
                                             'type': 'application/ld+json'})
            logger.info('Описание добавлено')
            desc = str(loads(scr.string)['description'])
        except (AttributeError, KeyError) as ex:
            error_logger.error('Error was occurred by desc handling: ' + ex.args[0])
            desc = ''
        return desc

    def get_certificate(self, soup, chat_id, message_id):
        cert = ''
        span = soup.findAll('span', attrs={'class': 'b2h2'})
        if len(span) > 1:
            cert = str(span[1].text)
            logger.info(span[1].text)
        elif len(span) == 1:
            cert = str(span[0].text)
            logger.info(span[0].text)
        else:
            cert = 'Нет'
            logger.warning('Нет плашки')
        logger.info(cert)
        return cert

    def product_image(self, soup, chat_id, message_id):
        image = ''
        try:
            span = soup.find('img', attrs={'loading': 'lazy'})
            if span['src'] != "":
                logger.info('Фото есть')
                image = 'Фото есть'
            else:
                logger.info('Фото отсутствует')
                image = 'Фото отсутствует'
        except (TypeError, AttributeError, KeyError) as ex:
            error_logger.error('Error was occurred by image handling: ' + ex.args[0])
            image = 'Фото отсутствует'
        logger.info(image)
        return image

    def product_video(self, soup, chat_id, message_id):
        video = ''
        try:
            scr = soup.find('script', attrs={'id': 'state-webGallery-411446-default-1',
                                             'type': 'application/json'})
            if 'videos' in loads(scr.string):
                logger.info('Видео есть - ' + str(loads(scr.string)['videos']))
                video = 'Видео есть'
            else:
                logger.warning('Видео нет')
                video = 'Видео нет'
        except (TypeError, AttributeError, KeyError) as ex:
            error_logger.error('Error was occurred by video handling: ' + ex.args[0])
            video = 'Видео нет'
        return video

    def get_brand(self,url,brand_name):
        soup = self.parse_link(url)
        logger.info(url)
        a = soup.find('a', href=True, attrs={'class': ['tile-hover-target'], })
        soup = self.parse_link('https://www.ozon.ru' + str(a['href']))
        brand = soup.find('a', attrs={'class': 'b1g3'}, href=True)
        if brand is not None:
            logger.info(brand['href'])
            logger.info('brand is ' + brand['href'])
        else:
            logger.error('brand is NoneType')
            soup = self.parse_link(url)
            a = soup.findAll('a', href=True, attrs={'class': ['tile-hover-target'], })
            for elem in a:
                logger.info(elem['href'])
                soup = self.parse_link('https://www.ozon.ru' + str(elem['href']))
                item_brand = soup.find('a', attrs={'class': 'b1g3'}, href=True)
                if item_brand is not None and fuzz.partial_ratio(brand_name, str(item_brand['href'])) > 80:
                    brand = item_brand
                    logger.info(item_brand['href'])
                    logger.info('brand is ' + item_brand['href'])
                    return brand

        return brand

    def get_categories(self,brand, chat_id, message_id):
        cat_item_links = []
        telegram_bot.edit_message_text('Идет обработка: получаем ссылки на товар', chat_id, message_id)
        soup = self.parse_link(brand['href'])
        a = str(soup).find('"totalPages"') + len('"totalPages"')
        b = str(soup).find('},"context"')
        script_id = str(soup)[str(soup).find("state-searchResultsV2-"):str(soup).find("state-searchResultsV2-")+
                                                                       len('state-searchResultsV2-??????-default-1')]
        logger.info(str(soup)[a + 1:b] + ' pages')
        print(script_id)
        for i in range(1, int(str(soup)[a+1:b])+1):
            logger.info(brand['href'])
            try:
                soup = self.parse_link(brand['href'] + '?page=' + str(i))
                scr = soup.find('div', attrs={'id':str(script_id)}) # ,'type': 'application/json'})
                for e, v in enumerate(loads(scr['data-state'])['items']):
                    logger.info(v['link'] +': '+v['cellTrackingInfo']['brand'])
                    logger.info(v['link'] +': '+v['cellTrackingInfo']['brand'])
                    logger.info(v['link'])
                    cat_item_links.append('https://www.ozon.ru' + str(v['link']))
            except (AttributeError, KeyError) as ex:
                error_logger.error('Error via parsing categories: ' + ex.args[0])
        return cat_item_links

    def start(self, data, chat_id, message_id):
        if 'http' not in data[str(chat_id)]['brand']:
            self.link = 'https://www.ozon.ru/search/?from_global=true&text='
            print(self.link + data[str(chat_id)]['brand'])
            self.parse_data(self.link + data[str(chat_id)]['brand'], chat_id, message_id, data[str(chat_id)]['brand'])
        else:
            self.parse_data(data[str(chat_id)]['brand'], chat_id, message_id, data[str(chat_id)]['brand'])
        return 'ok'


class WildBerriesSite(MasterClass):
    def price_changes(self, soup, chat_id, message_id):
        for script in soup.findAll('script', attrs={'type': 'text/javascript'}):
            try:
                if 'google_tag_params' in script.string:
                    left = script.string.find('google_tag_params') + 20
                    right = script.string.find('};')
                    data = loads(script.string[left:right+1])
                    #data = loads(script.string[script.string.find('google_tag_params') + 20:script.string.find(';')])
                    if 'Discount' in data:
                        new = data['Value'][0]
                        logger.info(data['Value'])
                        price = 'Цена на товар составляет {0}'.format(new)
                        logger.info(price)
                    else:
                        logger.info(data['Value'])
                        cur = data['Value'][0]
                        logger.info(data['Value'])
                        price = 'Цена на товар составляет {0} руб'.format(cur)
                        logger.info(price)
            except (AttributeError, KeyError, TypeError, decoder.JSONDecodeError) as ex:
                    error_logger.error('Error was occurred by price change handling: ' + ex.args[0])
        logger.info(price)
        return price

    def get_sku(self, soup, chat_id, message_id):
        sku = ''
        try:
            span = soup.find('div', attrs={'class': 'article'}).text
            logger.info(str(span).replace('\n', '').replace('            ', ''))
            sku = str(span).replace('\n', '').replace('            ', '')
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by sku searching: ' + ex.args[0])
        return sku

    def item_in_stock(self,soup, chat_id, message_id):
        information = ''
        try:
            information = 'В наличии'
            for button in soup.findAll('button', attrs={'class': 'c-btn-main-lg-v1 j-add-to-wait'}):
                if 'hide' not in button['class']:
                    if 'в лист ожидания' in button.text.lower():
                        information = "Товар закончился, либо остались только некоторые варианты"
            logger.info(information)
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by item in stock searching: ' + ex.args[0])
        return information

    def reviews_rating(self,soup, chat_id, message_id):
        reviews = ''
        rating = ''
        try:
            rev = soup.find('meta', attrs={'itemprop': 'reviewCount'})
            rat = soup.find('meta', attrs={'itemprop': 'ratingValue'})
            if rev is not None:
                logger.info(rev['content'])
                reviews = rev['content']
            else:
                logger.info('rev is 0')
                reviews = '0'
            if rat is not None:
                logger.info(rat['content'])
                rating = rat['content']
            else:
                logger.info('rat is 0')
                rating = '0'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by reviews/rating handling: ' + ex.args[0])
        return reviews, rating

    def perfect_name(self,soup, chat_id, message_id):
        name = ''
        try:
            brand_name = soup.find('meta', attrs={'itemprop': 'name'})
            if brand_name is not None:
                logger.info(brand_name['content'])
                name = brand_name['content']
            else:
                logger.info('Имя отсуствует')
                name = 'Имя отсуствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by name handling: ' + ex.args[0])
        return name

    def description(self,soup, chat_id, message_id):
        desc = ''
        try:
            brand_desc = soup.find('meta', attrs={'itemprop': 'description'})
            if brand_desc is not None:
                logger.info(brand_desc['content'])
                desc = 'Описание добавлено'
            else:
                logger.info('Описание отсутствует')
                desc = 'Описание отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by description handling: ' + ex.args[0])
        return desc

    def get_certificate(self,soup, chat_id, message_id):
        cert = ''
        try:
            certificate = soup.find('a', attrs={'class': 'spec-actions-link'})
            if certificate is not None:
                logger.info(certificate.text)
                cert = certificate.text
            else:
                logger.info('Сертификат отсутствует')
                cert = 'Сертификат отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by cert handling: ' + ex.args[0])
        return cert

    def product_image(self,soup, chat_id, message_id):
        image = ''
        try:
            image_link = soup.find('meta', attrs={'property': 'og:image'})
            if image_link is not None:
                logger.info('Фото есть')
                logger.info(image_link['content'])
                image = 'Фото в наличии'
            else:
                logger.info('Фото отсутствует')
                image = 'Фото отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by image handling: ' + ex.args[0])
        return image

    def product_video(self,soup, chat_id, message_id):
        video = ''
        try:
            video_link = soup.find('meta', attrs={'property': 'og:video'})
            if video_link is not None:
                logger.info('Видео есть')
                logger.info(video_link['content'])
                video = 'Видео в наличии'
            else:
                logger.info('Видео отсутствует')
                video = 'Видео отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by video handling: ' + ex.args[0])
        return video

    def get_brand(self,url, brand_name):
        try:
            soup = self.parse_link(url)
            a = soup.find('a', href=True, attrs={'class': ['ref_goods_n_p', 'j-open-full-product-card']})
            logger.info(a['href'])
            soup = self.parse_link(str(a['href']))
            brand = soup.find('a', attrs={'id': 'brandBannerImgRef'}, href=True)
            logger.info('brand is ' + brand['href'])
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by brand handling: ' + ex.args[0])
        return brand

    def get_categories(self, brand, chat_id, message_id):
        cat_item_links = []
        telegram_bot.edit_message_text('Идет обработка: получаем ссылки на товар', chat_id, message_id)
        soup = self.parse_link(brand['href'])
        banners = soup.findAll('a', attrs={'class': ['j-banner-shown-stat j-banner-click-stat j-banner']},
                              href=True)
        if len(banners) != 0:
            brand_links = []
            for banner in banners:
                brand_links.append('https://www.wildberries.ru' + banner['href'])
            for i,v in enumerate(brand_links):
                logger.info(v)
                try:
                    soup = self.parse_link(v)
                    ulrs = soup.findAll('a', attrs={'class': ['ref_goods_n_p j-open-full-product-card']}, href=True)
                    for url in ulrs:
                        if url['href'] not in cat_item_links and 'https://www.wildberries.ru/catalog' in url['href']:
                            cat_item_links.append(url['href'])
                except (AttributeError, KeyError, TypeError) as ex:
                    error_logger.error('Error via parsing categories: ' + ex.args[0])
        else:
            soup = self.parse_link(brand['href'] + '?page=1')
            a = soup.find('a', attrs={'class': 'pagination-next'}, href=True)
            if a is not None:
                while a is not None:
                    try:
                        ulrs = soup.findAll('a', attrs={'class': ['ref_goods_n_p j-open-full-product-card']}, href=True)
                        for url in ulrs:
                            if url['href'] not in cat_item_links and 'https://www.wildberries.ru/catalog' in url['href']:
                                cat_item_links.append(url['href'])
                        soup = self.parse_link('https://www.wildberries.ru' + a['href'])
                        a = soup.find('a', attrs={'class': 'pagination-next'}, href=True)
                    except (AttributeError, KeyError, TypeError) as ex:
                        error_logger.error('Error via parsing categories: ' + ex.args[0])
            else:
                try:
                    ulrs = soup.findAll('a', attrs={'class': ['ref_goods_n_p j-open-full-product-card']}, href=True)
                    for url in ulrs:
                        if url['href'] not in cat_item_links and 'https://www.wildberries.ru/catalog' in url['href']:
                            cat_item_links.append(url['href'])
                    soup = self.parse_link('https://www.wildberries.ru' + a['href'])
                    #a = soup.find('a', attrs={'class': 'pagination-next'}, href=True)
                except (AttributeError, KeyError, TypeError) as ex:
                    error_logger.error('Error via parsing categories: ' + ex.args[0])
        return cat_item_links

    def start(self, data, chat_id, message_id):
        if 'http' not in data[str(chat_id)]['brand']:
            self.link = 'https://www.wildberries.ru/catalog/0/search.aspx?search={0}&sort=popular'
            print(self.link.format(data[str(chat_id)]['brand']))
            self.parse_data(self.link.format(data[str(chat_id)]['brand']), chat_id, message_id, data[str(chat_id)]['brand'])
        else:
            self.parse_data(data[str(chat_id)]['brand'], chat_id, message_id, data[str(chat_id)]['brand'])
        return 'ok'


class GoodsSite(MasterClass):

    def price_changes(self, soup, chat_id, message_id):
        price=''
        for div in soup.findAll('div', attrs={'class': 'price__final'}):
            try:
                price = div.text.replace('₽', 'р')
            except (AttributeError, KeyError, TypeError, decoder.JSONDecodeError) as ex:
                    error_logger.error('Error was occurred by price change handling: ' + ex.args[0])
        logger.info(price)
        return price

    def get_sku(self, soup, chat_id, message_id):
        sku = ''
        for component in soup.findAll('component', attrs={'is': 'leaveReview'}):
            try:
                sku = component['product-id']
            except (AttributeError, KeyError, TypeError) as ex:
                error_logger.error('Error was occurred by sku searching: ' + ex.args[0])
        return sku

    def item_in_stock(self,soup, chat_id, message_id):
        information = ''
        try:
            information = 'В наличии'
            div = soup.find('div', attrs={'class': 'prod--disabled-caption'})
            if div is not None:
                information = 'Нет в наличии'
            logger.info(information)
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by item in stock searching: ' + ex.args[0])
        return information

    def reviews_rating(self,soup, chat_id, message_id):
        reviews = ''
        rating = ''
        try:
            rev = soup.find('span', attrs={'class': 'tooltipster card-prod--reviews-count'})
            rat = soup.find('a', attrs={'class': 'card-prod--reviews'})
            if rev is not None:
                logger.info(rev.text.replace("\n","").strip().replace('(','').replace(')',''))
                reviews = rev.text.replace("\n","").strip().replace('(','').replace(')','')
            else:
                logger.info('rev is 0')
                reviews = '0'
            if rat is not None:
                logger.info(rat.text.replace("\n","").strip())
                rating = rat.text.replace("\n","").strip()
                print('rat is ' + rating)
            else:
                logger.info('rat is 0')
                rating = '0'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by reviews/rating handling: ' + ex.args[0])
        return reviews, rating

    def perfect_name(self,soup, chat_id, message_id):
        name = ''
        try:
            brand_name = soup.find('h1', attrs={'itemprop': 'name'})
            if brand_name is not None:
                logger.info(brand_name.text)
                name = brand_name.text
            else:
                logger.info('Имя отсуствует')
                name = 'Имя отсуствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by name handling: ' + ex.args[0])
        return name

    def description(self,soup, chat_id, message_id):
        desc = ''
        try:
            brand_desc = soup.find('div', attrs={'itemprop': 'description'})
            if brand_desc is not None:
                logger.info('Описание добавлено')
                desc = brand_desc.text.replace('\n','')
            else:
                logger.info('Описание отсутствует')
                desc = 'Описание отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by description handling: ' + ex.args[0])
        return desc

    def get_certificate(self,soup, chat_id, message_id):
        cert = ''
        try:
            certificate = soup.find('div', attrs={'class': 'item-custom-badge'})
            if certificate is not None:
                logger.info(certificate.text)
                cert = certificate.text
            else:
                logger.info('Сертификат отсутствует')
                cert = 'Сертификат отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by cert handling: ' + ex.args[0])
        return cert

    def product_image(self,soup, chat_id, message_id):
        image = ''
        try:
            image_link = soup.find('component', attrs={'is': 'imageZoomSlider'})
            if image_link[':images'] is not None:
                logger.info('Фото есть')
                image = 'Фото в наличии'
            else:
                logger.info('Фото отсутствует')
                image = 'Фото отсутствует'
        except (AttributeError, KeyError, TypeError) as ex:
            error_logger.error('Error was occurred by image handling: ' + ex.args[0])
        return image

    def product_video(self,soup, chat_id, message_id):
        video = 'Видео отсутствует'
        return video

    def get_categories(self, brand, chat_id, message_id):
        cat_item_links = []
        telegram_bot.edit_message_text('Идет обработка: получаем ссылки на товар', chat_id, message_id)
        print('brand is ' + str(brand) )
        soup = self.parse_link(brand['href'])
        a = str(soup)[str(soup).find('"pagesCount":'):str(soup).find('"pagesCount":') + 16]
        pages = int(a[a.find(':') + 1:a.find(',')])
        for i in range(1,pages+1):
            try:
                for link in soup.findAll('a', attrs={'class': 'ddl_product_link', 'data-list-id': 'mainSearch'}):
                    logger.info('https://goods.ru' + link['href'])
                    cat_item_links.append('https://goods.ru' + link['href'])
            except (AttributeError, KeyError, TypeError) as ex:
                error_logger.error('Error via parsing categories: ' + ex.args[0])
        return cat_item_links

    def start(self, data, chat_id, message_id):
        if 'http' not in data[str(chat_id)]['brand']:
            self.link = 'https://goods.ru/catalog/page-1/?q={}'
            print(self.link.format(data[str(chat_id)]['brand']))
            self.parse_data(self.link.format(data[str(chat_id)]['brand']), chat_id, message_id, data[str(chat_id)]['brand'])
        else:
            self.parse_data(data[str(chat_id)]['brand'], chat_id, message_id, data[str(chat_id)]['brand'])
        return 'ok'