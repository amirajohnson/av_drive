from cmu_cs3_graphics import *
from PIL import Image
from pprint import pprint
import random
'''
Citations:
1. Parked Truck Images - Drawing by Paige Johnson (sister)
2. Pedestrian - Amira Johnson
3. Bike - Amira Johnson
5. Traffic Light Images - Drawing by Paige Johnson (sister)
6. Logos, home images, instructions, etc -- by Amira Johnson
7. Backdrop - Amira
8. Parking Lot - https://ozinga.com/wp-content/uploads/2020/09/22_CommonConcreteProblems-1024x500.jpg

Typical 112 functions, taken from the 112 website:
1. getCellBounds
2. getCell
3. pointInGraph
'''
###### algorithms #########
###########################
#get the partners of each node.
def getPartners(board, row, col):
    partnersList = []
    directions = [(1,0), (0,1), (0, 0), (-1,0), (0, -1)]
    for (dRow, dCol) in directions:
            newRow = dRow + row
            newCol = dCol + col
            if newRow >= len(board) or newRow < 0:
                continue
            elif newCol >= len(board[0]) or newCol < 0:
                continue
            else:
                if board[newRow][newCol] == True:
                    partnersList.append((newRow,newCol))
    return partnersList #return the partners

#construct the graph given the board
def constructGraph(app, board, startRow, startCol):
    nodesDict = dict()
    for row in range(len(board)):
        for col in range(len(board[0])):
            if (row, col) in app.restrictions:
                continue
            elif board[row][col] == True: #if this part is an open node
                nodesDict[(row,col)] = getPartners(board, row, col)

    return nodesDict

#DO NOT TOUCH THIS FUNCTION AMIRA!!!!
#breadth first search function, adapted from https://www.educative.io/edpresso/how-to-implement-a-breadth-first-search-in-python
def bfsHelper(app, visited, queue, dead, connections, graph, node):
    if queue == [] or app.goal in graph[node]:
        connections[app.goal] = node
        return connections
    else:
        n = queue.pop(0)
        for neighbor in graph[n]:
            if neighbor not in visited and neighbor not in dead:
                if neighbor in app.restrictions:
                    continue
                else:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    connections[neighbor] = node
                    #when it reaches a dead end, clear out the rest of the dict
                    solution = bfsHelper(app, visited, queue, dead, connections, graph, neighbor)
                    if solution != None:
                        return connections
                    else:
                        dead.append(neighbor)

#find any duplicates to remove them
def checkDuplicateConnections(connections):
    seen = set()
    duplicates = []
    for child in connections:
        if connections[child] in seen:
            duplicates.append(connections[child])
        seen.add(connections[child])
    return duplicates

#reconstruct the solution based on duplicates
def reconstructSolution(parent, connections):
    #the parents are the things that are repeating
    newConnections = dict()
    duplicateConnections = dict()
    connectionsList = list(connections)
    newList = []
    seen = set() #keeps track of the parents we've encountered already
    for i in range(len(connectionsList)):
        child = connectionsList[i]
        parent = connections[child]
        if parent in seen:
            #next index needs to be the i where the parent occurs again
            for j in range(i, len(connectionsList)):
                c = connectionsList[j]
                p = connections[c]
                if p == parent:
                    newList = connectionsList[:i] + connectionsList[j-1:]
        seen.add(parent)
    for value in newList:
        newConnections[value] = connections[value]
    return newConnections

#account for when thingies have no path
def doBreadthFirstSearch(app, node):
    app.visited = [node]
    app.queue = [node]
    path = []
    dead = []   
    connections = {node: None}
    solutionDict = bfsHelper(app, app.visited, app.queue, dead, connections, app.graph, node)
    if solutionDict != None:
        duplicateParents = checkDuplicateConnections(solutionDict)
        if duplicateParents != []:
            for parent in duplicateParents:
                solutionDict = reconstructSolution(parent, connections)
        
        for i in range(len(solutionDict)-1, -1, -1):
            currentNode = list(solutionDict.keys())[i]
            parent = solutionDict[currentNode]
            if parent == None: #it hit the first node
                path = reversed(path)
                path = list(path)  
                return path
            path.append(parent)
    else:
        app.noPathAvailable = True

