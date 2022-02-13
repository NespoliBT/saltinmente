def getMessageInfo(message):
    return [
        message.from_user.id,
        message.from_user.username,
        message.chat.id
    ]
