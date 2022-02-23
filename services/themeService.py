import random


def getRandomTheme(themes, themesData):
    theme = random.choice(themes)

    themeName = themesData[theme][0]

    themeSolutions = themesData[theme]

    firstLetter = random.choice(themeSolutions[1:])[0]

    themeSolutions = filter(
        lambda x: x.startswith(firstLetter), themeSolutions)

    # Soluzioni
    themeSolutions = tuple(themeSolutions)

    return [themeName, firstLetter, themeSolutions]
