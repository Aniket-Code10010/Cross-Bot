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
        [Button.inline("ADD NEW MSG PAIR", data="addmsg")],
        [Button.inline("RESTART BOT", data="restart")],
        [
            Button.inline("Start Promo", data="startpromo"),
            Button.inline("Stop Promo", data="stoppromo"),
        ]
    ]
    await event.reply("Choose Options", buttons=btn)

@bot.on(events.NewMessage(incoming=True, pattern="^/help"))
async def help(e):
    msg = """
• `/start` - __Most Features Are Here__

• `/addch <id>` - __This Will add Channel id__

• `/remch <id>` - __This Will Remove Channel id__

• `/remmsgpair` - __To Delete the ad__

• `/interval <in seconds>` - __To set Interval of ad__
"""
    await e.reply(msg)


@bot.on(events.NewMessage(incoming=True, pattern="^/addch"))
async def addchh(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        id = event.text.split()[1]
    except:
        return await event.reply("Input Not Found")
    chs = dB.get("CHATS") or []
    if int(id) not in chs:
        chs.append(int(id))
    dB.set("CHATS", chs)
    await event.reply("`Succesfully Added`")


@bot.on(events.NewMessage(incoming=True, pattern="^/remch"))
async def remmchh(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        id = event.text.split()[1]
    except:
        return await event.reply("Input Not Found")
    chs = dB.get("CHATS") or []
    if int(id) in chs:
        chs.remove(int(id))
    dB.set("CHATS", chs)
    await event.reply("`Succesfully Removed`")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("addmsg")))
async def add_msgs(event):
    ADS = dB.get("ADS") or []
    async with event.client.conversation(event.sender_id) as cv:
        await cv.send_message(
            """`Send First Message of the pair`\n__Note: Avoid to use " and ' in message.__"""
        )
        msg1 = await cv.get_response(timeout=90)
        if msg1.text.startswith("/cancel"):
            return await msg1.reply("`Process Cancelled Successfully`")
        await cv.send_message(
            """`Send Second Message of the pair`\n__Note: Avoid to use " and ' in message.__"""
        )
        msg2 = await cv.get_response(timeout=90)
        if msg2.text.startswith("/cancel"):
            return await msg2.reply("`Process Cancelled Successfully`")
        xx = [msg1.text, msg2.text]
        ADS.append(xx)
        dB.set("ADS", ADS)
        return await cv.send_message("`Succesfully Added`")


@bot.on(events.NewMessage(incoming=True, pattern="^/remmsgpair"))
async def rem_msg_pair(event):
    if str(event.sender_id) not in OWNER:
        return
    ADS = dB.get("ADS") or []
    i = 0
    text = ""
    for item in ADS:
        text += f"`{i}` - `{item}`\n"
        i += 1
    if not text:
        return await event.reply("`No Msg Found`")
    async with event.client.conversation(event.sender_id) as cv:
        await cv.send_message(text)
        await cv.send_message("`Send The Corresponding numbers of the ad`")
        no = await cv.get_response(timeout=90)
        x = await cv.send_message("`Processing...`")
        if no.text.startswith("/cancel"):
            return await x.reply("`Process Cancelled Successfully`")
        ADS.pop(int(no.text))
        dB.set("ADS", ADS)
        return await x.edit("`Done.`")


@bot.on(events.NewMessage(incoming=True, pattern="^/interval"))
async def intt(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        inn = event.text.split()[1]
    except:
        return await event.reply("`Invalid Input`")
    dB.set("INTERVAL", int(inn))
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
    dB.set("RESTART", [x.id, x.chat_id])
    os.execl(sys.executable, sys.executable, "-m", "bot")


async def onstart():
    try:
        xx = dB.get("RESTART")
        x = await bot.get_messages(xx[1], ids=xx[0])
        await x.edit("`Restarted`")
        dB.delete("RESTART")
    except BaseException:
        dB.delete("RESTART")


async def msg_poster():
    INTERVAL = dB.get("INTERVAL")
    CHATS = dB.get("CHATS")
    ADS = dB.get("ADS")
    chat1 = CHATS[0]
    CHATS.pop(0)
    sent_to = []
    while len(sent_to) != len(CHATS):
        n = 0
        for chat in CHATS:
            if len(ADS) < (n + 1):
                break
            msgpair1 = ADS[n]
            msgpair2 = None
            msgpair2 = ADS[n + 1]
            n += 1
            if chat not in sent_to:
                sent_to.append(chat)
            else:
                continue
            try:
                sent_1 = await bot.send_message(chat, msgpair1[0])
                sent_2 = await bot.send_message(chat, msgpair1[1])
                sent_3 = await bot.send_message(chat1, msgpair2[0])
                sent_4 = await bot.send_message(chat1, msgpair2[1])
                # could've used apscheduler here, but going for an easier approach.
                await asyncio.sleep(int(INTERVAL))
                await sent_1.delete()
                await sent_2.delete()
                await sent_3.delete()
                await sent_4.delete()
            except Exception as exc:
                log.error(exc)
                log.error("Failed to send/delete message in %s.", chat)
        if len(sent_to) == len(CHATS):
            sent_to = []


log.info("Started bot, looping cross promoter messages.")
bot.loop.run_until_complete(onstart())
bot.loop.run_until_complete(start_msg_poster())
bot.run_until_disconnected()
