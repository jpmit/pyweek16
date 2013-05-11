import pygame
import sys
import world
import board
import data
import menu
from const import *

class Window(object):
    """Main game window"""
    def __init__(self):
        pygame.display.set_caption('Space Rotate!')
        self.screen = pygame.display.set_mode((WINDOWWIDTH,
                                               WINDOWHEIGHT))
        self.newgame()

    def newgame(self):
        Game(self)

class Game(object):
    """Game class for launching game"""
    def __init__(self,window):
        self.screen = window.screen

        # any constants
        self.nworlds = 6 # 5 + bonus

        # for controlling FPS
        self.clock = pygame.time.Clock()
                
        # load game-wide fonts, sound effects, images
        self.loadsounds()
        self.loadfonts()
        self.bim = pygame.image.load(data.filepath('back.png')).convert()
        self.nemesis = pygame.image.load(data.filepath('nemsmall.png')).convert_alpha()
        self.largenemesis = pygame.image.load(data.filepath('nemlarge.png')).convert_alpha()

        # create board
        self.board = board.Board(self)
        
        # display menu screen        
        menu.Menu(self)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def loadsounds(self):
        try:
            pygame.mixer.init()
            self.sfx = {'newgame': pygame.mixer.Sound(data.filepath('newgame.ogg')),
                        'click': pygame.mixer.Sound(data.filepath('click.ogg')),
                        'complete': pygame.mixer.Sound(data.filepath('complete.ogg')),
                        'laugh': pygame.mixer.Sound(data.filepath('eviljest.ogg'))}
            self.soundon = True
        except:
            print 'Cannot load sound'
            self.soundon = False

    def loadfonts(self):
        pygame.font.init()
        self.timerfont = pygame.font.Font(data.filepath('comicate.ttf'),40)
        self.smallfont = pygame.font.Font(data.filepath('vera.ttf'),20)
        self.levelnamefont = self.timerfont
        self.worldnamefont = pygame.font.Font(data.filepath('comicate.ttf'),80)
        self.menufont = pygame.font.Font(data.filepath('comicate.ttf'),50)
        self.menufont2 = pygame.font.Font(data.filepath('comicate.ttf'),40)

    def completed(self):
        """Completed game, display message and return to main menu"""
        text1 = "GAME COMPLETE!"
        text2 = "CONGRATULATIONS"
        surf1 = self.menufont2.render(text1,True,WHITE)
        surf2 = self.menufont2.render(text2,True,WHITE)
        self.screen.blit(self.bim,(0,0))        
        self.screen.blit(surf1,(100,250))
        self.screen.blit(surf2,(130,350))        
        pygame.display.update()
        pygame.time.wait(5000)
        menu.Menu(self)
