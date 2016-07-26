# TERM PROJECT: Laser Cutter
# Software accompanying laser cutter
# Larisa Thorne (lthorne), Section A
# 2015-12-09


""" VERSION 15: 
        (1) Fixed Arduino path problems
        (2) Change time display (est)
        (3) Allow to select if want to use saved path
        (4) Catches images with non- black/white pixels
"""

import sys
import os
import PIL.Image
import PIL.ImageDraw
from PIL import ImageTk
from tkinter import filedialog
from tkinter import *
import tkinter.messagebox
import serial, time
import random

# Class for properties of each pixel in GIF loaded:
class PixelCell(object):

    def __init__(self, row, col, color, size, ordinal):
        self.row = row
        self.col = col
        self.color = color
        self.size = int(size)
        self.ordinal = ordinal


    def __repr__(self):
        return "PixelCell((%d,%d),color=%s) \n" % (self.row,self.col,self.color)


    def draw(self, canvas, x0, y0):
        canvas.create_rectangle((x0,y0),(x0 + self.size, y0 + self.size), 
                                    fill = str(self.color), width = 1)
        if self.color == "black":
            textColor = "white"
        else:
            textColor = "black"
        textContent = str("  " + str(self.ordinal) + "\n(" + str(self.col) 
                + "," + str(self.row) + ")")
        if (self.size > 20): # Only draw info if enough space
            canvas.create_text((x0 + 11, y0 + 11), text = textContent, 
                                    fill = textColor, font = ("Arial", 10))


# Class for relaying position movements to Arduino (via serial)
class SerialComm(object):

    def __init__(self, data):
        self.xCoords = []
        self.yCoords = []   
        self.xCoordsStripped = []
        self.yCoordsStripped = [] 
        self.all = []    
        self.multiplier = 15 # Don't go over 20: weird behavior
        self.laserState = 1 # Start with laser on 
        self.newIndex = 0 
        data.countdown = int(data.stepperStartDelay 
                    + data.stepperWaitPerCoord*(len(data.pixelPath)-1)) 

        # Enter input:
        self.coords = data.pixelPath
        SerialComm.stripCoords(self)
        SerialComm.getRelPixelPath(self)

        # Create new serial object at specified port with baud rate 9600:
        self.ser = serial.Serial(
                # Always check ports: Arduino > Tools > Port
                # port = "/dev/cu.usbmodem411", # At home
                port = "/dev/cu.usbmodem641", # At CMU
                baudrate = 9600) 

        # Check correct serial port:
        print("Serial port: ", self.ser.name)

        # Give Arduino time to ready for commands: NECESSARY
        time.sleep(2)


    def stripCoords(self):
        for x in self.coords:
            self.xCoordsStripped.append(x[0])
            self.yCoordsStripped.append(x[1])


    def getRelPixelPath(self):
        self.xCoords.append(str(self.xCoordsStripped[0]))
        self.yCoords.append(str(self.yCoordsStripped[0]))

        for i in range(1, len(self.xCoordsStripped)):
            relX = - self.xCoordsStripped[i - 1] + self.xCoordsStripped[i]
            relY = - self.yCoordsStripped[i - 1] + self.yCoordsStripped[i]
            if ((abs(relX) <= 1) and (abs(relY) <= 1)):
                self.laserState = 1 # Laser is on
            else:
                self.laserState = 0 # Laser is off
            self.all.append(str(self.laserState))
            self.all.append(str(relX * self.multiplier))
            self.all.append(str(relY * self.multiplier))
        self.all.append(str(0)) # Turn laser off at end.


    def updatePixelColor(self, data, index):
        if (index % 3 == 2): # After each y coordinate entered, bc start @ 0
            location = data.pixelPath[self.newIndex]
            for pixel in data.pixels:
                if ((pixel.row == location[0]) and (pixel.col == location[1])):
                    pixel.color = "red"
            self.newIndex += 1
        elif (index == (len(self.all) - 1)): # Last pixel coloring
            location = data.pixelPath[-1]
            for pixel in data.pixels:
                if ((pixel.row == location[0]) and (pixel.col == location[1])):
                    pixel.color = "red"


    def move(self, data, index):
        printStuff = self.ser.write(self.all[index].encode()) 
        # tag = index % 3
        # if tag == 0: print("laser")
        # if tag == 1: print("x")
        # if tag == 2: print("y")
        
        SerialComm.updatePixelColor(self, data, index) # fix index
        time.sleep(1.5) # Also NECESSARY


