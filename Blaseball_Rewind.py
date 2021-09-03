# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 16:36:37 2021

@author: 7max18
"""
import urllib.request, json
import pygame
import pygame.freetype
from blaseball_mike.chronicler import get_game_updates
from blaseball_mike.chronicler.v1 import time_season

url = 'https://raw.githubusercontent.com/xSke/blaseball-site-files/main/data/weather.json'

response = urllib.request.urlopen(url)

weatherData = json.loads(response.read())

firstBase = (185, 340)
secondBase = (130, 285)
thirdBase = (75, 340)

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
PURPLE = (102, 0, 204)
RED = (255, 0, 0)

eventIndex = 0
validSeason = False
validDay = False
validMatch = False

print("Select a Season from 1 to 24.")

while validSeason == False:
    mySeason = int(input())
    if 0 < mySeason and mySeason < 25:
        validSeason = True
    else:
        print("\nSeason invalid.")

days = time_season(mySeason)[0]['days']

print("Select a day from 1 to " + str(days) + ".")
while validDay == False:
    myDay = int(input())
    if 0 < myDay and myDay < days:
        validDay = True
    else:
        print("Date invalid.")
            
myGame = get_game_updates(season = mySeason, day = myDay)

matches = []

awayTeams = list(set(dic['data']['awayTeamName'] for dic in myGame))

i = 0
j = 0

while i < len(awayTeams):
    row = []
    row.append(awayTeams[i])
    row.append(next(dic['data']['homeTeamName'] for dic in myGame if dic['data']['awayTeamName'] == awayTeams[i]))
    matches.append(row)
    i += 1
    
print("Select a match.")

for match in matches:
    print(str(j + 1) + ". " + matches[j][0] + " vs " + matches[j][1])
    j += 1

while validMatch == False:
    myMatch = int(input())
    if 0 < myMatch and myMatch < j + 1:
        validMatch = True
    else:
        print("Invalid entry.")
        
for gameEvent in myGame[::-1]:
    if gameEvent['data']['homeTeamName'] != matches[myMatch - 1][1]:
        myGame.remove(gameEvent)
        
pygame.init()

GAME_FONT_A = pygame.freetype.SysFont('Courier New', 24)
GAME_FONT_B = pygame.freetype.SysFont('Courier New', 36)

ballsTextRect = GAME_FONT_A.get_rect('BALLS')
strikesTextRect = GAME_FONT_A.get_rect('STRIKES')
outsTextRect = GAME_FONT_A.get_rect('OUTS')
ballsTextRect.topleft = (25, 410)
strikesTextRect.topleft = (ballsTextRect.bottomleft[0],
                           ballsTextRect.bottomleft[1] + 10)
outsTextRect.topleft = (strikesTextRect.bottomleft[0], 
                        strikesTextRect.bottomleft[1] + 10)

awayTeamTextRect = GAME_FONT_B.get_rect(myGame[0]['data']['awayTeamNickname'])
awayTeamTextRect.topleft = (25, 60)
homeTeamTextRect = GAME_FONT_B.get_rect(myGame[0]['data']['homeTeamNickname'])
homeTeamTextRect.topleft = (awayTeamTextRect.bottomleft[0],
                            awayTeamTextRect.bottomleft[1] + 25)

feed = pygame.Surface((230, 245))

def diamond(center = (0, 0), diagonal = 0):
    return ((center[0], center[1] + diagonal/2), 
            (center[0] + diagonal/2, center[1]),
            (center[0], center[1] - diagonal/2),
            (center[0] - diagonal/2, center[1]))

#adapted from stackoverflow

def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = text.split(' ') # array of words.
    space = GAME_FONT_A.get_rect(' ').width # The width of a space.
    max_width, max_height = surface.get_size()
    font_height = GAME_FONT_A.get_sized_ascender()
    x, y = pos
    delta_x = x
    line = ''
    for word in words:
        word_rect = font.get_rect(word)
        word_width = word_rect.width
        if delta_x + word_width >= max_width:
            line_surface = font.render(line, color)
            surface.blit(line_surface[0], (x, y))
            delta_x = pos[0]  # Reset the x.
            y += font_height + 5 # Start on new row.
            line = ''
        delta_x += word_width + space    
        line += word + ' '
    line_surface = font.render(line, color)
    surface.blit(line_surface[0], (x, y))

def refresh():
    gameEvent = myGame[eventIndex]['data']
    
    i = 0
    j = 0
    k = 0

    #inning and game status
    
    inningText = ''
    
    screen.fill((0, 0, 0))
    
    if gameEvent['gameComplete']:
        inningText += 'FINAL '
        inningColor = RED
    elif gameEvent['shame']:
        inningText += 'SHAME '
        inningColor = PURPLE
    else:
        inningText += 'LIVE '
        inningColor = GREEN
        
    inningText += str(gameEvent['inning'] + 1) + ' '
    
    #weather
    
    weather = weatherData[gameEvent['weather']]
    weatherText = weather['name']
    weatherTextRect = GAME_FONT_A.get_rect(weatherText)
    weatherTextRect.topright = (475, 25)
    GAME_FONT_A.render_to(screen, weatherTextRect.topleft, weatherText, WHITE)
    
    #team names and scores
    
    GAME_FONT_B.render_to(screen, awayTeamTextRect.topleft, 
                          gameEvent['awayTeamNickname'], gameEvent['awayTeamColor'])
    GAME_FONT_B.render_to(screen, homeTeamTextRect.topleft, 
                          gameEvent['homeTeamNickname'], gameEvent['homeTeamColor'])
    
    awayScoreTextRect = GAME_FONT_B.get_rect(str(gameEvent['awayScore']))
    awayScoreTextRect.topright = (475, awayTeamTextRect.topright[1])
    homeScoreTextRect = GAME_FONT_B.get_rect(str(gameEvent['homeScore']))
    homeScoreTextRect.topright = (475, homeTeamTextRect.topright[1])
    
    GAME_FONT_B.render_to(screen, awayScoreTextRect.topleft, str(gameEvent['awayScore']), WHITE)
    GAME_FONT_B.render_to(screen, homeScoreTextRect.topleft, str(gameEvent['homeScore']), WHITE)
    
    #pitcher and batter
    
    pitcherTextRect = GAME_FONT_A.get_rect('PITCHER')
    pitcherTextRect.topleft = (25, 160)
    batterTextRect = GAME_FONT_A.get_rect('BATTER')
    batterTextRect.topleft = (pitcherTextRect.bottomleft[0], 
                              pitcherTextRect.bottomleft[1] + 25)
    GAME_FONT_A.render_to(screen, pitcherTextRect.topleft, 'PITCHER', WHITE)
    GAME_FONT_A.render_to(screen, batterTextRect.topleft, 'BATTER', WHITE)
    
    #bases
     
    if 0 in gameEvent['basesOccupied']:
        pygame.draw.polygon(screen, WHITE, diamond(firstBase, 100))
    else:
        pygame.draw.polygon(screen, WHITE, diamond(firstBase, 100), 5)
    if 1 in gameEvent['basesOccupied']:
        pygame.draw.polygon(screen, WHITE, diamond(secondBase, 100))
    else:
        pygame.draw.polygon(screen, WHITE, diamond(secondBase, 100), 5)
    if 2 in gameEvent['basesOccupied']:
        pygame.draw.polygon(screen, WHITE, diamond(thirdBase, 100))
    else:
        pygame.draw.polygon(screen, WHITE, diamond(thirdBase, 100), 5)
        
    #balls, strikes and outs
    
    GAME_FONT_A.render_to(screen, ballsTextRect.topleft, 'BALLS', WHITE)
    GAME_FONT_A.render_to(screen, strikesTextRect.topleft, 'STRIKES', WHITE)
    GAME_FONT_A.render_to(screen, outsTextRect.topleft, 'OUTS', WHITE)
    
    if gameEvent['topOfInning']:
        inningText += '▲' 
        pitcherNameText = gameEvent['homePitcherName']
        pitcherColor = gameEvent['homeTeamColor']
        batterNameText = gameEvent['awayBatterName']
        batterColor = gameEvent['awayTeamColor']
    
        while i < 3:
            pygame.draw.circle(screen, WHITE, (225 - 25 * i, ballsTextRect.center[1]), 10, 3)
            i += 1
        while j < gameEvent['awayStrikes'] - 1:
            pygame.draw.circle(screen, WHITE, (225 - 25 * j, strikesTextRect.center[1]), 10, 3)
            j += 1
        while k < 2:
            pygame.draw.circle(screen, WHITE, (225 - 25 * k, outsTextRect.center[1]), 10, 3)
            k += 1
    else:
        inningText += '▼'
        pitcherNameText = gameEvent['awayPitcherName']
        pitcherColor = gameEvent['awayTeamColor']
        batterNameText = gameEvent['homeBatterName']
        batterColor = gameEvent['homeTeamColor']
        
        while i < 3:
            pygame.draw.circle(screen, WHITE, (225 - 25 * i, ballsTextRect.center[1]), 10, 3)
            i += 1
        while j < gameEvent['homeStrikes'] - 1:
            pygame.draw.circle(screen, WHITE, (225 - 25 * j, strikesTextRect.center[1]), 10, 3)
            j += 1
        while k < 2:
            pygame.draw.circle(screen, WHITE, (225 - 25 * k, outsTextRect.center[1]), 10, 3)
            k += 1
    
    i = 0
    j = 0
    k = 0
        
    while i < gameEvent['atBatBalls']:
        pygame.draw.circle(screen, WHITE, (225 - 25 * i, ballsTextRect.center[1]), 10)
        i += 1
    while j < gameEvent['atBatStrikes'] - 1:
        pygame.draw.circle(screen, WHITE, (225 - 25 * j, strikesTextRect.center[1]), 10)
        j += 1
    while k < gameEvent['halfInningOuts']:
        pygame.draw.circle(screen, WHITE, (225 - 25 * k, outsTextRect.center[1]), 10)
        k += 1
    
    #inning and game status (cont.)
    
    inningTextRect = GAME_FONT_A.get_rect(inningText)
    inningTextRect.topleft = (25, 25)
    GAME_FONT_A.render_to(screen, inningTextRect.topleft, inningText, inningColor)
    
    #pitcher and batter (cont.)
    
    if pitcherNameText == '':
        pitcherNameText = '—'
    if batterNameText == '':
        batterNameText = '—'
        
    pitcherNameTextRect = GAME_FONT_A.get_rect(pitcherNameText)
    batterNameTextRect = GAME_FONT_A.get_rect(batterNameText)
    pitcherNameTextRect.topright = (475, pitcherTextRect.topright[1])
    batterNameTextRect.topright = (475, batterTextRect.topright[1])
    GAME_FONT_A.render_to(screen, pitcherNameTextRect.topleft, pitcherNameText, pitcherColor)
    GAME_FONT_A.render_to(screen, batterNameTextRect.topleft, batterNameText, batterColor)
    
    #feed
    
    feed.fill((0, 0, 0))
    blit_text(feed, gameEvent['lastUpdate'], (0, 0), GAME_FONT_A, WHITE)
    screen.blit(feed, (255, 250))
    
    pygame.display.flip()
    
screen = pygame.display.set_mode([500, 500])
pygame.display.set_caption('Blaseball Rewind')


running = True

refresh()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and eventIndex < len(myGame) - 1:
                eventIndex += 1
                refresh()
            elif event.key == pygame.K_LEFT and eventIndex > 2:
                eventIndex -= 1
                refresh()
pygame.quit()