#check if the neighbor is legal
def isLegalNeighbor(app, row, col, path):
    if row < 0 or row >= len(app.board) or col < 0 or col >= len(app.board[0]):
        return False
    elif (row,col) in app.restrictions:
        return False
    elif (row, col) in path:
        return False
    return True

#algorithm for moving objects - made by me, dfs, NEED TO KEEP TRACK OF VISITED
def createPathHelper(app, node, goalNode, path, dead):
    directions = [(0,1), (1,0), (0,-1), (-1, 0)]
    if  node[0] == goalNode[0] and node[1] == goalNode[1]:
        return path
    else:
        row, col = node
        for (dRow, dCol) in directions:
            newRow = row+dRow
            newCol = col+dCol
            if isLegalNeighbor(app, newRow, newCol, path) and (newRow, newCol) not in dead:
                path.append((newRow, newCol))
                sol = createPathHelper(app, (newRow, newCol), goalNode, path, dead)
                if sol != None:
                    return path
                else:
                    path.remove((newRow, newCol))
                    dead.append((newRow, newCol)) #restrict these for future checks
        return None

 #create a path for the pedestrian       
def createPath(app, node, goalNode):
    path = [node]
    dead = []
    return createPathHelper(app, node, goalNode, path, dead)

#get the coordinates for each cell.
def getCellBounds(app, row, col):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + cellWidth * col
    y0 = app.margin + cellHeight * row
    return (x0, y0, cellWidth, cellHeight)

################
###classes######
################

#################
####Bike Class###
#################
class Bike(object):
    def __init__(self, app, board, row, col):
        self.row = row
        self.board = board
        self.col = col
        self.app = app
        self.image = ''
        self.goal = self.getGoal()
        self.path = createPath(app, (self.row, self.col), self.goal)


    def draw(self):
        left, top, width, height = getCellBounds(self.app, self.row, self.col)
        drawImage(self.app.bikeImage, left, top, width = 25, height = 15)

    def __hash__(self):
        return hash(self.row)

    def __str__(self):
        return f'Bike at ({self.row},{self.col})'

    def getGoal(self):
        while True:
            randomRow = random.randint(0, len(self.board)-1)
            randomCol = random.randint(0, len(self.board[0])-1)
            if (randomRow, randomCol) not in self.app.restrictions:
                return (randomRow, randomCol)
    
    def move(self):
        if self.path != None and self.path != []:
            nextRow, nextCol = self.path.pop(0)
            self.row = nextRow
            self.col = nextCol
        else:
            return

    def highlightGoal(self):
        left, top, width, height = getCellBounds(self.app, self.goal[0], self.goal[1])
        drawRect(left, top, width, height, fill = 'orange')


##################
####Wall Class####
##################
class Wall(object):
    def __init__(self, app, row, col):
        self.row = row
        self.col = col
        self.app = app
        self.color = rgb(0, 36, 27)

    def draw(self):
        left, top, width, height = getCellBounds(self.app, self.row, self.col)
        drawRect(left, top, width, height, fill = self.color)
        drawRect(left+width, top, width, height, fill = self.color)

