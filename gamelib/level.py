import pygame
import menu
from const import *
from pygame.locals import *

class Level(object):
    def __init__(self,game,world,title,ldata):
        self.game = game
        self.screen = game.screen
        self.board = game.board        
        self.world = world
        self.title = title
        self.ispaused = False
        
        # each level has dictionary of cells
        # keys are location e.g. '11', '21'
        # where first number is xpos on board, second ypos
        # values are cell objects
        self.cells = self.createcells(ldata)

        self.cellclicked = None
        self.drawlevel()
        self.loop()

    def createcells(self,ldata):
        """Create list of cell objects in level"""
        clist =  [Cell({c:ldata[c]},self.world.outercol,
                       self.world.innercol, self.world.tcol)
                  for c in ldata.keys()]
        d = {}
        for c in clist:
            d[str(c.xpos)+str(c.ypos)] = c
        return d

    def createcellkeys(self):
        d = {}
        for cell in self.cells:
            d[str(cell.xpos)+str(cell.ypos)] = None
        return d
            
    def drawlevel(self):
        self.screen.blit(self.game.bim,(0,0))
        for cell in self.cells.values():
            self.board.drawcell(cell)
        self.board.drawnemesis()
        self.board.drawtimer(self.world.timeleft)
        self.board.drawtitle(self.title)
    
    def issolved(self):
        for cell in self.cells.values():
            if not cell.issolved():
                return False
        return True

    def handletime(self):
        self.world.timeleft -= 1
        self.board.drawtimer(self.world.timeleft)
        if self.world.timeleft == 0:
            self.outoftime()

    def outoftime(self):
        if self.game.soundon:
            self.game.sfx['laugh'].play()        
        text1 = "OUT OF TIME"
        surf1 = self.game.menufont2.render(text1,True,WHITE)
        self.screen.blit(self.game.bim,(0,0))
        self.screen.blit(self.game.largenemesis,(172,200))
        self.screen.blit(surf1,(170,100))

        pygame.display.update()
        pygame.time.wait(3000)
        menu.Menu(self.game)
            
    def handlemousedown(self,(mousex,mousey)):
        """Mouse click - highlight the cell clicked on if in inner circle"""
        cellx, celly = self.board.getcellnum(mousex, mousey)
        if cellx is not None and celly is not None:
            # inside boundary, did we click on a cell that is present?
            cellkey = str(cellx) + str(celly)
            if cellkey in self.cells:
                # we clicked on a cell, but maybe not in the inner circle
                if self.board.incircle(mousex,mousey,cellx,celly):
                    self.cellclicked =  str(cellx) + str(celly)
                    self.cells[cellkey].icol = self.world.outercol
                    self.board.drawcell(self.cells[cellkey])
                    pygame.display.update()
                    self.game.clock.tick(FPS)

    def handlemouseup(self):
        if self.cellclicked:
            self.cells[self.cellclicked].icol = self.world.innercol
            self.board.rotatecell(self.cells[self.cellclicked])
            self.board.rotateconnections(self.cells,self.cellclicked)
            self.cellclicked = None

    def levelend(self):
        """Play flashing sequence etc. at end of level"""
        if self.game.soundon:
            self.game.sfx['complete'].play()
            allcells = self.cells.values()
            ncells = len(allcells)
            for i in range(self.world.nflash):
                cell = allcells[i%ncells]
                cell.icol = self.world.endcol
                self.update()
                cell.icol = self.world.innercol
                self.update()

    def update(self):
        self.drawlevel()
        pygame.display.update()
        self.game.clock.tick(FPS)

    def pause(self):
        self.game.sfx['newgame'].play()
        self.ispaused = not (self.ispaused)

    def loop(self):
        while not self.issolved():

            if not (self.ispaused):
                self.update()
            
            for event in pygame.event.get():

                if event.type == KEYUP:
                    if event.key == K_p:
                        self.pause()
                    if event.key == K_q:
                        # back to main menu
                        menu.Menu(self.game)
                if event.type == QUIT:
                    self.game.terminate()

                if not (self.ispaused):

                    if event.type == self.world.timeevent:
                        self.handletime()

                    if event.type == MOUSEBUTTONDOWN:
                        self.handlemousedown(event.pos)

                    if event.type == MOUSEBUTTONUP:
                        self.handlemouseup()#event.pos)

        # we finished the level
        self.levelend()

        # execution returns to world (see world.py)
        return

class Cell(object):
    def __init__(self,celldata,ocol,icol,tcol):
        """celldata is dict with key e.g. '34'"""
        key = celldata.keys()[0]
        self.key = key
        self.xpos = int(key[0])
        self.ypos = int(key[1])
        # current and solved states
        self.current = celldata[key][0]
        self.solve = celldata[key][1]
        # connections to other cells
        self.conns = celldata[key][2]
        # inner and outer circle colors
        self.icol = icol
        self.ocol = ocol
        # triangle color
        self.tcol = tcol

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self.celldata())

    def celldata(self):
        """Recreate celldata dict"""        
        cdata = {'%s%s' %(self.xpos,self.ypos):
                 [self.current, self.solve, self.conns]}
        return cdata
    
    def issolved(self):
        return (self.current == self.solve)

    def rotate(self):
        """rotate cell by shifting current data
        [1,0,0,1]->[1,1,0,0]
        [0,1,1,0]->[0,1,1,0]"""
        n = len(self.current)
        new = [0]*n
        for i in range(n):
            if self.current[i] == 1:
                new[(i + 1)%n] = 1
        self.current = new
