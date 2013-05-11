import pygame
import string
import menu
from random import randint
import sys
import data
import level
import leveldata
from const import *
from pygame.locals import *
#import leveldatatest
#leveldata = leveldatatest

class Worldloop(object):
    """Simple class for looping through worlds"""
    def __init__(self,game,start):
        self.game = game
        self.loop(start)

    def loop(self,start):
        if start == self.game.nworlds:
            # bonus level
            World(self.game,start)
        for worldnum in range(start,self.game.nworlds):
            World(self.game,worldnum)

        if start == self.game.nworlds:
            # we completed the bonus level
            menu.Menu(self.game)
        else:
            # if here we have completed the game!
            self.game.completed()
    
class World(object):
    def __init__(self,game,worldnum):
        self.game = game
        self.screen = game.screen
        self.board = game.board
        self.worldnum = worldnum

        # colors for the circles
        # triangle color
        self.tcol = (255,255,255)
        # outer and inner circle colors

        if worldnum == 2:
            self.outercol = (0,255,0)
            self.innercol = (0,112,0)
        elif worldnum == 3:
            self.outercol = (255,39,0)
            self.innercol = (255,191,0)            
        elif worldnum == 4:
            self.outercol = (105,72,120)
            self.innercol = (231,16,190)
        elif worldnum == 5:
            self.outercol = (30,40,40)
            self.innercol = (136,137,143)            
        else:
            # default and level 1 colors
            self.outercol = (255,0,0)
            self.innercol = (112,0,0)            
            
        # inner circle end colors
        self.endcol = (255,255,255)
        self.nflash = 20 

        # load music for this world
        if game.soundon:
            if worldnum in [3,4,5]:
                pygame.mixer.music.load(data.filepath('videogame7.ogg'))                
            else:
                pygame.mixer.music.load(data.filepath('space.ogg'))                

        self.levelnum = 0

        # load levels for this world
        # if we are in the bonus world, load from leveldatabonus
        if self.worldnum == self.game.nworlds:
            self.alllevels = self.getbonuslevels()
            self.numlevels = len(self.alllevels)

        else:
            self.alllevels = leveldata.LEVELS[str(worldnum)]
            self.numlevels = len(self.alllevels)
        
        # start timer for this world
        self.timeevent = pygame.USEREVENT
        pygame.time.set_timer(self.timeevent,1000)

        if self.worldnum == self.game.nworlds:
            self.timeleft = WORLDTIME['bonus']
        else:
            self.timeleft = WORLDTIME[str(self.worldnum)]
        
        # play the world!
        self.playworld()
        
    def getbonuslevels(self):
        """Return random selection of bonus levels"""
        import leveldatabonus
        # 3 easy levels, 4 mid levels, 3 hard levels
        nlevs = len(leveldatabonus.LEVELS['bonus'])
        e1,e2,e3 = (randint(0,99),randint(0,99),randint(0,99))
        m1,m2,m3,m4 = (randint(0,99),randint(100,199),
                       randint(100,199),randint(100,199))
        h1,h2,h3 = (randint(200,299),randint(200,299),randint(200,299))
        # screenshot is level 290
        levels = [leveldatabonus.LEVELS['bonus'][i] for i in
                  [e1,e2,e3,m1,m2,m3,m4,h1,h2,h3]]
        return levels

    def drawintro(self):
        if self.worldnum == self.game.nworlds:
            text = 'BONUS'
        else:
            text = 'GALAXY ' + str(self.worldnum)
        surf = self.game.worldnamefont.render(text,True,WHITE)
        self.screen.blit(self.game.bim,(0,0))        
        self.screen.blit(surf,(100,250))
        pygame.display.update()
        pygame.time.wait(2000)
        # start the music!
        pygame.mixer.music.play(-1)                   
                    

    def playworld(self):
        # draw world screen e.g. "Galaxy 1"
        self.drawintro()
        while self.levelnum != self.numlevels:
            self.nextlevel()

    def nextlevel(self):
        self.board.clear()
        title = ('level ' + str(self.levelnum + 1) + '/'
                 + str(self.numlevels))
        self.level = level.Level(self.game,self, title,
                                 self.alllevels[self.levelnum])
        # if here, we completed the level
        self.levelnum += 1
