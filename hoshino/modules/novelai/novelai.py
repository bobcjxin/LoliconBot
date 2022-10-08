from pathlib import Path
from hoshino import Service, priv, aiorequests, R
import requests
import base64
from PIL import Image
from io import BytesIO
import math

sv_help = "[ai绘图+关键词] 关键词仅支持英文，用逗号隔开\n" \
          "[以图绘图+图片]"

sv = Service(
    name="二次元ai绘图",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76"
}

imgpath = R.img('novelai').path
Path(imgpath).mkdir(parents=True, exist_ok=True)


@sv.on_fullmatch("ai绘图帮助", "AI绘图帮助")
async def send_help(bot, ev):
    await bot.send(ev, f'{sv_help}')


@sv.on_prefix(("ai绘图", "AI绘图"))
async def novelai_getImg(bot, ev):
    '''
    AI绘制二次元图片
    '''
    key_word = str(ev.message.extract_plain_text()).strip()
    await bot.send(ev, "正在绘图中，请稍后...")
    try:
        url = f"http://91.217.139.190:5010/got_image?tags={key_word}"
        img_resp = await aiorequests.get(url, headers=headers, timeout=30)
    except Exception as e:
        await bot.finish(ev, f"api请求超时，请稍后再试。{e}", at_sender=True)
    i = await img_resp.content
    seed = img_resp.headers['seed']
    img = 'base64://' + base64.b64encode(bytes(i)).decode()
    try:
        await bot.send(ev, f"根据关键词【{key_word}】绘制的图片如下：\n[CQ:image,file={img}]\nseed:{seed}", at_sender=True)
    except Exception as e:
        await bot.finish(ev, f"图片发送失败。{e}", at_sender=True)


@sv.on_prefix(("以图绘图", "AI以图绘图"))
async def novelai_drawImg(bot, ev):
    for m in ev.message:
        if m.type == 'image':
            file = m.data['url']
            break
    search_img = await aiorequests.get(file)
    i = await search_img.content
    im = Image.open(BytesIO(i))
    w, h = im.size
    if w > h:
        n = math.ceil(w // 756)
    else:
        n = math.ceil(h // 756)
    im.thumbnail((w // n, h // n))
    buffer = BytesIO()
    im.save(buffer, format='PNG')
    e = buffer.getvalue()
    data = base64.b64encode(bytes(e)).decode()
    i = requests.post("http://91.217.139.190:5010/got_image2image?tags=lolicon", data=data).content
    img = 'base64://' + base64.b64encode(bytes(i)).decode()
    await bot.send(ev, f"根据图片绘制的图片如下：\n[CQ:image,file={img}]\n", at_sender=True)