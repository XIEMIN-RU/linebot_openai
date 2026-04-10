from flask import Flask, request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 1. 建立一個全域變數來當作計數器，初始值為 0
openai_msg_counter = 0

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
    # 2. 宣告在這裡要使用全域變數
    global openai_msg_counter 
    
    text1 = event.message.text

    # [額外功能] 設定一個特定指令來查看目前計數
    if text1 == "查看計數":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"報告！OpenAI 目前共傳了 {openai_msg_counter} 則訊息。")
        )
        return # 提早結束，不把這個指令傳給 OpenAI

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
        temperature=1,
    )
    
    try:
        ret = response['choices'][0]['message']['content'].strip()
        
        # 3. 若成功取得 OpenAI 的回覆，計數器 +1
        openai_msg_counter += 1
        
        # (選擇性) 你也可以讓它印在伺服器的終端機後台上方便觀察
        print(f"目前 OpenAI 已傳送總訊息數：{openai_msg_counter}")
        
    except Exception as e:
        ret = '發生錯誤！'
        print(f"Error: {e}") # 印出錯誤訊息方便 debug

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
