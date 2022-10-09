from email.quoprimime import unquote
from numpy import TooHardError
import requests
from hoshino import Service
from hoshino.typing import CQEvent
import base64
from loguru import logger
import re
import json
from hoshino import aiorequests, priv
import io
from io import BytesIO
from PIL import Image
import traceback
from .config import TOKEN, HOST


####替换成自己的API URL
word2img_url = "%s/got_image?tags=" % HOST
img2img_url = "%s/got_image2image" % HOST
token = "&token=%s" % TOKEN

sv_help='''
[ai绘图+关键词] 关键词仅支持英文，用逗号隔开
[以图绘图+关键字+图片] 注意图片尽量长宽都在765像素一下，不然会被狠狠地压缩
逗号分隔tag,%20为空格转义,加0代表增加权重,可以加很多个,有消息称加入英语句子识别(你们自己测)
可选参数
&shape=Portrait/Landscape/Square 默认Portrait竖图           
&scale=11                        默认11,只建议11-24,细节会提高,太高了会过曝
&seed=1111111                    随机生成不建议用,如果想在返回的原图上修改,在响应头里找到seed，请注意seed一脉单传,seed不会变,也不能倒退
'''.strip()

sv = Service(
    name="二次元ai绘图",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)

@sv.on_fullmatch('ai绘图帮助')
async def gen_pic_help(bot, ev: CQEvent):
    await bot.send(ev, sv_help)


@sv.on_prefix(('ai绘图'))
async def gen_pic(bot, ev: CQEvent):
    try:
        await bot.send(ev, f"正在生成，请稍后...", at_sender=True)
        text = ev.message.extract_plain_text()
        get_url = word2img_url + text + token
        print(get_url)
        # image = await aiorequests.get(get_url)
        res = await aiorequests.get(get_url)
        image = await res.content
        load_data = json.loads(re.findall('{"steps".+?}', str(image))[0])
        image_b64 = 'base64://' + str(base64.b64encode(image).decode())
        mes = f"[CQ:image,file={image_b64}]\n"
        mes += f'seed:{load_data["seed"]}   '
        mes += f'scale:{load_data["scale"]}\n'
        mes += f'tags:{text}'
        await bot.send(ev, mes, at_sender=True)
    except:
        traceback.print_exc()
        await bot.send(ev, "生成失败…")


thumbSize=(768,768)
@sv.on_prefix(('以图生图'))
async def gen_pic_from_pic(bot, ev: CQEvent):
    try:
        await bot.send(ev, f"正在生成，请稍后...", at_sender=True)
        tag = ev.message.extract_plain_text()
        if tag == "":
            url = ev.message[0]["data"]["url"]
        else:
            url = ev.message[1]["data"]["url"]
        post_url = img2img_url + (f"?tags={tag}" if tag != "" else "") + token
        image = Image.open(io.BytesIO(requests.get(url, timeout=20).content))
        image = image.convert('RGB')
        if (image.size[0] > image.size[1]):
            image_shape = "Landscape"
        elif (image.size[0] == image.size[1]):
            image_shape = "Square"
        else:
            image_shape = "Portrait"
        image.thumbnail(thumbSize, resample=Image.ANTIALIAS)
        imageData = io.BytesIO()
        image.save(imageData, format='JPEG')
        temp = post_url+ "&shape=" + image_shape
        res = await aiorequests.post(post_url+ "&shape=" + image_shape, data=base64.b64encode(imageData.getvalue()))
        img = await res.content
        image_b64 = f"base64://{str(base64.b64encode(img).decode())}"
        mes = f"[CQ:image,file={image_b64}]\n"
        mes += f'tags:{tag}'
        await bot.send(ev, mes, at_sender=True)
    except:
        traceback.print_exc()
        await bot.send(ev, "生成失败…")