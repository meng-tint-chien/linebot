from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('y9AC19uX8VOLcgpFZpJRjx2v9LJ9aDSUCgvHZhnhdijtDbSKhvcayE9hPRwFlCRjUvMVPCZYox1rYMwaekLeEVyJ0gDv9cTA0dGdRyigKk5Qjos+gwUDsxI2H9IP7SpgfKyGmakdqUpI+uRRVPiaKgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3b1a6196ac1e2c07c215023f0287be4b')


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()