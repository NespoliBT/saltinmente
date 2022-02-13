import json
import logging
import random
from pyrogram import Client, filters
from services.messageService import getMessageInfo
from services.themeService import getRandomTheme

app = Client("my_account")
logging.basicConfig(filename="log.txt", level=logging.INFO)

queue = {}
playing = []
themeGroupMap = {}
currentScore = {}

themesFile = open('themes.json')
themesData = json.load(themesFile)
themes = tuple(themesData.keys())


def checkIfPlaying(a, b, query):
    return query.chat.id in playing


isPlaying = filters.create(checkIfPlaying)


@app.on_message(filters.command("saltinmente") & filters.group & ~isPlaying)
async def saltinmente(client, message):
    [userid, username, groupid] = getMessageInfo(message)
    logging.info(f"[{userid}] {username} Group: {groupid}: \n {message.text}")

    if not queue.get(groupid):
        queue[groupid] = [
            userid
        ]

    groupQueue = queue[groupid]
    groupQueue[:] = [x for x in groupQueue if x != userid]
    groupQueue.append(userid)

    if len(groupQueue) >= 2:
        themeGroupMap[groupid] = getRandomTheme(themes, themesData)

        await message.reply(f"""
💡 Partita iniziata 💡
Tema: {themeGroupMap[groupid][0]}
Prima lettera: {themeGroupMap[groupid][1]}
        """)

        queue.pop(groupid)
        playing.append(groupid)


@app.on_message(isPlaying)
async def play(client, message):
    [userid, username, groupid] = getMessageInfo(message)
    logging.info(f"[{userid}] {username} Group: {groupid}: \n {message.text}")

    [themeName, firstLetter, themeSolutions] = themeGroupMap[groupid]

    if(message.text in themeSolutions):

        # Aggiorna punteggio
        if not currentScore.get(groupid):
            currentScore[groupid] = {userid: [1, username]}
        elif(userid in currentScore[groupid].keys()):
            currentScore[groupid][userid][0] += 1
        else:
            currentScore[groupid][userid] = [1, username]

        await message.reply_text("Corretto! 🎉")

        if(currentScore[groupid][userid][0] == 5):
            scoreboard = ""
            sortedScore = dict(
                sorted(
                    currentScore[groupid].items(),
                    key=lambda item: item[1], reverse=True
                )
            )

            i = 0
            for user in sortedScore:
                i += 1
                username = sortedScore[user][1]
                score = sortedScore[user][0]

                if(i == 1):
                    scoreboard += f"🥇 {username} ({user}): {score}\n"
                elif(i == 2):
                    scoreboard += f"🥈 {username} ({user}): {score}\n"
                elif(i == 3):
                    scoreboard += f"🥉 {username} ({user}): {score}\n"
                else:
                    scoreboard += f"{user}: {score}\n"

            await message.reply(f"""
🏁 Partita finita 🏁
{scoreboard}
            """)
            playing.remove(groupid)
            currentScore.pop(groupid)
        else:
            # Nuovo tema
            themeGroupMap[groupid] = getRandomTheme(themes, themesData)

            await message.reply(f"""
    Tema: {themeGroupMap[groupid][0]}
    Prima lettera: {themeGroupMap[groupid][1]}
            """)


@app.on_message(filters.group)
async def searching(client, message):
    [userid, username, groupid] = getMessageInfo(message)
    logging.info(f"[{userid}] {username} Group: {groupid}: \n {message.text}")

    if(queue.get(groupid) and message != "/saltinmente"):
        groupQueue = queue[groupid]
        await message.reply_text("Hai interrotto la coda...\nvergognati...")
        queue.pop(groupid)


app.run()