########################################################
# MODE DISPATCHER:

def init(data, canvas):
    data.mainColor = "skyblue"#"navy" #"blue4" #"skyblue"
    data.minorColor = "steel blue"

    if (data.mode == "welcomeScreen"):
        welcomeScreenInit(data, canvas)
    elif (data.mode == "mainProgram"):
        mainProgramInit(data, canvas)


def mousePressed(event, data):
    if (data.mode == "welcomeScreen"):
        welcomeScreenMousePressed(event, data)
    elif (data.mode == "mainProgram"):
        mainProgramMousePressed(event, data)


def keyPressed(event, data):
    if (data.mode == "welcomeScreen"):
        welcomeScreenKeyPressed(event, data)
    elif (data.mode == "mainProgram"):
        mainProgramKeyPressed(event, data)


def timerFired(data):
    if (data.mode == "welcomeScreen"):
        welcomeScreenTimerFired(data)
    elif (data.mode == "mainProgram"):
        mainProgramTimerFired(data)


def redrawAll(canvas, data):
    if (data.mode == "welcomeScreen"):
        welcomeScreenRedrawAll(canvas, data)
    elif (data.mode == "mainProgram"):
        mainProgramRedrawAll(canvas, data)


########################################################
# welcomeScreen mode:
########################################################


def welcomeScreenInit(data, canvas):
    data.button1.pack_forget()
    data.button2.pack_forget()
    data.button4.pack_forget()
    data.button5.pack_forget() 
    data.button6.pack_forget()    
    data.button3.pack()
    data.welcomeImages = []
    data.welcomeImages.append(ImageTk.PhotoImage(file = "WelcomeImage1.gif"))
    data.welcomeImages.append(ImageTk.PhotoImage(file = "WelcomeImage2.gif"))
    data.welcomeImages.append(ImageTk.PhotoImage(file = "WelcomeImage3.gif"))
    data.welcomeImages.append(ImageTk.PhotoImage(file = "WelcomeImage4.gif"))
    data.welcomeImages.append(ImageTk.PhotoImage(file = "WelcomeImage5.gif"))
    data.welcomeImages.append(ImageTk.PhotoImage(file = "WelcomeImage6.gif"))

    
def welcomeScreenMousePressed(event, data):
    pass


def welcomeScreenKeyPressed(event, data):
    pass


def welcomeScreenTimerFired(data):
    randomIndex = random.randint(0,5)
    data.welcomePhoto = data.welcomeImages[randomIndex] # Pick random image