#########################
#####Pedestrian Class#####
##########################
#class for the moving pedestrian object.
class Pedestrian(object):
    def __init__(self, app, board, row, col):
        self.row = row
        self.col = col
        self.node = (row, col)
        self.app = app
        self.board = board
        self.image = ''
        self.goal = self.getGoal()
        self.visited = []
        self.path = createPath(app,(self.row, self.col),self.goal)     

    def draw(self):
        left, top, width, height = getCellBounds(self.app, self.row, self.col)
        drawImage(self.app.person, left, top, width = width, height = height)

    def highlightGoal(self):
        left, top, width, height = getCellBounds(self.app, self.goal[0], self.goal[1])
        drawRect(left, top, width, height, fill = 'orange')

    def __hash__(self):
        return hash(self.node)

    def __str__(self):
        return f'Pedestrian at ({self.row},{self.col})'
    
    def getGoal(self):
        while True:
            randomRow = random.randint(0, len(self.board)-1)
            randomCol = random.randint(0, len(self.board[0])-1)
            if (randomRow, randomCol) not in self.app.restrictions:
                return (randomRow, randomCol)

    def move(self):
        if self.path != None and self.path != []:
            nextRow, nextCol = self.path.pop(0)
            self.row = nextRow
            self.col = nextCol
        else:
            return

###################################
#initializing app-wide variables
def onAppStart(app):
    app.rows, app.cols = 30, 30
    app.board = [[True]*app.cols for row in range(app.rows)]
    app.margin = .15*app.width
    app.goal = (len(app.board)-1, len(app.board[0])-1)
    app.carRow, app.carCol = 1,0
    app.screen = 'Intro'
    app.restrictions = [(len(app.board)-1, 0)]
    app.startNode = (1,0)
    app.graph = dict()
    app.visited, app.queue= [], []
    app.obstaclesDict = {
        'b' : 'bike',
        'n' : 'pedestrian',
        'm': 'car'
    }
    app.path = []
    app.trail = []
    app.stepsPerSecond = 6
    app.gridHighlighted = True
    app.goKeyPressed = False
    app.noPathAvailable = False
    app.parkedCars = set()
    app.pedestrians = set()
    app.walls = set()
    app.bikes = set()
    app.obstacleToPlace = None
    ###images loading###
    app.truckImage = Image.open('Images/truck.png')
    app.trafficLightImage = Image.open('Images/trafficlight.png')
    app.trafficLightImage = CMUImage(app.trafficLightImage)
    app.truckImage = CMUImage(app.truckImage)
    app.homescreen = Image.open('Images/homescreen.png')
    app.homescreen = CMUImage(app.homescreen)
    app.lotImage = Image.open('Images/concrete.jpeg')
    app.lotImage = CMUImage(app.lotImage)
    app.instructions = Image.open('Images/instructions.png')
    app.instructions = CMUImage(app.instructions)
    app.obstacles = Image.open('Images/obstacles.png')
    app.obstacles = CMUImage(app.obstacles)
    app.label = Image.open('Images/label.png')
    app.label = CMUImage(app.label)
    app.backdrop = Image.open('Images/background.png')
    app.backdrop = CMUImage(app.backdrop)
    app.win = Image.open('Images/winScreen.png')
    app.win = CMUImage(app.win)
    app.person = Image.open('Images/pedestrian.png')
    app.person = CMUImage(app.person)
    app.bikeImage = Image.open('Images/bike.png')
    app.bikeImage = CMUImage(app.bikeImage)

    generateParkedCars(app)
    generateParkingLot(app)
    setFalseValues(app)
    app.pause = False
    app.currentKeyPressed = None

