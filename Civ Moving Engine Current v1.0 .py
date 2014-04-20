#more effective search function --> use mouse position as location heruistic
#"dot" "shifts" to the right for larger numbers --> (floating point errors?)
#determine indecies in initBoard! Do not wait to extrapolate in __init__ --> Done!
#Do gross math for efficient mouse click search....

from Tkinter import *
import random
import math
from fractions import Fraction

def specialInt(x): #rounds down for all cases, not just towards 0
	assert (type(x) == int or type(x) == float)
	if x >= 0:
		return int(x)
	else:
		return int(x-1)

def testSpecialInt(): #tests specialInt
	a = [1.1,1.9,0.2,0.9,-.2,-.9,-1.1,-1.9]
	c = []
	for b in a:
		c.append(specialInt(b))
	assert(c == [1,1,0,0,-1,-1,-2,-2])

class Animation(object): #From Kosbie email;expanded sligtly from stock code
	def mousePressed(self, event): pass
	def keyPressed(self, event): pass
	def timerFired(self): pass
	def init(self): pass
	def redrawAll(self): pass
	def mouseReleased(self,event): pass #added mouseReleased
	#removed many of the comments
	def run(self,rows=10,cols=20,width=500,height=500):#new args
		root = Tk()
		self.width,self.height = width,height
		self.rows,self.cols = rows,cols
		self.canvas = Canvas(root, width=width, height=height)
		self.canvas.configure(bd = 0, highlightthickness = 0) #added
		self.canvas.pack()
		def redrawAllWrapper():
			self.canvas.delete(ALL)
			self.redrawAll()
		def mousePressedWrapper(event):
			self.mousePressed(event)
			redrawAllWrapper()
		def mouseReleasedWrapper(event):
			self.mouseReleased(event)
			redrawAllWrapper()
		def keyPressedWrapper(event):
			self.keyPressed(event)
			redrawAllWrapper()
		root.bind("<Button-1>", mousePressedWrapper)
		root.bind("<Key>", keyPressedWrapper)
		root.bind("<B1-ButtonRelease>",mouseReleasedWrapper)
		self.timerFiredDelay = 20 # milliseconds
		def timerFiredWrapper():
			self.timerFired()
			redrawAllWrapper()
			self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
		self.init()
		timerFiredWrapper()
		root.mainloop()

class Tile(object): #tiles that make up the board
	tileSet = set() #list of all tiles to iterate through
	def __init__(self,colPos,rowPos,r,adj60,left,top,adj30): #initializes each tile
		cx = left + adj60 + colPos * adj60
		cy = top + r if rowPos%2 == 0 else top+2*r+adj30
		cy += rowPos/2*2*(r+adj30)
		self.cx,self.cy,self.r = cx,cy,r
		self.indexA,self.indexB = colPos,rowPos
		Tile.tileSet.add(self)

