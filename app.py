
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import tempfile, os
import datetime
import time
import traceback
#======python的函數庫==========

#======google試算表======
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client = gspread.authorize(creds)
sheet = client.open("Energy_Chart")
sheet1 = sheet.get_worksheet(0)
#======google試算表======


#=============Linebot==================
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi('TOi303gvTtC4ncGBIaUJmSLDvjRZrnbzpBuAr1f2SMh8WtjIXmTzFH1ALHzqpNruGPYT+c2KGNbIeDM5Hzn9fjR5m3ql1wvyFGPNk956PuA9U3HmcInqabuiPpxwRX/77UiN2iiF2aRZ2cKEg9LREwdB04t89/1O/w1cDnyilFU=')

# Channel Secret
handler = WebhookHandler('57853dccc508c4b194e42454586e9969')

# 監聽所有來自 /callback 的 Post Request
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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
@static_vars(counter=0)
def handle_message(event):
    
    msg = event.message.text
    user_id = event.source.user_id

    if '家庭用電資訊' in msg:
        message = TemplateSendMessage(
            alt_text = '家庭用電資訊',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/laWWGSw.png',
                title = "家庭用電資訊",
                text = " ",
                actions=[
                    MessageTemplateAction(
                        label = '查詢本月用電',
                        text = '查詢本月用電'
                    ),
                    MessageTemplateAction(
                        label = '查詢本月電費',
                        text = '查詢本月電費'
                    ),
                    MessageTemplateAction(
                        label= '用電趨勢查詢',
                        text = '用電趨勢查詢'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif '查詢本月用電' in msg:
        message = TextSendMessage(text= '本月平均用電功率 : 2743 W\n相當 5 個電鍋同時運作')
        line_bot_api.reply_message(event.reply_token, message)
    elif '查詢本月電費' in msg:
        message = TextSendMessage(text= '查詢本月電費 : 5472 元\n37%離峰時間\n36%半離峰時間\n25%尖峰時間')
        line_bot_api.reply_message(event.reply_token, message)
    elif '用電趨勢查詢' in msg:
        message = ImageSendMessage(
            original_content_url = 'https://imgur.com/wwyIC4Z.png',
            preview_image_url = 'https://imgur.com/wwyIC4Z.png'
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif '電動車用電資訊' in msg:
        message = TemplateSendMessage(
            alt_text = '電動車用電資訊',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/wNVluYP.png',
                title = "電動車用電資訊",
                text = " ",
                actions=[
                    MessageTemplateAction(
                        label = '充電樁電費',
                        text = '充電樁電費'
                    ),
                    MessageTemplateAction(
                        label = '電動車充電狀況',
                        text = '電動車充電狀況'
                    ),
                    MessageTemplateAction(
                        label= '啟動節費車充方案',
                        text = '啟動節費車充方案'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif '充電樁電費' in msg:
        message = TextSendMessage(text= '本月充電樁電費 : 1614元\n智能充電模式節省 : 120 元')
        line_bot_api.reply_message(event.reply_token, message)
    elif '電動車充電狀況' in msg:
        message = TextSendMessage(text= '電動車充電狀況 : 充電中 \n餘電 : 30%')
        line_bot_api.reply_message(event.reply_token, message)
    elif '啟動節費車充方案' in msg:
        sheet1.update_cell(1, 3, str(1))
        message = TextSendMessage(text= '已啟動智能充電模式')
        line_bot_api.reply_message(event.reply_token, message)
    # elif '家電用電資訊' in msg:
    #     message = TextSendMessage(text= 'https://reurl.cc/bkrDb3')
    #     line_bot_api.reply_message(event.reply_token, message)
    elif '家電用電圖表' in msg:
        message = TemplateSendMessage(
            alt_text='圖片旋轉木馬',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url="https://imgur.com/sGyHay0.png",
                        action=MessageTemplateAction(
                            label="冰箱",
                            text="尚未連接冰箱"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/aPCse0f.png",
                        action=MessageTemplateAction(
                            label="電視",
                            text="尚未連接電視"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/5WE80aO.png",
                        action=MessageTemplateAction(
                            label="冷氣",
                            text="尚未連接冷氣"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/1R0p3XE.png",
                        action=MessageTemplateAction(
                            label="洗衣機",
                            text="尚未連接洗衣機"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/aiuqDow.png",
                        action=URITemplateAction(
                            label="手機充電",
                            uri="https://thingspeak.com/channels/1679927/charts/3?bgcolor=%23ffffff&color=%23d62020&dynamic=true&results=60&type=line&update=15"
                        )
                    )
                ]
            )
    )
    elif '家電用電數據' in msg:
        n = int(sheet1.cell(1, 2).value)
        power = sheet1.cell(n, 4).value
        voltage = sheet1.cell(n, 5).value
        current = sheet1.cell(n, 6).value
        message = TemplateSendMessage(
            alt_text='圖片旋轉木馬',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url="https://imgur.com/sGyHay0.png",
                        action=MessageTemplateAction(
                            label="冰箱",
                            text="尚未連接冰箱"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/aPCse0f.png",
                        action=MessageTemplateAction(
                            label="電視",
                            text="尚未連接電視"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/5WE80aO.png",
                        action=MessageTemplateAction(
                            label="冷氣",
                            text="尚未連接冷氣"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/1R0p3XE.png",
                        action=MessageTemplateAction(
                            label="洗衣機",
                            text="尚未連接洗衣機"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/aiuqDow.png",
                        action=MessageTemplateAction(
                            label="手機充電",
                            text= ("即時電能 : " + power + "W\n即時電壓 : " + voltage + "V\n即時電流 : " + current + 'A')
                        )
                    )
                ]
            )
    )
    elif '進入法師的快樂商店' in msg:
        message = TemplateSendMessage(
            alt_text='圖片旋轉木馬',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url="https://imgur.com/SqOVwVe.png",
                        action=MessageTemplateAction(
                            label="雪莉 ⚡️300",
                            text="餘額不足解鎖雪莉!\n重新進入法師的快樂商店"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/KQBMPyi.png",
                        action=MessageTemplateAction(
                            label="傑哥 ⚡️500",
                            text="餘額不足解鎖雪莉!\n重新進入法師的快樂商店"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/5niCamH.png",
                        action=MessageTemplateAction(
                            label="曾晴",
                            text="使用角色 曾晴"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/DcOVNZ6.png",
                        action=MessageTemplateAction(
                            label="管爺 ⚡️400",
                            text="餘額不足解鎖管爺!\n重新進入法師的快樂商店"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url="https://imgur.com/2rkUYNt.png",
                        action=MessageTemplateAction(
                            label="HowHow ⚡️400",
                            text="餘額不足解鎖HowHow!\n重新進入法師的快樂商店"
                        )
                    )
                ]
            )
    )
    elif '使用角色' in msg:
        message = VideoSendMessage(
            original_content_url='https://imgur.com/SqDVA5E.mp4', 
            preview_image_url='https://imgur.com/O8UdrCp.png'
        )
        line_bot_api.reply_message(event.reply_token, message)
    else:
        message = TemplateSendMessage(
                alt_text='Main Menu',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://imgur.com/laWWGSw.png',
                            title='家庭用電資訊',
                            text='本月平均用電、用電趨勢圖、本月總電費',
                            actions=[
                                MessageTemplateAction(
                                    label='點我查詢',
                                    text='家庭用電資訊'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://imgur.com/wNVluYP.png',
                            title='電動車用電資訊',
                            text='充電樁電費、電動車充電狀況、啟動節費車充方案',
                            actions=[
                                MessageTemplateAction(
                                    label='點我查詢',
                                    text='電動車用電資訊'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://imgur.com/iB4vh17.png',
                            title='家電用電圖表',
                            text='查看各個家電的用電圖表',
                            actions=[
                                MessageTemplateAction(
                                    label='點我查詢',
                                    text='家電用電圖表'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://imgur.com/1R0p3XE.png',
                            title='家電用電數據',
                            text='查看各個家電的用電數據',
                            actions=[
                                MessageTemplateAction(
                                    label='點我查詢',
                                    text='家電用電數據'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://imgur.com/QlLsw6N.png',
                            title='省電大法師的神奇商店',
                            text='用你省下的電換取快樂魔法能量\n現在你有快樂代幣 256枚',
                            actions=[
                                MessageTemplateAction(
                                    label='兌換省電的快樂',
                                    text='進入法師的快樂商店'
                                )
                            ]
                        )
                    ], image_aspect_ratio = 'rectangle', image_size = 'cover'
                )
            )
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

#=============Linebot==================
