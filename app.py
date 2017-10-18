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
        if index == 15:
            return content
        if head in data['href']:
            link = data['href']
        else:
            link = head + data['href']
        content += '{}\n\n'.format(link)
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
        if event.message == "抽":
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
		
		else if event.message == "蘋果":
		content = apple_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0


if __name__ == "__main__":
    app.run()