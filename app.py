from flask import Flask

app = Flask(__name__)



from flask import request, abort

from linebot import  LineBotApi, WebhookHandler

from linebot.exceptions import InvalidSignatureError

from linebot.models import MessageEvent, TextMessage, TextSendMessage

import openai

import os



openai.api_key = os.getenv('OPENAI_API_KEY')

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))

handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))



@app.route('/callback', methods=['POST'])

def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)

    try:

        handler1.handle(body, signature)

    except InvalidSignatureError:

        abort(400)

    return 'OK'



@handler1.add(MessageEvent, message=TextMessage)

def handle_message(event):

    text1=event.message.text

    response = openai.ChatCompletion.create(

       

        model="gpt-5-nano",

        messages=[

            {

                "role": "system", 

                "content": "你現在是一個古代詩人，喜歡用文言文來回答問題。"

            },

            {

                "role": "user", 

                "content": text1

            }

        ],

        temperature = 1,

    )

    try:

        ret = response['choices'][0]['message']['content'].strip()

    except:

        ret = '發生錯誤！'

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ret))



if __name__ == '__main__':

    app.run()
