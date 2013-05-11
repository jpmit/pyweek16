import pygame
import string
from const import *

class Board(object):
    def __init__(self,game):
        """Board is XCELLS*YCELLS (6x6), with a margin on all sides"""        
        self.game = game
        self.screen = game.screen 
        self.xmargin = (WINDOWWIDTH - XCELLS*CELLSIZE)/2
        self.ymargin = (WINDOWHEIGHT  - YCELLS*CELLSIZE)/2
        # radius squared of 'inner' circle
        self.crad2 = (CELLSIZE/2 - TSIZE)**2

    def clear(self):
        """Erase board by drawing (black) rectangle"""
        pygame.draw.rect(self.screen,BLACK,(0,0,WINDOWWIDTH,
                                            WINDOWHEIGHT))
        pygame.display.update()

    def getlefttop(self,xnum,ynum):
        """Return position of top left of cell"""
        left = self.xmargin + xnum*CELLSIZE
        top =  self.ymargin + ynum*CELLSIZE
        return (left,top)

    def getcellcenter(self,cellx,celly):
        """Center coords of cell"""
        xpos = self.xmargin + cellx*CELLSIZE + CELLSIZE/2
        ypos = self.ymargin + celly*CELLSIZE + CELLSIZE/2
        return (xpos,ypos)

    def getcellnum(self,xpos,ypos):
        """Return cell number"""
        if (xpos < self.xmargin) or (xpos > WINDOWWIDTH - self.xmargin):
            return (None,None)
        if (ypos < self.ymargin) or (ypos > WINDOWHEIGHT - self.ymargin):
            return (None,None)
        cellx = (xpos - self.xmargin)/CELLSIZE
        celly = (ypos - self.ymargin)/CELLSIZE

        return cellx,celly

    def incircle(self,xpos,ypos,cellx,celly):
        """Are we in inner circle of cell with index (cellx,celly)?"""
        xcell, ycell = self.getcellcenter(cellx,celly)
        if ((xpos - xcell)**2 + (ypos - ycell)**2) < self.crad2:
            return True
        return False

        return cellx, celly

    def gettpoints(self,left,top,tnum):
        """
        Return 3 points for drawing triangle
        tnum | direction
        0      top
        1      right
        2      down
        3      left
        """
        if tnum == 0:
            x1 = left + CELLSIZE/2
            y1 = top
            x2 = x1 + TSIZE
            y2 = y1 + TSIZE
            x3 = x2 - 2*TSIZE
            y3 = y2
        if tnum == 1:
            x1 = left + CELLSIZE
            y1 = top + CELLSIZE/2
            x2 = x1 - TSIZE
            y2 = y1 + TSIZE
            x3 = x2
            y3 = y2 - 2*TSIZE
        if tnum == 2:
            x1 = left + CELLSIZE/2
            y1 = top + CELLSIZE
            x2 = x1 - TSIZE
            y2 = y1 - TSIZE
            x3 = x2 + TSIZE*2
            y3 = y2
        if tnum == 3:
            x1 = left
            y1 = top + CELLSIZE/2
            x2 = x1 + TSIZE
            y2 = y1 + TSIZE
            x3 = x2
            y3 = y2 - TSIZE*2

        return ((x1,y1),(x2,y2),(x3,y3))

    def drawcell(self,cell):
        """Draw a cell onto the board"""
        
        # get top left and center co-ords of cell
        left, top = self.getlefttop(cell.xpos,cell.ypos)

        # draw connections to other cells (if these exist)
        # done first since this is 'bottom layer'
        for c in cell.conns:
            self.drawconn(left,top,c)
        
        # outer circle
        pygame.draw.circle(self.screen, cell.ocol,
                           (left + CELLSIZE/2,top + CELLSIZE/2),
                           CELLSIZE/2)
        # inner circle
        pygame.draw.circle(self.screen, cell.icol,
                           (left + CELLSIZE/2,top + CELLSIZE/2),
                            CELLSIZE/2 - TSIZE)
        
        # draw arrows
        for t in enumerate(cell.current):
            if t[1] == 1:
                points = self.gettpoints(left,top,t[0])
                pygame.draw.polygon(self.screen, cell.tcol, points)

    def drawconn(self,left,top,conn):
        """Draw connection between two cells"""
        # x and y are left and top of cell
        COFF = 0 # offset at edge of circle
        if conn == 'u':
            x = left
            y = top - COFF
            width = CELLSIZE
            height = CWIDTH
        elif conn == 'd':
            x = left
            y = top + CELLSIZE - CWIDTH
            width = CELLSIZE
            height = CWIDTH - COFF
        elif conn == 'l':
            x = left + COFF
            y = top
            width = CWIDTH
            height = CELLSIZE
        elif conn == 'r':
            x = left + CELLSIZE - CWIDTH
            y = top
            width = CWIDTH - COFF
            height = CELLSIZE
        pygame.draw.rect(self.screen,CONNCOLOUR,(x,y,width,height))
        pygame.draw.rect(self.screen,BLACK,(x,y,width,height),CBOX)
        return
    
    def drawtimer(self,timeleft):
        tstr = string.zfill(timeleft,2)
        tleft, ttop = self.getlefttop(0,0)
        self.screen.blit(self.game.timerfont.render(tstr,True,WHITE),
                         (tleft,ttop))

    def drawnemesis(self):
        tleft, ttop = self.getlefttop(1,0)
        tleft += CELLSIZE/2
        self.screen.blit(self.game.nemesis,(tleft,ttop))

    def drawtitle(self,title):
        tleft, ttop = self.getlefttop(3,0)
        self.screen.blit(self.game.levelnamefont.render(title,True,WHITE),
                         (tleft,ttop))

    def rotatecell(self,cell):
        """Rotate cell (clockwise)"""
        if self.game.soundon:
            self.game.sfx['click'].play()
        cell.rotate()
        self.drawcell(cell)
        pygame.display.update()
        self.game.clock.tick(FPS)        

    def rotateconnections(self,cells,cellkey):
        """Rotate any cells in dict cells connected to cell with key cellkey"""
        cell = cells[cellkey]
        for c in cell.conns:
            if c == 'u':
                key = str(cell.xpos) + str(cell.ypos - 1)
            elif c == 'd':
                key = str(cell.xpos) + str(cell.ypos + 1)
            elif c == 'l':
                key = str(cell.xpos-1) + str(cell.ypos)
            elif c == 'r':
                key = str(cell.xpos +1) + str(cell.ypos)            
            self.rotatecell(cells[key])