def welcomeScreenRedrawAll(canvas, data):
    canvas.create_rectangle((135, 15), 
                (460, data.height - 15), fill = data.mainColor,
                width = 0)
    canvas.create_image(data.width//2,data.height //2, 
                image = data.welcomePhoto)
    canvas.create_text((data.width//2,data.height //4 - 5), 
                text = "Welcome",
                font = ("Purisa", "17", "bold"))
    canvas.create_text((data.width//2,data.height //4 + 8), 
                text = "to",
                font = ("Purisa", "13", "bold"))
    canvas.create_text((data.width//2,data.height //4 + 30), 
                text = "LASER CUTTER!",
                font = ("Purisa", "23", "bold"))
    canvas.create_text((data.width//2,data.height //3 + 60), 
                text = "a CMU 15-112 term project",
                font = ("Purisa", "14", "bold"))
    canvas.create_text((data.width//2,data.height //3 + 80), 
                text = "by",
                font = ("Purisa", "11", "bold"))
    canvas.create_text((data.width//2,data.height //3 + 110), 
                text = "Larisa Thorne",
                font = ("Purisa", "16", "bold"))


########################################################
# mainProgram mode:
########################################################

def mainProgramInit(data, canvas):
    data.margin = 15
    data.marginY = data.margin + 15
    data.offsetImage = 25 # On left
    data.scale = 23
    data.between = 50
    data.imageDisplayWidth = 10 * data.scale # Pixel width times scale factor
    data.imageDisplayHeight = 12 * data.scale # Pixel height times scale factor
    data.blackPixelLoc = []
    data.readyToLoadImage = False
    data.pixels = []
    data.dirs = [ (-1, 0), (-1, 1), (0, 1), (1, 1), 
                          (1, 0), (1, -1), (0, -1), (-1, -1) ]
    data.pixelPath = []
    data.isCalculating = False
    data.isCalcCount = 5
    data.hasClickedCut = False
    data.readyToDrawRight = False
    data.isCutDone = False
    data.countdown = None
    data.flashOn = True
    data.flashCount = 0
    data.stop = False
    
    try:
        loadImages(data)
        getFileName(data)
        getFolder(data)
        loadPixelValues(data) 
        createPixelColorList(data)
        resizeImages(data)
        data.pixelSize = data.imageDisplayWidth // data.imDim[0]

        for j in range(len(data.pixelColorList[0])):
            for i in range(len(data.pixelColorList)):
                if (data.pixelColorList[i][j][0] == 0): 
                    color = "black"
                else:
                    color = "white"
                data.pixels.append(PixelCell(i, j, color, data.pixelSize, None))

        # Check if already have pixel path saved:
        prefix = data.filename.split(".")
        checkForFileName = prefix[0] + "PixelPath.txt"

        if checkForFileName in os.listdir(data.folderPath):
            result = tkinter.messagebox.askyesno("File found", 
                    str("Found saved '" + str(data.filename) + "' pixel path.\n\n" 
                    + "Use saved path?"))
            if result:
                dataFromFile = open(checkForFileName, mode = "rt")
                pixelPathStr = dataFromFile.read() # Reads in as string
                data.pixelPath = readFileReformat(pixelPathStr)
            else:
                data.isCalculating = True
                print(data.isCalculating)
                createPixelPath(data)

        else:
            data.isCalculating = True
            createPixelPath(data)

        assignPixelOrdinals(data)
        data.readyToDrawRight = True

    except:

        data.filename = "NONE"
        data.imDim = [0,0]

        data.button3.pack_forget()
        data.button1.pack(side = LEFT)
        data.button2.pack(side = LEFT)
        data.button6.pack(side = LEFT)
        data.button6.config(state = DISABLED)
        data.button5.pack(side = LEFT)
        data.button5.config(state = DISABLED)
        data.button4.pack(side = LEFT)

    data.stepperStartDelay = 2 # From serial communication
    data.stepperWaitPerCoord = 1.5 # From serial communication
               

def loadImages(data):
    # data.filename can be hardcoded here
    data.imageToDisplay = PIL.Image.open(data.filename)
    data.imDim = data.imageToDisplay.size # Old image dimensions


def loadPixelValues(data):
    # Looking at pixel colors
    data.pixelColorList = [[None]*data.imDim[1] for i in range(data.imDim[0])]
    data.visited = [[False]*data.imDim[1] for i in range(data.imDim[0])]
    RGBIm = data.imageToDisplay.convert('RGB') 

    for i in range(data.imDim[0]):
        for j in range(data.imDim[1]):
            r, g, b = RGBIm.getpixel((i,j))
            data.pixelColorList[i][j] = (r,g,b)
            if ((r,g,b) == (0,0,0)):
                data.blackPixelLoc.append((i,j))
            # Check for other colors:
            elif ((r,g,b) != (255,255,255)): 
                tkinter.messagebox.showinfo("Warning", str("Please select a " 
                        + "black and white image, only."))
                mainProgramInit(data, canvas)

    data.readyToLoadImage = True


def resizeImages(data):
    xResize = data.imageDisplayWidth / float(data.imageToDisplay.size[0])    
    data.imageDisplayHeight = int(data.imageToDisplay.size[1] * xResize)
    data.imageToDisplay = data.imageToDisplay.resize( (data.imageDisplayWidth,
            data.imageDisplayHeight))
    data.newImDim = data.imageToDisplay.size # New (rescaled) image dimensions


def createPixelColorList(data):
    data.newImage = PIL.Image.new('RGB',data.imDim, "white")
    RGBIm = data.imageToDisplay.convert('RGB') 

    # Copy pixels from list to new image:
    for i in range(data.imDim[0]):
        for j in range(data.imDim[1]):
            r, g, b = RGBIm.getpixel((i,j))
            fillCurrPixelWith = data.pixelColorList[i][j]

    data.numBlackPixels = len(data.blackPixelLoc)


def createPixelPath(data):
    for j in range(len(data.pixelColorList[0])):
        for i in range(len(data.pixelColorList)):
            if isLegal(data, i, j):
                if data.visited[i][j] == False: 
                    getPixelPath(data, i, j)


def getPixelPath(data, startRow, startCol):
        # Base case:
        if not (isLegal(data, startRow, startCol)):
            return

        # Recursive case:
        else:
            # Go further down line...
            data.pixelPath.append([startRow, startCol])
            data.visited[startRow][startCol] = True
            for direction in data.dirs:
                row = startRow + direction[0]
                col = startCol + direction[1]
                result = getPixelPath(data, row, col)
            return None                


def isLegal(data, row, col):
    # Check for out of bounds:
    if ((row < 0 or row >= len(data.pixelColorList)) or 
        (col < 0 or col >= len(data.pixelColorList[0]))):
        return False
    # Check if white:
    elif (data.pixelColorList[row][col][0] == 255):
        return False
    # Check if black but already visited:
    elif ((data.pixelColorList[row][col][0] == 0) and
        (data.visited[row][col] == True)):
        return False
    return True


def readFileReformat(path):
    path = path.split(",")
    Xlist = []
    Ylist = []
    for element in path:
        element.strip()
        if "[" in element:
            temp = ""
            for char in element:
                try:
                    char2 = int(char)
                    temp += char
                except:
                    continue

            Xlist.append(int(char))

        else:
            temp2 = ""
            for char in element:
                try:
                    char2 = int(char)
                    temp2 += char
                except:
                    continue

            Ylist.append(int(temp2))

    pathOut = []    
    for i in range(len(Xlist)):
        pathOut.append([Xlist[i],Ylist[i]])

    return pathOut


def assignPixelOrdinals(data):
    counter = 0
    for location in data.pixelPath:
        for pixel in data.pixels:
            if ((pixel.row == location[0]) and (pixel.col == location[1])):
                pixel.ordinal = counter
                counter += 1


def writeText(canvas, data):
    mainText = "Image to Cut"
    canvas.create_text((data.width/2, data.margin + data.offsetImage/2),
            text = mainText, font = ("Purisa", "18", "bold"))

    oldFileText = "Original image filename: "
    oldDimText = "Pixel dimensions:"
    timeText = "Estimated cut time: "
    textStartX = data.imageDisplayWidth // 2 + 10
    textStartY = data.imageDisplayHeight + 85
    textPromptFont = ("Purisa", "12", "bold")
    textDataFont = ("Purisa", "12")
    pixelDimText = "("+str(data.imDim[0]) + "," + str(data.imDim[1]) + ")"

    # Make font smaller for longer times:
    data.totTimeToCut = getCutTime(data)
    if ((data.baseTimeMin == 0) and (data.baseTimeHour == 0)):
        chooseFont = ("Purisa", "12") # Just seconds
    elif ((data.baseTimeMin != 0) and (data.baseTimeHour == 0)):
        chooseFont = ("Purisa", "10") # ~minutes
    elif ((data.baseTimeMin != 0) and (data.baseTimeHour != 0)):
        chooseFont = ("Purisa", "8") # ~hours

    # Shorten filename if too long:
    data.filenameText = ""
    if (len(data.filename) > 10):
        counter = 0
        for letter in data.filename:
            if (counter < 10):
                data.filenameText += letter
                counter += 1
        data.filenameText += "..."
    else:
        data.filenameText = data.filename


    canvas.create_text(textStartX, textStartY, text = oldFileText, 
                font = textPromptFont)
    canvas.create_text(textStartX, textStartY + 15, text = oldDimText, 
                font = textPromptFont)
    canvas.create_text(textStartX, textStartY + 30, text = timeText, 
                font = textPromptFont)
    canvas.create_text(textStartX + 115, textStartY, 
                text = str(data.filenameText), font = textDataFont)
    canvas.create_text(textStartX + 85, textStartY + 15, 
                text = pixelDimText, font = textDataFont)
    canvas.create_text(textStartX + 98, textStartY + 32, 
                text = data.totTimeToCut, font = chooseFont)

    # Clearly differentiates between when must calc pixelPath and when load it
    if (data.isCalculating == True):
        canvas.create_text(data.width - 150, data.height // 2, 
                text = "Calculating pixel path...", font = chooseFont)
 

def getCutTime(data):
    data.baseTimeInSec = (data.stepperStartDelay + 
                data.stepperWaitPerCoord * (len(data.blackPixelLoc) - 1))
    data.baseTimeSec = 0
    data.baseTimeMin = 0
    data.baseTimeHour = 0

    if (data.filename != "NONE"):
        if (data.baseTimeInSec >= 60): # If more than 60 seconds
            data.baseTimeMin = data.baseTimeInSec // 60
            data.baseTimeSec = data.baseTimeInSec - (data.baseTimeMin * 60)
            if (data.baseTimeMin >= 60): # If more than 60 minutes
                data.baseTimeHour = data.baseTimeMin // 60
                data.baseTimeMin = data.baseTimeMin - (data.baseTimeHour * 60)
                return (str(data.baseTimeHour) + "hr, " + str(data.baseTimeMin) + "min, " 
                        + str(data.baseTimeSec) + "sec")
            else:
                return (str(data.baseTimeMin) + "min, " + str(data.baseTimeSec) + "sec")
        else:
            return (str(data.baseTimeInSec) + "sec")
    else:
        return (str(0) + " sec") 
   

def getFileName(data):
    data.longFileName = data.filename
    tempFilename = data.filename
    tempList = []

    for i in tempFilename.split("/"):
        tempList.append(i)

    data.filename = tempList[-1]


def getFolder(data):
    data.folderPath = ""
    for word in data.longFileName.split("/"):
        if ((word != "") and (word != data.filename)):
            data.folderPath += "/" + word    


def mainProgramMousePressed(event, data):
    pass


def mainProgramKeyPressed(event, data):
    pass


def mainProgramTimerFired(data):
    data.flashOn = not data.flashOn
    if (data.isCalcCount > 0):
        data.isCalcCount -= 1
    else:
        data.isCalculating = False


def mainProgramRedrawAll(canvas, data):
    # Background:
    data.imageStartX = data.margin + data.offsetImage
    data.imageStartY = data.imageStartX + 10
    data.imageEndX = data.imageStartX + data.imageDisplayWidth
    data.imageEndY = data.imageStartX + data.imageDisplayHeight + 10
    canvas.create_rectangle((data.margin, data.margin),
            (data.width - data.margin, data.height - data.margin), 
            fill = data.mainColor)
    data.laserBeamR = ImageTk.PhotoImage(file = "LaserBeamRight.gif")
    canvas.create_image(data.width//2 + 140, 30, image = data.laserBeamR)
    data.laserBeamL = ImageTk.PhotoImage(file = "LaserBeamLeft.gif")
    canvas.create_image(data.width//2 - 140, 30, image = data.laserBeamL)
     
    # Dark boxes, left and right:
    canvas.create_rectangle((data.imageStartX - 15, 
            data.imageStartY - 6), (data.imageEndX + 25, 
            data.imageEndY + 85), width = 0, fill = data.minorColor)
    canvas.create_rectangle((data.imageStartX + data.imageDisplayWidth 
            + data.between - 15, data.imageStartY - 6), (data.imageEndX + 
            data.imageDisplayWidth + data.between + 25, data.imageEndY + 85), 
            width = 0, fill = data.minorColor)

    # Main outlines, left and right:
    canvas.create_rectangle((data.imageStartX, data.imageStartY + 10),
            (data.imageEndX, data.imageEndY + 10), width = 3)
    canvas.create_rectangle((data.imageStartX + data.imageDisplayWidth 
            + data.between + 10, data.imageStartY + 10), (data.imageEndX + 
            data.imageDisplayWidth + data.between + 10, data.imageEndY + 10), 
            width = 3)
     
    # Fill in selected image, if one given:
    if ((data.filename != "NONE") and (data.readyToLoadImage == True)): 
        data.tkImage = ImageTk.PhotoImage(data.imageToDisplay)

        # Put image onto canvas:
        canvas.create_image((data.imageStartX, data.imageStartY + 10), 
                                        anchor = NW, image=data.tkImage)

        # Draw pixels (right), only if ready:
        if ((data.isCalculating == False) and (data.readyToDrawRight == True)):
            for pixel in data.pixels:
                xStart = int(data.imageDisplayWidth + data.margin + 
                        data.offsetImage +data.between + 10 
                        + data.pixelSize * pixel.row)
                yStart = int(data.margin + data.offsetImage + 20 + 
                        data.pixelSize * pixel.col)
                if pixel.color != "white":        
                    pixel.draw(canvas, xStart, yStart)

    else:
        # No image loaded yet; ask for one:
        canvas.create_text((data.imageDisplayWidth /2 + data.margin + 
            data.offsetImage, data.imageDisplayHeight / 2 + data.margin + 
            data.offsetImage), text = "Load image, please.")
        mainProgramInit(data, canvas) # So can choose new file

    # Write text:
    writeText(canvas,data)

    # Draw countdown box if clicked "cut":
    if data.hasClickedCut:
        canvas.create_rectangle((data.width*3/4 - 90, data.height - 90),
                    (data.width*3/4 + 69, data.height - 65), fill = "white",
                    width = 5)
        if (data.countdown > 0):
            timerText = "Time left: " + str(data.countdown) + " secs"
            canvas.create_text((data.width*3/4 - 80, data.height - 85),
                    fill = "darkred", text = timerText, anchor = NW)
        else:
            if ((data.flashOn == True) and (data.flashCount <= 3)):
                canvas.create_text((data.width*3/4 - 70, data.height - 85),
                        fill = "darkred", text = "DONE!", anchor = NW,
                        font = ("Purisa", "13", "bold"))
                data.flashCount += 1
            elif (data.flashCount > 3):
                canvas.create_text((data.width*3/4 - 60, data.height - 85),
                        fill = "darkred", text = "DONE!", anchor = NW,
                        font = ("Purisa", "13", "bold"))




################################################################################
# This run function was partially assimilated from the events-example#.py files,
# located in the Animations notes section.

def run(width = 300, height = 300):


    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # Pause, then call timerFired again:
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)


    def openDirSearchBox(data, canvas):
        if (data.mode == "mainProgram"):
            fileOpened = filedialog.askopenfilename()

            # Check if correct file type:
            while (not fileOpened.endswith(".gif") and (fileOpened != "")):
                tkinter.messagebox.showinfo("Warning", 
                        "Upload an IMAGE(.gif), please.")
                fileOpened = filedialog.askopenfilename()

            data.filename = fileOpened
            init(data, canvas)

        canvas.update()


    def startCut(data, canvas):
        # Check if running main program and constructed pixel path:
        if (data.mode == "mainProgram"):
            if (len(data.pixelPath) != 0): 
                data.hasClickedCut = True

                try:
                    cut = SerialComm(data)
                    data.countdown -= data.stepperStartDelay
                    data.button6.config(state = NORMAL)
                    for i in range(len(cut.all)):
                        if (data.stop == False):
                            cut.move(data, i)
                            if (i % 3 == 2):
                                data.countdown -= data.stepperWaitPerCoord
                            canvas.update()
                        else:
                            break
                    data.isCutDone = True
                    data.button5.config(state = NORMAL)

                except:
                    if (data.isCutDone == False):
                        tkinter.messagebox.showinfo("Warning", 
                                "Connect Arduino to computer, please.")
                    else:
                        pass

            else:
                tkinter.messagebox.showinfo("Warning", 
                        "Upload an image to cut, please.")
            
        canvas.update()


    def navigateToMain(data, canvas):
        if (data.mode == "welcomeScreen"):
            data.mode = "mainProgram"
            mainProgramInit(data, canvas)


    def navigateToMenu(data, canvas):
        if (data.mode == "mainProgram"):
            data.mode = "welcomeScreen"
            welcomeScreenInit(data, canvas)


    def saveSettings(data):
        if ((data.mode == "mainProgram") and (data.isCutDone)):
            prefix = data.filename.split(".")
            pathnameToSave = prefix[0] + "PixelPath.txt" # Name w/o extension
            
            try:
                saveFile = open(pathnameToSave, mode = 'x')
                saveFile.write(str(data.pixelPath))
                saveFile.close()
                tkinter.messagebox.showinfo("Save", "Current pixel path" + 
                    "successfully saved.")
            except:
                tkinter.messagebox.showinfo("Save", "File already exists.")

        
    def stopLaser(data):
        data.stop = True
        # Send command to turn off laser:
        stopCut = SerialComm(data) # Establish new connection
        laserOffIndex = stopCut.all[-1]
        stopCut.move(data,laserOffIndex)




    # Create root before calling init (so we can create images in init)
    root = Tk()

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 500 # milliseconds
    data.mode = "welcomeScreen"
    

    # Create the canvas:
    canvas = Canvas(root, width = data.width, height = data.height)
    canvas.pack()

    textWidget = Text(root, height = 1, width = 12)

    data.buttonParent = root

    # Make button to search for image file:
    data.button1 = Button(data.buttonParent, text = "Open new file", 
                command = lambda: openDirSearchBox(data, canvas))

    # Make button to start cut:
    data.button2 = Button(data.buttonParent, text = "Cut!", 
                command = lambda: startCut(data, canvas))

    # Make button to switch to main program:
    data.button3 = Button(data.buttonParent, text = "Proceed to cutting!",
                command = lambda: navigateToMain(data, canvas))

    # Make button to return to welcome page:
    data.button4 = Button(data.buttonParent, text = "Return to Menu",
                command = lambda: navigateToMenu(data, canvas))

    # Make button to save pixel path:
    data.button5 = Button(data.buttonParent, text = "Save Settings",
                command = lambda: saveSettings(data))

    # Make button to stop laser:
    data.button6 = Button(data.buttonParent, text = "Stop laser",
                command = lambda: stopLaser(data))


    def buttonManager(data, canvas):
        if (data.mode == "welcomeScreen"):
            welcomeScreenInit(data, canvas)
        elif (data.mode == "mainProgram"):
            mainProgramInit(data, canvas)

    buttonManager(data, canvas)
    init(data, canvas)

    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)

    # root.lift() # Opens app on top of other application windows
    
    # Launch the app
    root.mainloop()  # Blocks until window is closed.



run(600, 450)
