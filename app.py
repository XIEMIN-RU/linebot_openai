from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# --- 1. 初始化計數器變數 ---
msg_count = 0

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
    # --- 2. 宣告使用全域變數 ---
    global msg_count
    
    text1 = event.message.text
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
        # --- 3. 成功解析回覆後，計數器加 1 ---
        msg_count += 1
        
        # 可選：如果你想在後台 Terminal 看到累計次數
        print(f"目前累計傳送訊息數：{msg_count}")
        
    except:
        ret = '發生錯誤！'
        
    reply_with_count = f"{ret}\n\n(累計對話次數：{msg_count})"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_with_count))

# --- 4. 可選：新增一個網頁路徑來查看計數 ---
@app.route('/count')
def show_count():
    return f"目前 OpenAI 共傳送了 {msg_count} 則訊息。"

if __name__ == '__main__':
    app.run()
