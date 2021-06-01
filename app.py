
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

import gspread
from oauth2client.service_account import ServiceAccountCredentials



scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client = gspread.authorize(creds)
sheet = client.open("English_test")
sheet_problem = sheet.get_worksheet(0)
sheet_option = sheet.get_worksheet(1)
sheet_id = sheet.get_worksheet(2)
sheet_name = sheet.get_worksheet(3)

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
    total_num = int(sheet_id.cell(100,1).value)
    registered = False
    no = 0
    login_state = 0

    #check registration state
    if total_num != 0:
        for i in range(1,total_num + 1):
            if sheet_id.cell(i,1).value == user_id:
                no = i
                registered = True

    if not registered:
        no = total_num + 1
        sheet_id.update_cell(no, 1, user_id)
        sheet_id.update_cell(no, 2, str(0))
        sheet_id.update_cell(100, 1, str(no))
        registered = True

    login_state = int(sheet_id.cell(no,2).value)
    # 0:id reg / 1:name in / 2:name confirm / 3:start
                
    if login_state == 0 or '重新填寫' in msg:
        sheet_id.update_cell(no, 2, str(1))
        message = TextSendMessage(text= '請輸入姓名')
        line_bot_api.reply_message(event.reply_token, message)

    if login_state == 1:
        sheet_id.update_cell(no, 2, str(2))
        student_num = int(sheet_name.cell(1,1).value)
        name = msg
        seatnum = ''
        _class = ''
        name_exist = False
        
        for i in range (1,student_num + 2):
                if sheet_name.cell(i,1).value == msg:
                    seatnum = sheet_name.cell(i,3).value
                    _class = sheet_name.cell(i,2).value
                    name_exist = True
                    
        if name_exist:
            sheet_id.update_cell(no, 3, _class)
            sheet_id.update_cell(no, 4, seatnum)
            sheet_id.update_cell(no, 5, name)
            sheet_id.update_cell(no, 6, '0')
            for i in range (7, 27):
                sheet_id.update_cell(no, i, '0')
            sheet_id.update_cell(no, 6, '0')
            message = TemplateSendMessage(
                alt_text='確認班級座號姓名？',
                template=ConfirmTemplate(
                    text="你是"+ _class + ' ' + seatnum + '號 ' + name + '嗎?',
                    actions=[
                        PostbackTemplateAction(
                            label="確認",
                            text="確認資料 開始聽力測驗 請點開影片檔案 並選出你聽到的單字 如果沒有影片出現時 請輸入#重新載入題目 並注意重複作答系統將不予計分",
                            data="會員註冊"
                        ),
                        MessageTemplateAction(
                            label="重新填寫",
                            text="重新填寫"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            sheet_id.update_cell(no, 2, str(1))
            message = TextSendMessage(text= '查無此人 請重新輸入')
            line_bot_api.reply_message(event.reply_token, message)
            

    if '確認資料' in msg:
        message = VideoSendMessage(
            original_content_url='https://imgur.com/bkm2cPn.mp4', 
            preview_image_url='https://imgur.com/2CJYX6c.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'usually', text = '#1 your ans : usually\ncorrect ans : usually\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'watch TV', text = '#1 your ans:watch TV\ncorrect ans:usually')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'play sports', text = '#1 your ans:play sports\ncorrect ans:usually')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#1' in msg or (sheet_id.cell(no,7).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,7).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 7, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/FDujC2X.mp4', 
            preview_image_url='https://imgur.com/4ARs5aO.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'afternoon', text = '#2 your ans : afternoon\ncorrect ans : after school')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'after school', text = '#2 your ans : after school\ncorrect ans : after school\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'after work', text = '#2 your ans : after work\ncorrect ans : after school')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#2' in msg or (sheet_id.cell(no,8).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,8).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 8, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/0v0MtpW.mp4', 
            preview_image_url='https://imgur.com/hZHDi6D.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'watch movies', text = '#3 your ans : watch movies\ncorrect ans : watch TV')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'new TV', text = '#3 your ans : new TV\ncorrect ans : watch TV')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'watch TV', text = '#3 your ans : watch TV\ncorrect ans : watch TV\ngood job!')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    if '#3' in msg or (sheet_id.cell(no,9).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,9).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 9, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/Bp8x0Ll.mp4', 
            preview_image_url='https://imgur.com/t7keRVy.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'walk the dog', text = '#4 your ans : walk the dog\ncorrect ans : walk the dog\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'walk in the park', text = '#4 your ans : walk in the park\ncorrect ans : walk the dog')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'cats and dogs', text = '#4 your ans : cats and dogs\ncorrect ans : walk the dog')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#4' in msg or (sheet_id.cell(no,10).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,10).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 10, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/mITn8uT.mp4', 
            preview_image_url='https://imgur.com/st821yg.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'save the world', text = '#5 your ans : save the world\ncorrect ans : surf the internet')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'surf the internet', text = '#5 your ans : surf the internet\ncorrect ans : surf the internet\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'surf is up', text = '#5 your ans : surf is up\ncorrect ans : surf the internet')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#5' in msg or (sheet_id.cell(no,11).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,11).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 11, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/cRpfUGP.mp4', 
            preview_image_url='https://imgur.com/tOUdChN.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'ride a bike', text = '#6 your ans : ride a bike\ncorrect ans : read books')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'read papers', text = '#6 your ans : read papers\ncorrect ans : read books')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'read books', text = '#6 your ans : read books\ncorrect ans : read books\ngood job!')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#6' in msg or (sheet_id.cell(no,12).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,12).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 12, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/RdhTRe4.mp4', 
            preview_image_url='https://imgur.com/7ezNT5R.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'play the piano', text = '#7 your ans : play the piano\ncorrect ans : play sports')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'play sports', text = '#7 your ans : play sports\ncorrect ans : play sports\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'play the sport', text = '#7 your ans : play the sport\ncorrect ans : play sports')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#7' in msg or (sheet_id.cell(no,13).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,13).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 13, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/LDIemg1.mp4', 
            preview_image_url='https://imgur.com/BgRCXLX.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'listen to music', text = '#8 your ans : listen to music\ncorrect ans : listen to music\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'list of music', text = '#8 your ans : list of music\ncorrect ans : listen to music')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = "that's the music", text = "#8 your ans : that's the music\ncorrect ans : listen to music")
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#8' in msg or (sheet_id.cell(no,14).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,14).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 14, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/lVxpNDp.mp4', 
            preview_image_url='https://imgur.com/fdgthsL.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'do housework', text = '#9 your ans : do housework\ncorrect ans : do my homework')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'do me a favor', text = '#9 your ans : do me a favor\ncorrect ans : do my homework')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = "do my homework", text = "#9 your ans : do my homework\ncorrect ans : do my homework\ngood job!")
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#9' in msg or (sheet_id.cell(no,15).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,15).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 15, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/nRqfbNB.mp4', 
            preview_image_url='https://imgur.com/qRmhPT1.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'some time', text = '# 10 your ans : some time\ncorrect ans : sometimes')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'sometimes', text = '# 10 your ans : sometimes\ncorrect ans : sometimes\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = "some times", text = "# 10 your ans : some times\ncorrect ans : sometimes")
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)


    
    if '# 10' in msg or (sheet_id.cell(no,16).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,16).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 16, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 11',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/E4wtVGJ.png',
                title = "選擇填入空格的詞句",
                text = "I ____ do homework after school.",
                actions=[
                    MessageTemplateAction(
                        label = 'like',
                        text = '# 11 your ans : like\ncorrect ans : usually'
                    ),
                    MessageTemplateAction(
                        label = 'usually',
                        text = '# 11 your ans : usually\ncorrect ans : usually\ngood job!'
                    ),
                    MessageTemplateAction(
                        label= 'have',
                        text = '# 11 your ans : have\ncorrect ans : usually'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    
    if '# 11' in msg or (sheet_id.cell(no,17).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,17).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 17, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 12',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/Rp9LKBa.png',
                title = "選擇填入空格的詞句",
                text = "Jack usually ___ the dog in the morning.",
                actions=[
                    MessageTemplateAction(
                        label = 'play the piano',
                        text = '# 12 your ans : play the piano\ncorrect ans : walks'
                    ),
                    MessageTemplateAction(
                        label = 'listen',
                        text = '# 12 your ans : listen\ncorrect ans : walks'
                    ),
                    MessageTemplateAction(
                        label= 'walks',
                        text = '# 12 your ans : walks\ncorrect ans : walks\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 12' in msg or (sheet_id.cell(no,18).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,18).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 18, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 13',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/vriIBqw.png',
                title = "選擇填入空格的詞句",
                text = "Mom and I sometimes _____ the internet at home.",
                actions=[
                    MessageTemplateAction(
                        label = 'browse',
                        text = '# 13 your ans : browse\ncorrect ans : surf'
                    ),
                    MessageTemplateAction(
                        label = 'look',
                        text = '# 13 your ans : look\ncorrect ans : surf'
                    ),
                    MessageTemplateAction(
                        label= 'surf',
                        text = '# 13 your ans : surf\ncorrect ans : surf\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 13' in msg or (sheet_id.cell(no,19).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,19).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 19, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 14',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/2ktphE6.png',
                title = "選擇填入空格的詞句",
                text = "______ you usually play sports in after work?",
                actions=[
                    MessageTemplateAction(
                        label = 'Do',
                        text = '# 14 your ans : Do\ncorrect ans : Do\ngood job!'
                    ),
                    MessageTemplateAction(
                        label = 'Does',
                        text = '# 14 your ans : Does\ncorrect ans : Do'
                    ),
                    MessageTemplateAction(
                        label= 'Are',
                        text = '# 14 your ans : Are\ncorrect ans : Do'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 14' in msg or (sheet_id.cell(no,20).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,20).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 20, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 15',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/NSYMEMS.png',
                title = "選擇填入空格的詞句",
                text = "________ Lily ________ homework after school?",
                actions=[
                    MessageTemplateAction(
                        label = 'Do does',
                        text = '# 15 your ans : Do does\ncorrect ans : Does do'
                    ),
                    MessageTemplateAction(
                        label = 'Do do',
                        text = '# 15 your ans : Do do\ncorrect ans : Does do'
                    ),
                    MessageTemplateAction(
                        label= 'Does do',
                        text = '# 15 your ans : Does do\ncorrect ans : Does do\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    if '# 15' in msg or (sheet_id.cell(no,21).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,21).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 21, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 16',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/9ksK0is.png',
                title = "選擇填入空格的詞句",
                text = "_______ does your brother do after scool?",
                actions=[
                    MessageTemplateAction(
                        label = 'When',
                        text = '# 16 your ans : When\ncorrect ans : What'
                    ),
                    MessageTemplateAction(
                        label = 'Where',
                        text = '# 16 your ans : Where\ncorrect ans : What'
                    ),
                    MessageTemplateAction(
                        label= 'What',
                        text = '# 16 your ans : What\ncorrect ans : What\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 16' in msg or (sheet_id.cell(no,22).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,22).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 22, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 17',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/Y1vvXux.png',
                title = "選擇填入空格的詞句",
                text = "A: Does Amy read books after school? B: Yes, _____ _____. ",
                actions=[
                    MessageTemplateAction(
                        label = 'she does',
                        text = '# 17 your ans : she does\ncorrect ans : she does\ngood job!'
                    ),
                    MessageTemplateAction(
                        label = 'he does',
                        text = '# 17 your ans : he does\ncorrect ans : she does'
                    ),
                    MessageTemplateAction(
                        label= 'she do',
                        text = '# 17 your ans : she do\ncorrect ans : she does'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 17' in msg or (sheet_id.cell(no,23).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,23).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 23, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 18',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/SJoGeQT.png',
                title = "選擇填入空格的詞句",
                text = "A: What do you do in the morning? B:_______ listen to music.",
                actions=[
                    MessageTemplateAction(
                        label = 'You',
                        text = '# 18 your ans : You\ncorrect ans : I'
                    ),
                    MessageTemplateAction(
                        label = 'He',
                        text = '# 18 your ans : He\ncorrect ans : I'
                    ),
                    MessageTemplateAction(
                        label= 'I',
                        text = '# 18 your ans : I\ncorrect ans : I\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 18' in msg or (sheet_id.cell(no,24).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,24).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 24, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 19',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/JQZd2b9.png',
                title = "選擇填入空格的詞句",
                text = "Do you ________ walk the dog in the park?",
                actions=[
                    MessageTemplateAction(
                        label = 'want',
                        text = '# 19 your ans : want\ncorrect ans : sometimes'
                    ),
                    MessageTemplateAction(
                        label = 'sometimes',
                        text = '# 19 your ans : sometimes\ncorrect ans : sometimes\ngood job!'
                    ),
                    MessageTemplateAction(
                        label= 'no',
                        text = '# 19 your ans : no\ncorrect ans : sometimes'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 19' in msg or (sheet_id.cell(no,25).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,25).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 25, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 20',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/goWtiMu.png',
                title = "選擇填入空格的詞句",
                text = "I ______ usually watch TV after school.",
                actions=[
                    MessageTemplateAction(
                        label = "don't",
                        text = "# 20 your ans : don't\ncorrect ans : don't\ngood job!"
                    ),
                    MessageTemplateAction(
                        label = "no",
                        text = "# 20 your ans : no\ncorrect ans : don't"
                    ),
                    MessageTemplateAction(
                        label = "not",
                        text = "# 20 your ans : not\ncorrect ans : don't"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 20' in msg or (sheet_id.cell(no,26).value == '0' and '#' in msg):
        if 'good job!' in msg and sheet_id.cell(no,26).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        sheet_id.update_cell(no, 26, '1')
        message = TemplateSendMessage(
            alt_text = 'finished!',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/k1jt05e.png',
                title = "作答完成",
                text = "你的分數" + sheet_id.cell(no,6).value,
                actions=[
                    MessageTemplateAction(
                        label = "我知道了!",
                        text = "完成作答"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)


    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
