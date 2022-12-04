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

scoreboardData = json.load(open('scores.json'))
scoreboardDataDict = dict(scoreboardData)
print(scoreboardDataDict)

usersNeededToPlay = 2
winCondition = 5


def checkIfPlaying(a, b, query):
    return query.chat.id in playing


isPlaying = filters.create(checkIfPlaying)


@app.on_message(filters.command("score") & filters.group)
async def score(client, message):
    print("asdasd")
    [userid, username, groupid, firstName] = getMessageInfo(message)
    userNicename = username if username else firstName
    logging.info(
        f"[{userid}] {userNicename} Group: {groupid}: \n {message.text}")

    scoreboardStr = ""

    scoreboard = sorted(scoreboardDataDict.items(),
                        key=lambda k: k[1]["score"], reverse=True)

    for(user) in scoreboard:
        scoreboardStr += f"{user[1]['userNicename']}: {user[1]['score']} punti\n"

    await message.reply(scoreboardStr)


@app.on_message(filters.command("saltinmente") & filters.group & ~isPlaying)
async def saltinmente(client, message):
    [userid, username, groupid, firstName] = getMessageInfo(message)
    userNicename = username if username else firstName
    logging.info(
        f"[{userid}] {userNicename} Group: {groupid}: \n {message.text}")
    print("ciao")
    if not queue.get(groupid):
        queue[groupid] = [
            userid
        ]

    groupQueue = queue[groupid]
    groupQueue[:] = [x for x in groupQueue if x != userid]
    groupQueue.append(userid)

    if len(groupQueue) >= usersNeededToPlay:
        themeGroupMap[groupid] = getRandomTheme(themes, themesData)
        print(themeGroupMap[groupid])
        await message.reply(f"""
💡 Partita iniziata 💡
Tema: {themeGroupMap[groupid][0]}
Prima lettera: {themeGroupMap[groupid][1]}
        """)

        queue.pop(groupid)
        playing.append(groupid)


@app.on_message(isPlaying)
async def play(client, message):
    [userid, username, groupid, firstName] = getMessageInfo(message)
    userNicename = username if username else firstName
    logging.info(
        f"[{userid}] {userNicename} Group: {groupid}: \n {message.text}")

    [themeName, firstLetter, themeSolutions] = themeGroupMap[groupid]

    if(message.text.lower() in themeSolutions):

        # Aggiorna punteggio
        if not currentScore.get(groupid):
            currentScore[groupid] = {userid: [1, userNicename]}
        elif(userid in currentScore[groupid].keys()):
            currentScore[groupid][userid][0] += 1
        else:
            currentScore[groupid][userid] = [1, userNicename]

        await message.reply_text("Corretto! 🎉")

        if(currentScore[groupid][userid][0] == winCondition):
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
                userNicename = sortedScore[user][1]
                score = sortedScore[user][0]

                if(i == 1):
                    scoreboard += f"🥇 {userNicename}: {score}\n"
                elif(i == 2):
                    scoreboard += f"🥈 {userNicename}: {score}\n"
                elif(i == 3):
                    scoreboard += f"🥉 {userNicename}: {score}\n"
                else:
                    scoreboard += f"{userNicename}: {score}\n"


                newScore = ((scoreboardDataDict.get(str(user)) and scoreboardDataDict.get(
                    str(user)).get("score")) or 0) + score

                scoreboardDataDict.update(
                    {str(user): {"userNicename": userNicename, "score": newScore}})

                with open('scores.json', 'w') as scoreFile:
                    json.dump(scoreboardDataDict, scoreFile)

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
    [userid, username, groupid, firstName] = getMessageInfo(message)
    userNicename = username if username else firstName
    logging.info(
        f"[{userid}] {userNicename} Group: {groupid}: \n {message.text}")

    if(queue.get(groupid) and message != "/saltinmente"):
        groupQueue = queue[groupid]
        queue.pop(groupid)

app.run()
