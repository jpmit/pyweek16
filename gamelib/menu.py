import pygame
import level
from const import *
from pygame.locals import *
import world
import data

class Menu(object):
    """The menu is the first screen we get when we run the game"""
    def __init__(self,game):
        self.game = game
        self.screen = game.screen
        if game.soundon:
            pygame.mixer.music.load(data.filepath('menu.ogg'))
            pygame.mixer.music.play(-1)
            
        # text position for title, newgame, tutorial, worldselect
        self.tposx, self.tposy = (100,100)
        self.nposx, self.nposy = (120,220)
        self.tutposx, self.tutposy = (120,320)
        self.sposx, self.sposy = (120,420)
        
        # x and y offset to write world nums 1,2,..
        self.xoff = 30
        self.yoff = 50
        
        # don't list worlds on menu unless asked for
        self.listw = False
        self.drawmenu()
        self.loop()
        
    def drawmenu(self):
        self.screen.blit(self.game.bim,(0,0))

        # menu text: tsurf = title, nsurf = new game,
        # tutsurf = instruction, ssurf = select
        tsurf = self.game.menufont.render('Space Rotate',True,WHITE)
        nsurf = self.game.menufont2.render('New Game',True,WHITE)
        tutsurf = self.game.menufont2.render('Instructions',True,WHITE)        
        ssurf = self.game.menufont2.render('Select Galaxy',True,WHITE)

        # get text position on screen to check when clicked
        # title
        trect = tsurf.get_rect()
        self.trect = [trect.top+self.tposy,trect.left+self.tposx,
                      trect.bottom+self.tposy,trect.right+self.tposx]
        # new game
        nrect = nsurf.get_rect()
        self.nrect = [nrect.top+self.nposy,nrect.left+self.nposx,
                      nrect.bottom+self.nposy,nrect.right+self.nposx]
        # tutorial (instructions)
        tutrect = tutsurf.get_rect()
        self.tutrect = [tutrect.top+self.tutposy,tutrect.left+self.tutposx,
                      tutrect.bottom+self.tutposy,tutrect.right+self.tutposx]
        # select
        srect = tsurf.get_rect()        
        self.srect = [srect.top+self.sposy,srect.left+self.sposx,
                      srect.bottom+self.sposy,srect.right+self.sposx]
        # world
        self.wrects = []
        for w in range(1,self.game.nworlds+1):
            if w == self.game.nworlds:
                ws = 'extra'
                xset = w
            else:
                ws = str(w)
                xset = w
            surf = self.game.menufont2.render(ws,True,WHITE)            
            rect = surf.get_rect()
            rectpos = [self.sposy + self.yoff,rect.left+self.sposx + xset*self.xoff,
                       rect.bottom + self.sposy + self.yoff,
                       rect.right + self.sposx + xset*self.xoff]
            self.wrects.append(rectpos)

        # draw to the screen
        self.screen.blit(tsurf, (self.tposx,self.tposy))
        self.screen.blit(nsurf, (self.nposx,self.nposy))
        self.screen.blit(tutsurf, (self.tutposx,self.tutposy))        
        self.screen.blit(ssurf, (self.sposx,self.sposy))
        pygame.display.update()

    def inrect(self,mousex,mousey,rect):
        """Return True if mouse click is inside rectangle, else False"""
        if mousex > rect[1] and mousex < rect[3]:
            if mousey > rect[0] and mousey < rect[2]:
                return True
        return False

    def handlemouseup(self,(mousex,mousey)):
        """If we clicked on new game, start new game etc."""
        if self.inrect(mousex,mousey,self.nrect):
            # start game from level 1
            self.game.sfx['newgame'].play()
            # wait long enough to hear sound effect!
            pygame.time.wait(1000)
            self.startgame(1)
        if self.inrect(mousex,mousey,self.srect):
            # display galaxies (worlds) to select from
            if self.listw == False:
                self.game.sfx['newgame'].play()                
                self.listworlds()
        if self.inrect(mousex,mousey,self.tutrect):
            # display instructions
            self.game.sfx['newgame'].play()
            self.controls()
        if self.listw == True:
            # if we clicked on a galaxy (world) start game from there
            wc = self.wclicked((mousex,mousey))
            if wc:
                self.game.sfx['newgame'].play()
                pygame.time.wait(1000)                
                self.startgame(wc)

    def controls(self):
        self.screen.blit(self.game.bim,(0,0))
        text = ["Click in the centre of ",
                "a portal to rotate it",
                "",
                "a blue bar will",
                "cause the adjacent",
                "portal to rotate",
                "",
                "Complete the level by creating a path",
                "from top left portal to bottom right",
                "portal",
                "",
                "q to quit to main menu during level",
                "p to pause during level",
                "",
                "[Press any key]"]
        left,top = (50,50)
        dy = 30
        for (t,i) in zip(text,range(len(text))):
            surf = self.game.smallfont.render(t,True,WHITE)
            self.screen.blit(surf,(left,top+i*dy))
            
        # draw a portal
        tcol = (255,255,255)
        # outer and inner circle colors
        outercol = (255,0,0)
        innercol = (112,0,0)
        cell1 = level.Cell({'40': [[1, 0, 0, 0], [0, 1, 0, 1], []]},
                           outercol,innercol,tcol)
        cell2 = level.Cell({'41': [[1, 1, 0, 0], [0, 1, 0, 1], ['r']]},
                           outercol,innercol,tcol)
        cell3 = level.Cell({'51': [[1, 0, 0, 0], [0, 1, 0, 1], []]},
                           outercol,innercol,tcol)        
        self.game.board.drawcell(cell1)
        self.game.board.drawcell(cell2)
        self.game.board.drawcell(cell3)         

        pygame.display.update()
        self.controlloop()
        self.drawmenu()
        self.loop()

    def controlloop(self):
        while True:
            self.game.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game.terminate()                

                if event.type == KEYUP:
                    return

    def wclicked(self,(mousex,mousey)):
        """If we clicked on a world, return world number, else None"""
        for w in range(self.game.nworlds):
            if self.inrect(mousex,mousey,self.wrects[w]):
                return w+1
        
    def listworlds(self):
        for w in range(1,self.game.nworlds+1):
            if w == self.game.nworlds:
                # the last galaxy (world) is called bonus
                wname = 'bonus'
            else:
                wname = str(w)
            surf = self.game.menufont2.render(wname,True,WHITE)
            self.screen.blit(surf, (self.sposx + w*self.xoff,
                                    self.sposy + self.yoff))
            pygame.display.update()
        self.listw = True
                
    def loop(self):
        while True:
            self.game.clock.tick(FPS)

            for event in pygame.event.get():

                if event.type == QUIT:
                    self.game.terminate()

                if event.type == MOUSEBUTTONUP:
                    self.handlemouseup(event.pos)

    def startgame(self,worldnum):
        world.Worldloop(self.game,worldnum)