class MoveEngine(Animation): #basis of the "board" and how things will move
	def mousePressedOld(self,event):
		if not(self.selected): #select a "unit"
			for tile in Tile.tileList:
				if ((((event.x-tile.cx)**2+(event.y-tile.cy)**2)**.5 <= 
					self.adj60) and 							#.5 for sqrt
					(self.indexA == tile.indexA) and (self.indexB == 
						tile.indexB)):
					self.selected = True
		elif self.selected: #move a "unit"
			for tile in Tile.tileList:
				if (((event.x-tile.cx)**2+(event.y-tile.cy)**2)**.5 <= 
					self.adj60):
					self.indexA = tile.indexA
					self.indexB = tile.indexB
					self.selected = False
		#print self.selected

	def mousePressed(self,event):
		adj60,adj30,r = self.adj60,self.adj30,self.r
		mBlue = ((1.0*r-adj30)/adj60) #slope for blue lines
		mRed = ((1.0*adj30-r)/adj60) #slope for red lines
		#see concept "Board With Lines.png" if unclear
		mseX,mseY = event.x,event.y
		mseX -= self.adjX
		mseY -= self.adjY
		yIntBlue = mseY - self.top - (mseX-self.left)*mBlue
		yIntRed = mseY - self.top - (mseX-self.left)*mRed
		blueNum = (yIntBlue - adj30)/(2*adj30)
		redNum = (yIntRed - adj30)/(2*adj30)
		bFloor = int(math.floor(blueNum)) #changed from specialInt
		rFloor = int(math.floor(redNum))  #^this
		#print "b: " + str(blueNum) + "," + "r: " + str(redNum)
		if (bFloor+rFloor)%3 == 0:
			if blueNum % 1 > redNum % 1: pass
		#		print "left"
			else: pass
		#		print "right"
		indexA,indexB = -1,Fraction(1,3)
		indexA += rFloor
		indexB += Fraction(1,3)*rFloor
		indexA -= bFloor
		indexB += Fraction(1,3)*bFloor
		if (bFloor+rFloor)%3 == 0:
			if blueNum % 1 > redNum % 1: indexA -= 1
			else: indexA += 1
		indexA,indexB = int(math.floor(indexA)),int(math.floor(indexB))
		if not self.selected:
			if (self.indexA == indexA) and (self.indexB == indexB):
				self.selected = True
		else:
			self.indexA = indexA
			self.indexB = indexB
			self.selected = False

	def keyPressed(self,event): #mainly for testing; as moving uses the mouse in game
		if event.keysym == "z": self.indexA -= 2 #move the "dot" #left
		elif event.keysym == "s": self.indexB -= 1 #up
		elif event.keysym == "x": self.indexB += 1 #down
		elif event.keysym == "c": self.indexA += 2 #right
		elif event.keysym == "d": self.coords = not(self.coords) #superimpose
														   #numbers over tiles
		elif event.keysym == "Up": self.adjY -= 5
		elif event.keysym == "Down": self.adjY += 5
		elif event.keysym == "Right": self.adjX += 5
		elif event.keysym == "Left": self.adjX -= 5
		#print self.indexA,self.indexB

	def drawBoard(self): #for each tile object, draws a hexagon
		for tile in Tile.tileSet:
			cx,cy,r = tile.cx,tile.cy,tile.r
			adj60, adj30 = self.adj60,self.adj30
			cx += self.adjX
			cy += self.adjY
			if ((self.right+2*self.adj60>cx>self.left-2*adj60) and
				(self.bottom+2*r>cy>self.top-2*r)):
				self.canvas.create_polygon(cx,          cy-r,
										   cx+adj60,    cy-adj30,
										   #m = (int(adj60)/(r-adj30))
										   cx+adj60,    cy+adj30,
										   cx,          cy+r,
										   #m = (int(adj60)/(adj30-r))
										   cx-adj60,    cy+adj30,
										   cx-adj60,    cy-adj30,
										   fill = "white", outline = "black",
										   width = r/50)#line width heuristic
				if self.coords:self.canvas.create_text(cx,cy,text="%d,%d"%(
					tile.indexA,tile.indexB)) #superimpose numbers
		self.canvas.create_rectangle(self.left,self.top,self.right,self.bottom)
		#bounding rectangle to show what the board actually is

	def initBoard(self,left,top,right,bottom,r=-1): #creates tiles for board
		self.left,self.top,self.right,self.bottom = left,top,right,bottom
		self.width,self.height = width,height = abs(left-right),abs(top-bottom)
		if r < 0: r = min(width,height)/20 #radius heuristic
		adj60, adj30 = r*(3**.5)/2, r/2.0 #distances corresponding to the sides
			 #opposide the 30 and 60 degree angles of triangles in the hexagons
		self.adj60,self.adj30,self.top,self.left,self.r=adj60,adj30,top,left,r
		print r, adj60,adj30
		for colPos1 in xrange(0,self.cols,2):
			for rowPos1 in xrange(0,self.rows,2):
				Tile(colPos1,rowPos1,r,adj60,left,top,adj30)
		for colPos2 in xrange(1,self.cols,2): #easier to iterate every other row, separately
			for rowPos2 in xrange(1,self.rows,2):
				Tile(colPos2,rowPos2,r,adj60,left,top,adj30)

	def drawPosition(self,indexA,indexB): #draws dot: hypothetical unit
		if (indexA%2 != indexB%2): indexA += 1 #NOT self.indexA
		adj60, adj30 = self.adj60, self.adj30
		left,top,r = self.left,self.top,self.r
		cx = left + adj60 + indexA*adj60
		cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
		cy += indexB/2*float(2*(r+adj30))
		cx += self.adjX
		cy += self.adjY
		color = "black"
		if self.selected: color = "yellow"
		self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = color)
		#the dot, which represents a unit, has an arbitrary radius of 5

	def init(self): #initializes the animation
		self.initBoard(50,50,self.width-50,self.height-50)
		#"in-shifted" by 25 to show that program works even if the boundaries
		#are not the edges
		self.indexA = 0
		self.indexB = 0
		self.selected = False
		self.coords = False
		self.adjX = 0
		self.adjY = 0

	def redrawAll(self): #redraws all
		self.drawBoard()
		self.drawPosition(self.indexA,self.indexB)

MoveEngine().run(100,100)

def testAll():
	print
	testSpecialInt()
	print "All Passed!"

testAll()