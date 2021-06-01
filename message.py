#這些是LINE官方開放的套件組合透過import來套用這個檔案上
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client = gspread.authorize(creds)
sheet = client.open("test_1_db")
sheet_loc = sheet.get_worksheet(0)
sheet_cost = sheet.get_worksheet(1)
sheet_wal = sheet.get_worksheet(2)
sheet_light = sheet.get_worksheet(3)
sheet_pass = sheet.get_worksheet(4)

#ImagemapSendMessage(組圖訊息)
def imagemap_message():
    message = ImagemapSendMessage(
        base_url="https://i.imgur.com/BfTFVDN.jpg",
        alt_text='最新的合作廠商有誰呢？',
        base_size=BaseSize(height=2000, width=2000),
        actions=[
            URIImagemapAction(
                #家樂福
                link_uri="https://tw.shop.com/search/%E5%AE%B6%E6%A8%82%E7%A6%8F",
                area=ImagemapArea(
                    x=0, y=0, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                #生活市集
                link_uri="https://tw.shop.com/search/%E7%94%9F%E6%B4%BB%E5%B8%82%E9%9B%86",
                area=ImagemapArea(
                    x=1000, y=0, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                #阿瘦皮鞋
                link_uri="https://tw.shop.com/search/%E9%98%BF%E7%98%A6%E7%9A%AE%E9%9E%8B",
                area=ImagemapArea(
                    x=0, y=1000, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                #塔吉特千層蛋糕
                link_uri="https://tw.shop.com/search/%E5%A1%94%E5%90%89%E7%89%B9",
                area=ImagemapArea(
                    x=1000, y=1000, width=1000, height=500
                )
            ),
            URIImagemapAction(
                #亞尼克生乳捲
                link_uri="https://tw.shop.com/search/%E4%BA%9E%E5%B0%BC%E5%85%8B",
                area=ImagemapArea(
                    x=1000, y=1500, width=1000, height=500
                )
            )
        ]
    )
    return message

#TemplateSendMessage - ButtonsTemplate (按鈕介面訊息)
def buttons_message():
    message = TemplateSendMessage(
        alt_text='好消息來囉～',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="是否要進行抽獎活動？",
            text="輸入生日後即獲得抽獎機會",
            actions=[
                DatetimePickerTemplateAction(
                    label="請選擇生日",
                    data="input_birthday",
                    mode='date',
                    initial='1990-01-01',
                    max='2019-03-10',
                    min='1930-01-01'
                ),
                MessageTemplateAction(
                    label="看抽獎品項",
                    text="有哪些抽獎品項呢？"
                ),
                URITemplateAction(
                    label="免費註冊享回饋",
                    uri="https://tw.shop.com/nbts/create-myaccount.xhtml?returnurl=https%3A%2F%2Ftw.shop.com%2F"
                )
            ]
        )
    )
    return message

#TemplateSendMessage - ConfirmTemplate(確認介面訊息)
def Confirm_Template():

    message = TemplateSendMessage(
        alt_text='是否註冊成為會員？',
        template=ConfirmTemplate(
            text="是否註冊成為會員？",
            actions=[
                PostbackTemplateAction(
                    label="馬上註冊",
                    text="現在、立刻、馬上",
                    data="會員註冊"
                ),
                MessageTemplateAction(
                    label="查詢其他功能",
                    text="查詢其他功能"
                )
            ]
        )
    )
    return message

#旋轉木馬按鈕訊息介面

def Carousel_Template_menu():
    message = TemplateSendMessage(
        alt_text='一則旋轉木馬按鈕訊息',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/3whWd6A.png',
                    title='ID-card location',
                    text='check last ID-CARD location',
                    actions=[
                        MessageTemplateAction(
                            label='tap to check',
                            text='check last ID-CARD location'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/Ev4ToWr.png',
                    title='Wallet location',
                    text='check present wallet location',
                    actions=[
                        MessageTemplateAction(
                            label='tap to check',
                            text='check present wallet location'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/5NqGKmh.png',
                    title='Cost',
                    text='check cost info',
                    actions=[
                        MessageTemplateAction(
                            label='tap to check',
                            text='check cost info'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/oczX1yI.png',
                    title='Light',
                    text='turn on signal light',
                    actions=[
                        MessageTemplateAction(
                            label='tap to light up',
                            text='turn on signal light'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/McGA5nL.png',
                    title='Password setting',
                    text='set wallet password',
                    actions=[
                        MessageTemplateAction(
                            label='tap to set',
                            text='set wallet password'
                        )
                    ]
                )
            ], image_aspect_ratio = 'rectangle', image_size = 'cover'
        )
    )
    return message

def Carousel_Template_off():
    message = TemplateSendMessage(
        alt_text='一則旋轉木馬按鈕訊息',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/774QQKE.png',
                    title='Turn off',
                    text='turn off the light',
                    actions=[
                        MessageTemplateAction(
                            label='tap to off',
                            text='off'
                        )
                    ]
                )
            ], image_aspect_ratio = 'rectangle', image_size = 'cover'
        )
    )
    return message

def Carousel_Template_cost():
    message = TemplateSendMessage(
        alt_text='一則旋轉木馬按鈕訊息',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/CHPYx2q.png',
                    title= '$' + sheet_cost.cell(1,8).value,
                    text='food cost',
                    actions=[
                        MessageTemplateAction(
                            label='done',
                            text='done'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/OUXtBls.png',
                    title= '$' + sheet_cost.cell(2,8).value,
                    text='clothing cost',
                    actions=[
                        MessageTemplateAction(
                            label='done',
                            text='done'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/oyNcabU.png',
                    title= '$' + sheet_cost.cell(3,8).value,
                    text='housing',
                    actions=[
                        MessageTemplateAction(
                            label='done',
                            text='done'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/e5oOgav.png',
                    title= '$' + sheet_cost.cell(4,8).value,
                    text='transportation',
                    actions=[
                        MessageTemplateAction(
                            label='done',
                            text='done'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/iW98jue.png',
                    title= '$' + sheet_cost.cell(5,8).value,
                    text='education',
                    actions=[
                        MessageTemplateAction(
                            label='done',
                            text='done'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/IcUTcAe.png',
                    title= '$' + sheet_cost.cell(6,8).value,
                    text='entertainment',
                    actions=[
                        MessageTemplateAction(
                            label='done',
                            text='done'
                        )
                    ]
                )
            ], image_aspect_ratio = 'rectangle', image_size = 'cover'
        )
    )
    return message

#TemplateSendMessage - ImageCarouselTemplate(圖片旋轉木馬)
def image_carousel_message1():
    message = TemplateSendMessage(
        alt_text='圖片旋轉木馬',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/uKYgfVs.jpg",
                    action=URITemplateAction(
                        label="新鮮水果",
                        uri="http://img.juimg.com/tuku/yulantu/110709/222-110F91G31375.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QOcAvjt.jpg",
                    action=URITemplateAction(
                        label="新鮮蔬菜",
                        uri="https://cdn.101mediaimage.com/img/file/1410464751urhp5.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Np7eFyj.jpg",
                    action=URITemplateAction(
                        label="可愛狗狗",
                        uri="http://imgm.cnmo-img.com.cn/appimg/screenpic/big/674/673928.JPG"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QRIa5Dz.jpg",
                    action=URITemplateAction(
                        label="可愛貓咪",
                        uri="https://m-miya.net/wp-content/uploads/2014/07/0-065-1.min_.jpg"
                    )
                )
            ]
        )
    )
    return message

#關於LINEBOT聊天內容範例