####Intro Screen#######
####drawing functions###
def drawIntroScreen(app):
    # #title
    drawImage(app.homescreen, 10, 10, width = app.width, height = app.height)
    # #start
    drawRect(app.width//2-50, 350, 100, 50, fill = rgb(219, 186, 221), borderWidth = 4, border = rgb(80, 197, 183))
    drawLabel('Start', app.width//2, 375, size = 25, 
                 font = 'Oswald', fill = 'white', bold = True)
    # #instructions
    drawRect(app.width//2-50, 425, 100, 50, fill = rgb(219, 186, 221), borderWidth = 4, border = rgb(80, 197, 183))
    drawLabel('Instructions', app.width//2, 450, size = 15, 
                 font = 'Oswald', fill = 'white', bold = True) 
###########################################################################
####Instructions Screen #########
#################################
def drawInstructionsScreen(app):
    drawImage(app.instructions, 0, 0, width = app.width, height = app.height)
    #play button
    drawRect(app.width//2-50, 600, 75, 50, fill = rgb(219, 186, 221), border = 'white', borderWidth=2)
    drawLabel('PLAY', app.width//2-10, 625, size = 20, bold = True, fill = 'white', font = 'Oswald')

################################################################################
####Gameplay Screen##
####drawing functions####
#from https://www.cs.cmu.edu/~112/lecture3/notes/notes-animations-part2.html
def pointInGrid(app, x, y):
    # return True if (x, y) is inside the grid defined by app.
    return ((app.margin <= x <= app.width-app.margin) and
            (app.margin <= y <= app.height-app.margin))

#from https://www.cs.cmu.edu/~112/lecture3/notes/notes-animations-part2.html
def getCell(app, x, y):
    if (not pointInGrid(app, x, y)):
        return None
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)
    return (row, col)

#if there is no path available, show this to user.
def drawNoPathAvailable(app):
    drawLabel("I'm stuck! Press 'r' to restart!",
            app.width//2, app.height//2, fill = rgb(219, 86, 221), size = 30,
            bold = True, font = 'Oswald')

#draw the highlighted grid while the user places obstacles
def drawGridHighlight(app):
    if app.gridHighlighted == True:
        for row in range(app.rows):
            for col in range(app.cols):
                left, top, width, height = getCellBounds(app, row, col)
                drawRect(left, top, width, height, fill = rgb(83, 58, 113),
                        opacity = 50, border = 'black', borderWidth = 1)
#draw the parking lot
def drawLot(app):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    drawImage(app.lotImage, app.margin, app.margin, width = gridWidth, height = gridHeight)
    drawRect(app.margin-5, app.margin-5, gridWidth+10, gridHeight+15, fill = None, border = 'white', borderWidth = 8)
    
#draws parking lot lines
def drawPath(app):
    for row in range(0, app.rows, 2 ):
        for col in range(1, app.cols):
            left, top, width, height = getCellBounds(app, row, col)
            drawLine(left, top, left, top+height, fill = 'white', lineWidth = 5)

#draw the car onto the board at a given row and col
def drawCar(app, row, col):
    left, top, width, height = getCellBounds(app, row, col)
    drawRect(left, top, width/2, height/2, fill = 'goldenrod')

################################################################################
###Objects Bar########
def drawObjectsBar(app):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    drawImage(app.obstacles, app.width//2-1.05*app.margin, app.height-1*app.margin, width = gridWidth-2.5*app.margin, height = app.margin+10, borderWidth = 20, border = rgb(80, 197, 183))

################################################################################
####draw onto the board #################
########################################
#drawing the obstacles onto the board.
#draw bikes
def drawBikes(app):
    for bike in app.bikes:
        bike.draw()
        bike.highlightGoal()
#draw Pedestrians
def drawPedestrians(app):
    for pedestrian in app.pedestrians:
        pedestrian.draw()
        pedestrian.highlightGoal()

#draw the walls
def drawWalls(app):
    for wall in app.walls:
        wall.draw()

#draw the parked cars
def drawParkedCars(app):
    for (row, col) in app.parkedCars:
        left, top, width, height = getCellBounds(app, row, col)
        drawImage(app.truckImage, left, top-10, width = width, height = 2*height)
        #drawRect(left, top, width, height, fill = 'purple')
    
#draws the goal spot on the board.
def drawGoalSpot(app):
    left, top, width, height = getCellBounds(app, app.goal[0], app.goal[1])
    drawRect(left, top, width, height, fill = rgb(247, 236, 89))
        
#draw trail for the car
def drawTrail(app):
    for (row, col) in app.trail:
        left, top, width, height = getCellBounds(app,row,col)
        drawRect(left, top, width, height, fill = 'lightCoral')

#show the user how many of each thing they've placed / obstacles screen
def drawNumberOfObjects(app):
    drawLabel(f'Parked Cars: {len(app.parkedCars)}', app.width-.5*app.margin, app.margin+app.margin+50, fill ='black', bold = True, size = 15)
    drawLabel(f'Pedestrians: {len(app.pedestrians)}', app.width-.5*app.margin, app.margin+app.margin+65, fill = 'black', bold = True, size = 15)
    drawLabel(f'Bikes: {len(app.bikes)}', app.width-.5*app.margin, app.margin+app.margin+80, fill = 'black', bold = True, size = 15)

#draw the win and restart screen
def drawWin(app):
    if app.path == [] and app.goKeyPressed:
        drawImage(app.win, app.width//2-app.margin, app.height//2-app.margin, width = 300, height = 200)

#draw the entire gameplay screen
def drawGameplayScreen(app):
        drawImage(app.backdrop, 0, 0, width = app.width, height = app.height)
        drawImage(app.label, app.width//2-1.05*app.margin, 40, width = 290, height = 100)
        drawImage(app.trafficLightImage, app.width//2 + .5*app.margin, 20, width = 200, height = 120)
        drawImage(app.trafficLightImage, app.width//2 - 2*app.margin, 20, width = 200, height = 120)
        drawLot(app)
        drawGoalSpot(app)
        drawTrail(app)
        drawPath(app)
        drawObjectsBar(app)
        drawGridHighlight(app)
        drawWalls(app)
        drawParkedCars(app)
        drawCar(app, app.carRow, app.carCol)
        drawBikes(app)
        drawPedestrians(app)
        drawNumberOfObjects(app)
        drawWin(app)

################################################################################
####controller functions####
#############################
#if there is no path available, tell the user to press r to restart
def noPathAvailable(app):
    if app.path == None and (app.carRow, app.carCol) != app.goal:
        app.noPathAvailable = True

#check if app.path is legal
def isLegalPath(app):
    for cell in app.path:
        (row, col) = cell
        if cell in app.restrictions:
            return False
    return True
  
#move the car when the spacekey is pressed
def moveCar(app):
    if app.noPathAvailable == True or app.path == None:
        return 
    if isLegalPath(app):
        if (app.carRow,app.carCol) != app.goal and app.path != []:
            nextRow, nextCol = app.path.pop(0)
            app.trail.append((nextRow, nextCol))
            app.carRow = nextRow
            app.carCol = nextCol   

#move the pedestrians
def movePedestrian(app):
    for pedestrian in app.pedestrians:
        if pedestrian.path != []:
            pedestrian.move()

#move the bikes
def moveBike(app):
    for bike in app.bikes:
        if bike.path != []:
            bike.move()

#add obstacles to the board. #add how the user can choose what they want to add.
def changeBoard(app, row, col, item):
    if (row,col) != app.goal and (row,col) != (0,0):
        if item == 'pedestrian':
            app.pedestrians.add(Pedestrian(app, app.board, row, col))
        elif item == 'bike':
            app.bikes.add(Bike(app, app.board, row, col))
        elif item == 'car':
            pass
        app.restrictions.append((row, col))
        app.board[row][col] = False

#set everything that is invalid to False
def setFalseValues(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if (row, col) in app.restrictions:
                app.board[row][col] = False

#randomly place walls and parked cars.
def generateWalls(app):
    wallsToPlace = 65
    i=0
    while i < wallsToPlace:
        row = random.randrange(0, app.rows-1,2)
        col = random.randrange(0, app.cols-1,2)
        if ((row, col) != (1,0) and (row, col) != app.goal and (row, col) not in app.restrictions):
            app.walls.add(Wall(app, row, col))
            app.restrictions.append((row, col))
            app.restrictions.append((row, col+1))
            i+=1    

def generateParkedCars(app):
    carsToPlace = 65
    i = 0
    while i < carsToPlace:
        row = random.randrange(0, app.rows)
        col = random.randrange(0, app.cols-1, 2)
        if ((row, col) != (1,0) and (row, col) != app.goal and (row, col) not in app.parkedCars and (row, col) not in app.restrictions
             and (row, col) != (app.goal[0]-1, app.goal[1]) and (row, col) != (app.goal[0], app.goal[1]-1)):
            app.parkedCars.add((row, col))
            app.restrictions.append((row, col))
            i+=1

def generateParkingLot(app):
    generateParkedCars(app)
    generateWalls(app)

#checks what button was clicked on the homescreen
def checkButtonClicked(app, mouseX, mouseY):
    if app.screen == 'Intro':
        #startButton check
        if ((mouseX>=app.width-50 and mouseX<=app.width+50) or
            (mouseY>=350 and mouseY<=400)):
            app.screen = 'Gameplay'
            app.background = rgb(80, 197, 183)
        #instructionsButton
        elif ((mouseX>=app.width-50 and mouseX<=app.width+50) or 
            (mouseY>=425 and mouseY<=475)):
            app.screen = 'Instructions'
    elif app.screen == 'Instructions':
        #if the play button is clicked, open the game.
        if ((mouseX>=app.width-50 and mouseX<=app.width+25) or 
            (mouseY>=600 and mouseY<=650)):
            app.screen = 'Gameplay'
            app.background = rgb(80, 197, 183)

#when the mouse is clicked ...
def onMousePress(app, x, y):
    if app.screen == 'Intro' or app.screen == 'Instructions':
        checkButtonClicked(app, x, y)
    elif app.screen == 'Gameplay':
        if app.obstacleToPlace == None:
            return
        elif getCell(app, x, y) != None:
            row, col = getCell(app, x, y)
            changeBoard(app, row, col, app.obstacleToPlace)

#restart the game when the restart key is pressed
def restart(app):
    app.board = [[True]*app.cols for row in range(app.rows)]
    app.carRow, app.carCol = (1,0)
    app.restrictions = []
    app.graph = dict()
    app.startNode = (1, 0)
    app.goal = (len(app.board)-1, len(app.board[0])-1)
    app.visited, app.queue = [], []
    app.path = []
    app.trail = []
    app.goKeyPressed = False
    app.noPathAvailable = False
    app.parkedCars = set()
    app.walls = set()
    app.pedestrians = set()
    app.bikes = set()
    app.gridHighlighted = True
    generateParkingLot(app)
    setFalseValues(app)

#when ___ key is pressed, run this function.    
def onKeyPress(app, key):
    if app.screen == 'Gameplay':
        app.currentKeyPressed = key
        if key == 'space':
            app.goKeyPressed = True
            app.gridHighlighted = False
            app.graph = constructGraph(app, app.board, app.startNode[0], app.startNode[1])
            app.path = doBreadthFirstSearch(app, app.startNode)
            if app.path == []:
                restart(app) 
        elif key == 'r':
            app.noPathAvailable = False
            restart(app)
        elif key =='p':
            app.paused = not app.paused
        else:
            if key in app.obstaclesDict:
                app.obstacleToPlace = app.obstaclesDict[key]
#on step
def onStep(app):
    if app.screen == 'Gameplay':
        if app.noPathAvailable:
            restart(app)
        else:
            setFalseValues(app)
            noPathAvailable(app)
            if app.goKeyPressed == True:
                moveCar(app)
                movePedestrian(app)
                moveBike(app)

def redrawAll(app):
    if app.screen == 'Intro':
        drawIntroScreen(app)
    elif app.screen == 'Instructions':
        drawInstructionsScreen(app)
    else:
        drawGameplayScreen(app)
        if app.noPathAvailable:
            drawNoPathAvailable(app)
 
def main():
    runApp(width = 1000, height = 800)
main()