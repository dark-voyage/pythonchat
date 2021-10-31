import asyncio

from pywebio import start_server
import pywebio
from pywebio.input import *
from pywebio.output import *
from pywebio.platform import tornado
from pywebio.session import base, defer_call, info as session_info, run_async, run_js
import os.path

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 150

async def main():
    global chat_msgs
    
    put_markdown("## 👋 Onlayn chatga xush kelibsiz!\nBu chat 68dan kamroq qator koddan tashkil etilgan! xabarlar soni 150tadan oshsa o'chadi")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Chatga kirish", required=True, placeholder="Sizning ismingiz", validate=lambda n: "Bunday ism uje bor!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    chat_msgs.append(('📢', f'`{nickname}` chatga qoshildi!'))
    msg_box.append(put_markdown(f'📢 `{nickname}` chatga qoshildi'))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 Yangi xabar", [
            textarea(placeholder="Xabarning matni ...", name="msg"),
            actions(name="cmd", buttons=["Yuborish", {'label': "Chatni tark etish", 'type': 'cancel'}])
        ], validate = lambda m: ('msg', "Xabaringizni matnini kiriting!") if m["cmd"] == "Yuborish" and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("Siz chatni tark etingiz!")
    msg_box.append(put_markdown(f'📢 Foydalanuvchi `{nickname}` chatni tark etdi!'))
    chat_msgs.append(('📢', f'Foydalanuvchi `{nickname}` chatni etdi!'))

    put_buttons(['Qaytadan kirish'], onclick=lambda btn:run_js('window.location.reload()'))

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)
        
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname: # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
        
        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]
        
        last_idx = len(chat_msgs)
pywebio.platform.tornado_http.start_server(main, host='chatforus.herokuapp.com', debug=False, cdn=True, static_dir=None, allowed_origins=None, check_origin=None, auto_open_webbrowser=False, session_expire_seconds=None, session_cleanup_interval=None, max_payload_size='200M')
