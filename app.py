import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from imgurpython import ImgurClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *



app = Flask(__name__)

line_bot_api = LineBotApi('y9AC19uX8VOLcgpFZpJRjx2v9LJ9aDSUCgvHZhnhdijtDbSKhvcayE9hPRwFlCRjUvMVPCZYox1rYMwaekLeEVyJ0gDv9cTA0dGdRyigKk5Qjos+gwUDsxI2H9IP7SpgfKyGmakdqUpI+uRRVPiaKgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3b1a6196ac1e2c07c215023f0287be4b')

client_id = '9976db0687776b7'
client_secret = '145147997222a4f55998364e7470b1f348f33e93'
album_id = '6FdES'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
def apple_news():
    target_url = 'http://www.appledaily.com.tw/realtimenews/section/new/'
    head = 'http://www.appledaily.com.tw'
    print('Start parsing appleNews....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('.rtddt a'), 0):
        if index == 5:
            return content
        if head in data['href']:
            link = data['href']
        else:
            link = head + data['href']
        content += '{}\n\n'.format(link)
    return content
def ptt_beauty():
    rs = requests.session()
    res = rs.get('https://www.ptt.cc/bbs/Beauty/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    all_page_url = soup.select('.btn.wide')[1]['href']
    start_page = get_page_number(all_page_url)
    page_term = 2  # crawler count
    push_rate = 10  # 推文
    index_list = []
    article_list = []
    for page in range(start_page, start_page - page_term, -1):
        page_url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'.format(page)
        index_list.append(page_url)

    # 抓取 文章標題 網址 推文數
    while index_list:
        index = index_list.pop(0)
        res = rs.get(index, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            index_list.append(index)
            # print u'error_URL:',index
            # time.sleep(1)
        else:
            article_list = craw_page(res, push_rate)
            # print u'OK_URL:', index
            # time.sleep(0.05)
    content = ''
    for article in article_list:
        data = '[{} push] {}\n{}\n\n'.format(article.get('rate', None), article.get('title', None),
                                             article.get('url', None))
        content += data
    return content
	
def get_page_number(content):
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1


def craw_page(res, push_rate):
    soup_ = BeautifulSoup(res.text, 'html.parser')
    article_seq = []
    for r_ent in soup_.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']
            if link:
                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                rate = r_ent.find(class_="nrec").text
                url = 'https://www.ptt.cc' + link
                if rate:
                    rate = 100 if rate.startswith('爆') else rate
                    rate = -1 * int(rate[1]) if rate.startswith('X') else rate
                else:
                    rate = 0
                # 比對推文數
                if int(rate) >= push_rate:
                    article_seq.append({
                        'title': title,
                        'url': url,
                        'rate': rate,
                    })
        except Exception as e:
            # print('crawPage function error:',r_ent.find(class_="title").text.strip())
            print('本文已被刪除', e)
    return article_seq


def crawl_page_gossiping(res):
    soup = BeautifulSoup(res.text, 'html.parser')
    article_gossiping_seq = []
    for r_ent in soup.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']

            if link:
                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                url_link = 'https://www.ptt.cc' + link
                article_gossiping_seq.append({
                    'url_link': url_link,
                    'title': title
                })

        except Exception as e:
            # print u'crawPage function error:',r_ent.find(class_="title").text.strip()
            # print('本文已被刪除')
            print('delete', e)
    return article_gossiping_seq

def ptt_gossiping():
    rs = requests.session()
    load = {
        'from': '/bbs/Gossiping/index.html',
        'yes': 'yes'
    }
    res = rs.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
    soup = BeautifulSoup(res.text, 'html.parser')
    all_page_url = soup.select('.btn.wide')[1]['href']
    start_page = get_page_number(all_page_url)
    index_list = []
    article_gossiping = []
    for page in range(start_page, start_page - 2, -1):
        page_url = 'https://www.ptt.cc/bbs/Gossiping/index{}.html'.format(page)
        index_list.append(page_url)

    # 抓取 文章標題 網址 推文數
    while index_list:
        index = index_list.pop(0)
        res = rs.get(index, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            index_list.append(index)
            # print u'error_URL:',index
            # time.sleep(1)
        else:
            article_gossiping = crawl_page_gossiping(res)
            # print u'OK_URL:', index
            # time.sleep(0.05)
    content = ''
    for index, article in enumerate(article_gossiping, 0):
        if index == 5:
            return content
        data = '{}\n{}\n\n'.format(article.get('title', None), article.get('url_link', None))
        content += data
    return content
	
def movie():
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('ul.filmNextListAll a')):
        if index == 7:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
        
        if event.message.text == "蘋果":
            print("event.reply_token:", event.reply_token)
            print("event.message.text:", event.message.text)
            content = apple_news()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
            
        if event.message.text == "表特":
            content = ptt_beauty()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
            
        if event.message.text == "廢文":
            content = ptt_gossiping()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        
        if event.message.text == "電影":
            content = movie()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
			
        if event.message.text == "搞":
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="嗨嗎"))
			
        if event.message.text == "幹":
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="死屁孩"))
        if event.message.text[0] == "+":
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="http://lmgtfy.com/?q="+event.message.text))
		    
        if event.message.text == "屁孩":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/q97n3fa.png",
                preview_image_url="https://i.imgur.com/q97n3fa.png"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "死屁孩":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/z06PIVw.png",
                preview_image_url="https://i.imgur.com/z06PIVw.png"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "帥哥":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/89iGrd2.jpg",
                preview_image_url="https://i.imgur.com/89iGrd2.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "八七雯":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/y2VHmR0.jpg",
                preview_image_url="https://i.imgur.com/y2VHmR0.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "開會":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/veAX519.jpg",
                preview_image_url="https://i.imgur.com/veAX519.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "開喝":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/qbX5uQp.jpg",
                preview_image_url="https://i.imgur.com/qbX5uQp.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "港組":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/S5Hljc3.jpg",
                preview_image_url="https://i.imgur.com/S5Hljc3.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        
        if event.message.text == "操":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/qg7xrPJ.jpg",
                preview_image_url="https://i.imgur.com/qg7xrPJ.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "林寬":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/Rt9HeIp.jpg",
                preview_image_url="https://i.imgur.com/Rt9HeIp.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "先開喝":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/oaBS0bo.jpg",
                preview_image_url="https://i.imgur.com/oaBS0bo.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "郁雯揪打lol":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/T49NQfd.jpg",
                preview_image_url="https://i.imgur.com/T49NQfd.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "冠希":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/3NKN1u1.png",
                preview_image_url="https://i.imgur.com/3NKN1u1.png"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "胖":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/jeJ3iww.png",
                preview_image_url="https://i.imgur.com/jeJ3iww.png"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        if event.message.text == "英文王":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/twaSjzP.jpg",
                preview_image_url="https://i.imgur.com/twaSjzP.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "彥傑":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/OUuX08a.png",
                preview_image_url="https://i.imgur.com/OUuX08a.png"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "寬":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/XzWufEr.jpg",
                preview_image_url="https://i.imgur.com/XzWufEr.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "臭gay":
            image_message = ImageSendMessage(
                original_content_url="https://i.imgur.com/fHxlMBl.jpg",
                preview_image_url="https://i.imgur.com/fHxlMBl.jpg"
            )
            line_bot_api.reply_message(event.reply_token, image_message)
			
        if event.message.text == "給我女神照":
            print("event.reply_token:", event.reply_token)
            print("event.message.text:", event.message.text)
            client = ImgurClient(client_id, client_secret)
            images = client.get_album_images("kYTl1")
            index = random.randint(0, len(images) - 1)
            url = images[index].link
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )
            line_bot_api.reply_message(
            event.reply_token, image_message)
		
        if event.message.text == "嗨抽":
            print("event.reply_token:", event.reply_token)
            print("event.message.text:", event.message.text)
            client = ImgurClient(client_id, client_secret)
            images = client.get_album_images("n873Y")
            index = random.randint(0, len(images) - 1)
            url = images[index].link
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )
            line_bot_api.reply_message(
            event.reply_token, image_message)
        if event.message.text == "控肉抽":
            print("event.reply_token:", event.reply_token)
            print("event.message.text:", event.message.text)
            client = ImgurClient(client_id, client_secret)
            images = client.get_album_images("Z86oo")
            index = random.randint(0, len(images) - 1)
            url = images[index].link
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )
            line_bot_api.reply_message(
            event.reply_token, image_message)
        

        if event.message.text == "抽":
            print("event.reply_token:", event.reply_token)
            print("event.message.text:", event.message.text)
            client = ImgurClient(client_id, client_secret)
            images = client.get_album_images(album_id)
            index = random.randint(0, len(images) - 1)
            url = images[index].link
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )
            line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0
        


		


if __name__ == "__main__":
    app.run()