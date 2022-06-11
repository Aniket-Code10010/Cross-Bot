from . import *


try:
    bot.start(bot_token=BOT_TOKEN)
except Exception as erc:
    log.info(str(erc))

FUTURE = []


@bot.on(events.NewMessage(incoming=True, pattern="^/start"))
async def strt(event):
    if str(event.sender_id) not in OWNER:
        return
    btn = [
        [Button.inline("RESTART BOT", data="restart")],
        [
            Button.inline("Start Promo", data="startpromo"),
            Button.inline("Stop Promo", data="stoppromo"),
        ],
    ]
    await event.reply("Choose Options", buttons=btn)


@bot.on(events.NewMessage(incoming=True, pattern="^/help"))
async def help(e):
    msg = """
• `/start` - __Most Features Are Here__

• `/addch <id>` - __This Will add Channel id__

• `/remch <id>` - __This Will Remove Channel id__

• `/interval <in seconds>` - __To set Interval of ad__
"""
    await e.reply(msg)


@bot.on(events.NewMessage(incoming=True, pattern="^/addch"))
async def addchh(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        id = int(event.text.split()[1])
    except:
        return await event.reply("Input Not Found")
    chs = dB.get("AD_DATA") or {}
    async with bot.conversation(event.sender_id, timeout=500) as cv:
        await cv.send_message(f"Send 1st Promotion Ad Of {id} to post on other Chats.")
        repl = (await cv.get_response()).text
        await cv.send_message(f"Send 2nd Promotion Ad Of {id} to post on other Chats.")
        repl2 = (await cv.get_response()).text
        chs[id] = [repl, repl2]
    dB.set("AD_DATA", chs)
    await event.reply("`Succesfully Added`")


@bot.on(events.NewMessage(incoming=True, pattern="^/remch"))
async def remmchh(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        id = int(event.text.split()[1])
    except:
        return await event.reply("Input Not Found")
    chs = dB.get("AD_DATA") or {}
    if id in chs:
        chs.pop(id)
    dB.set("AD_DATA", chs)
    await event.reply("`Succesfully Removed`")


@bot.on(events.NewMessage(incoming=True, pattern="^/interval"))
async def intt(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        inn = event.text.split()[1]
    except:
        return await event.reply("`Invalid Input`")
    dB.set("INTERVAL1", int(inn))
    await event.reply("`Done.`")


async def start_msg_poster():
    if not FUTURE:
        print("Successfully Started msg poster.")
        future = asyncio.ensure_future(msg_poster())
        FUTURE.append(future)


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("startpromo")))
async def _(e):
    if not FUTURE:
        await e.reply("Successfully Started msg poster.")
        future = asyncio.ensure_future(msg_poster())
        FUTURE.append(future)
    else:
        await e.reply("Msg post funcn already runningF")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("stoppromo")))
async def _(e):
    if FUTURE:
        x = await e.reply("Trying to stop msg post func.")
        FUTURE[0].cancel()
        FUTURE.clear()
        await x.edit("`Done.`")
    else:
        await e.reply("Post func is not running.")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("restart")))
async def restart(event):
    x = await event.reply("`Restarting...`")
    dB.set("RESTART1", [x.id, x.chat_id])
    os.execl(sys.executable, sys.executable, "-m", "bot")


async def onstart():
    try:
        xx = dB.get("RESTART1")
        x = await bot.get_messages(xx[1], ids=xx[0])
        await x.edit("`Restarted`")
        dB.delete("RESTART1")
    except BaseException:
        dB.delete("RESTART1")


async def msg_poster():
    INTERVAL = dB.get("INTERVAL1") or dB.get("INTERVAL") or 3600
    DATA = dB.get("AD_DATA")
    CROSS = []
    for chat1 in list(DATA):
        for chat2 in list(DATA):
            if chat1 != chat2:
                CROSS.append([chat1, chat2])
    if CROSS:
        for chat1, chat2 in list(CROSS):
            try:
                sent = []
                msg1 = DATA[chat2] if isinstance(DATA[chat2], list) else [DATA[chat2]]
                msg2 = DATA[chat1] if isinstance(DATA[chat1], list) else [DATA[chat1]]
                for m in msg1:
                    sent.append(await bot.send_message(chat1, m))
                for m in msg2:
                    sent.append(await bot.send_message(chat1, m))
                await asyncio.sleep(int(INTERVAL))
                for snt in sent:
                    try:
                        await snt.delete()
                    except:
                        pass
            except Exception as exc:
                log.error(exc)
                log.error("Failed to send message in {} {}".format(chat1, chat2))
                for snt in sent:
                    try:
                        await snt.delete()
                    except:
                        pass


log.info("Started bot, looping cross promoter messages.")
bot.loop.run_until_complete(onstart())
bot.loop.run_until_complete(start_msg_poster())
bot.run_until_disconnected()
