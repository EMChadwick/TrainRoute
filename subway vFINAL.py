# -*- coding: utf-8 -*-
#import libraries
from collections import defaultdict
import tkinter as tk
import csv
import copy # used as a shortcut for creating a copy of the station dictionary to mutate for route finding
import datetime # used to give the user more detailed information when they save their route
#///////////////////////////////////CLASSES//////////////////////////////////////////////


class CSV:
    """takes a CSV file and stores its data in a dictionary of lists"""
    #read a csv file into a dictionary
    def __init__(self, fileName):
        self.CSVDict = defaultdict(list)
        for record in csv.DictReader(open(fileName)):
              for key, val in record.items():   
                   self.CSVDict[key].append(val)
                   
   #to be used to add unique IDs to CSV files that have none                
    def addCol(self, key, column):
       self.CSVDict[key] = column
       
    #return a column from the csv file as a list    
    def getCol(self, colName):
        return self.CSVDict[colName]
       



class Station:
    """Represents one node on the network"""
    def __init__(self, coords, name):
        self.coords = coords
        self.name = name
        self.connections = []
        self.active = True
        
    #add a connection to a neighbour    
    def addConnection(self,ID, distance, line):
        self.connections.append((ID, distance, line))
    
    #remove a specified neighbor  - only used by the copy created for routefinding   
    def removeConnection(self,connection):
        self.connections.remove(connection)
    
    #return the station's coordinates
    def getCoords(self):
        return self.coords
    
    #return the station's name
    def getName(self):
        return self.name
    
    #return the station's list of connections
    def getConnections(self):
        return self.connections
    
    #return the active state of the station
    def isActive(self):
        return self.active
    
    #toggle the station
    def toggleActive(self):
            self.active = not self.active




"""A network composed of Stations"""
class Network:
    def __init__(self):
        self.stations = {}
        self.stationCount = 0
        self.closedLines = []
        self.lines = {}
     
    def addStation(self, ID, coords, name):
        self.stations[ID] = Station(coords, name)
        self.stationCount += 1
        
    #run Djikstra's Algorithm to find the fastest route between stwo given stations
    def findRoute(self, ID1, ID2):
        shortestDistance = {}
        predecessor = {}
        self.unVisited = self.stations.copy() #didn't realise python treats unVisited as a pointer to self.stations until I ran the algorithm with the GUI and all my stations disappeared. Lessons were learned.
        self.stationsCopy = copy.deepcopy(self.unVisited)
        infinity = 9999999999
        route = []
  
        try:
            if not (self.stations[ID1].isActive()):
                route.insert(0, "Starting station is closed, please choose \nanother station to begin your journey from")
                return(route, 0)
            if not(self.stations[ID2].isActive()):
                route.insert(0,"Destination station is closed, \nplease choose another")
                return(route, 0)
        except KeyError:
            route.insert(0,"Destination or starting station not found.")
            return(route, 0)
            
            
        #store all nodes as unvisited, store all nodes' distances as infinity
        for item in self.unVisited:
            shortestDistance[item] = infinity
            
        shortestDistance[ID1] = 0
        
        #remove all connections on closed lines from the copy dictionary
        for item in self.stationsCopy:
            for connection in self.stationsCopy[item].getConnections():
                    if (connection[2] in self.closedLines):
                        self.stationsCopy[item].removeConnection(connection)
        
        #main body of the Dijkstra's algorithm. probably 90% identical to most of the other assignments, but it works.
        while self.unVisited:
            minNode = None
            for node in self.unVisited:
                if minNode is None:
                    minNode = node
                elif (shortestDistance[node] < shortestDistance[minNode]):
                    minNode = node
            
            for connection in self.stationsCopy[minNode].getConnections():
                if (connection[2] in self.closedLines):
                    self.stationsCopy[minNode].removeConnection(connection)
            
            for connection in self.stationsCopy[minNode].getConnections():
                if (int(connection[1]) + shortestDistance[minNode] < shortestDistance[connection[0]]):
                    shortestDistance[connection[0]] = int(connection[1]) + shortestDistance[minNode]
                    predecessor[connection[0]] = minNode
            self.unVisited.pop(minNode)
        #end of Dijkstra's

        #create and return the list of stations in the route
        currentNode = ID2
        while (currentNode != ID1):
            try:
                route.insert(0, currentNode)
                currentNode = predecessor[currentNode]
            except KeyError:
                
                break
        route.insert(0, ID1)
        if(shortestDistance[ID2] != infinity):
            return(route, shortestDistance[ID2])


#///////////////////////////GUI PROGRAMMING//////////////////////////////

class GUI:
    """Contains all of the GUI objects and the interface methods"""
    def __init__(self):
        self.zoom = 1
        self.cwidth = 900
        self.cheight = 500
        self.stationSize = 2
        self.lineWidth = 5

        self.xOffset = self.stationSize +2
        self.yOffset = self.stationSize  +2 
        
        self.routeList = []
        self.routeLength = 0
        
        #/////////////CONSTRUCT THE LAYOUT////////////   
        self.window = tk.Tk()
        self.window.title("London Underground")
        self.window.iconbitmap('assets/icon.ico')
        #back contains leftFrame and routeFrame, 2 columns 1 row
        self.back = tk.Frame(master=self.window, width=1300, height=800, bg='grey')
        self.back.grid()


        # leftframe contains canvas and navFrame, 2 rows, 1 column
        self.leftFrame = tk.Frame(master=self.back, width=900, height=800, bg='white')
        self.canvas = tk.Canvas(master = self.leftFrame, width=self.cwidth+self.stationSize, height=self.cheight+self.stationSize, bg = "#efefef")
        #navframe contains cosuresFrame and buttonsFrame, 2 columns 1 row
        self.lowerFrame = tk.Frame(master=self.leftFrame, width=self.cwidth+self.stationSize, height=300, bg='white')                   
        self.closuresFrame = tk.Frame(master=self.lowerFrame, width=(self.cwidth+self.stationSize)/2, height=300,   bg='#AE6017')
        self.closuresFrame.grid_propagate(0)
        self.navFrame = tk.Frame(master=self.lowerFrame, width=(self.cwidth+self.stationSize)/2, height=300,   bg='grey')
        self.navFrame.grid_propagate(0)               
        self.routeFrame = tk.Frame(master=self.back, width=1300 -(self.cwidth+self.stationSize), height=806, bg='grey')
        self.routeFrame.grid_propagate(0)
        self.routeOutput = tk.Text(master = self.routeFrame, width = 48, height = 40, bg = "#4c5475", fg = "#0ed623")
        
        self.option = tk.StringVar(self.window) 
                        
        self.choices = linesCSV.getCol("name")                 
        self.option.set("Bakerloo Line")                           
        self.lineMenu = tk.OptionMenu(self.closuresFrame, self.option,  *self.choices,  command = self.colourShow)
        self.lineMenu.config(bg = "#d1e6fc")
        self.lineButton = tk.Button(self.closuresFrame, text="Open/Close", width = 10, bg = "#d1e6fc", command = self.lineToggle)
        self.allButton = tk.Button(self.closuresFrame, text="Open all", width = 10, bg = "#d1e6fc", command = self.openAll)
        self.log = tk.Text(master = self.closuresFrame, width = 60, height = 16.5, bg = "#4c5475", fg = "#0ed623")
        self.l1 = tk.Label(master = self.routeFrame, text="Choose start and end stations")
        self.l2 = tk.Label(master = self.navFrame, text="Use arrow keys to navigate around the map, \n and the mousewheel to zoom")  
        self.resetButton = tk.Button(master = self.navFrame, text = "Reset Map", width = 20, height = 2, bg = "#4aa3e2", command = self.reset)                 
                           
        
        #user controls
        self.canvas.bind("<Button-1>", self.callback) #toggles stations on click
        self.window.bind('<Right>', lambda event, direction = "right": self.move(event, direction))#   v
        self.window.bind('<Left>', lambda event, direction = "left": self.move(event, direction))#     controls for movement
        self.window.bind('<Up>', lambda event, direction = "up": self.move(event, direction))#         ^
        self.window.bind('<Down>', lambda event, direction = "down": self.move(event, direction))#     ^
        self.window.bind("<MouseWheel>", self.scale)# controls for zoom
        
        #window
        self.leftFrame.grid(row = 0, column = 1)
        
        #leftFrame
        self.canvas.grid(row=0, column=1)
        self.lowerFrame.grid(row=1, column=1)
        #lowerframe
        self.closuresFrame.grid(row=0, column=1)
        #closuresframe
        self.lineMenu.grid(row = 1, column = 1, sticky = 'w')
        self.log.grid(row = 2, column = 1, sticky = 's')
        self.lineButton.grid(row = 1, column = 1, pady=(0, 2), padx=(180, 0),sticky = 's')
        self.allButton.grid(row = 1, column = 1, pady=(0, 2), padx=(340, 0), sticky = 's')
        self.log.insert(tk.END, "Actions log \n")
        self.log.configure(state='disabled')
        #end of closuresframe
        self.navFrame.grid(row=0, column=2)
        #navFrame
        self.l2.grid(row = 1, column = 1, pady=(10, 2), padx=(100, 0), sticky = 's')
        self.resetButton.grid(row = 2, column = 1, pady=(10, 2), padx=(100, 0), sticky = 's')
        #end of navFrame
        #end of lowerframe
        #end of leftFrame 
        
        self.routeFrame.grid(row=0, column=2) 
        
        
        self.choices = {}
        for item in theNetwork.stations:
            k = theNetwork.stations[item].getName()
            v = item
            self.choices[k] = v
        self.inputOne = tk.Entry(self.routeFrame, width = 28)
        self.inputTwo = tk.Entry(self.routeFrame, width = 28)
        self.routeButton = tk.Button(self.routeFrame, text="GO", width = 15, bg = "#d1e6fc", command = self.showRoute)
        self.swapButton = tk.Button(self.routeFrame, text="<>", width = 5, height = 1, bg = "#d1e6fc", command = self.inputSwap)
        self.saveButton = tk.Button(self.routeFrame, text = "Save Route", width = 50, height = 3, bg = "#d1e6fc", command = self.saveRoute)
        
        #routeFrame
        self.l1.grid(row = 1, column = 1, sticky = 's') 
        self.inputOne.grid(row = 2, column = 1, pady=(10, 0), padx=(2, 0), sticky = 'w') 
        self.swapButton.grid(row = 2, column = 1, pady=(10, 0), padx=(4, 0), sticky = 'n')
        self.inputTwo.grid(row = 2, column = 1, pady=(10, 0), padx=(2, 0), sticky = 'e') 
        self.routeButton.grid(row = 3, column = 1, pady=(5, 0), sticky = 's')
        self.routeOutput.grid(row = 4, column = 1, pady=(5, 0), padx=(5, 0))
        self.saveButton.grid(row = 5, column = 1, pady=(5, 0), padx=(5, 0))
        self.routeOutput.insert(tk.END, "Route output")
        self.routeOutput.configure(state='disabled')
        self.saveButton.config(state = "disabled") 
        #end of Routeframe        
        #end of window
       
        #///////////END OF LAYOUT CONSTRUCTION//////////////


    #toggle stations on click
    def callback(self, event):
    
        for item in theNetwork.stations:
            crds = self.normalise(theNetwork.stations[item].getCoords())  
        #print(crds)
            x1 = (((crds[1])-self.stationSize) + self.xOffset)*self.zoom
            y1 = ((self.cheight - ((crds[0])-self.stationSize)) + self.yOffset)*self.zoom
            x2 = (((crds[1])+self.stationSize) + self.xOffset)*self.zoom
            y2 = ((self.cheight - ((crds[0])+self.stationSize)) + self.yOffset)*self.zoom
            if (event.x > x1 and event.x < x2 and event.y < y1 and event.y > y2):
                theNetwork.stations[item].toggleActive()
                stationN = theNetwork.stations[item].getName()
                if (theNetwork.stations[item].isActive()):
                    self.log.configure(state='normal')
                    self.log.insert(tk.END, (stationN + " has been opened \n"))
                    self.log.configure(state='disabled')
                if not (theNetwork.stations[item].isActive()):
                    self.log.configure(state='normal')
                    self.log.insert(tk.END, (stationN + " has been closed \n"))
                    self.log.configure(state='disabled')
                
                self.draw()
    
    #navigate around the map
    def move(self, event, direction):
        if (direction == "right"):
            self.xOffset -= (10/self.zoom)
            self.draw()
        if (direction == "left"):
            self.xOffset += (10/self.zoom)
            self.draw()
        if (direction == "down"):
            self.yOffset -= (10/self.zoom)
            self.draw()
        if (direction == "up"):
            self.yOffset += (10/self.zoom)
            self.draw()
            
            
    #TODO: fix the zoom so it zooms to the centre        
    #zoom in and out using the scroll wheel
    def scale(self, event):
        x,y = self.window.winfo_pointerxy()
        widget = self.window.winfo_containing(x,y)
        
        #only zoom if the mouse is on the canvas
        if (str(widget) == ".!frame.!frame.!canvas"):
            if (event.delta == -120):
                self.zoom = self.zoom*0.9
                #self.xOffset -= 20
                    #print(self.zoom)
            if(event.delta == 120):
                self.zoom = self.zoom*1.1
                        #self.xOffset += 20
            
            if(self.zoom >100):
                #self.xOffset += 20
                self.zoom = 100
            if(self.zoom <1):
                self.zoom = 1 
                #self.xOffset -= 20
                #print(self.zoom)
            
            
            if (self.zoom < 10):
                self.stationSize = 2
            if (self.zoom > 10):
                self.stationSize = 1
            if (self.zoom > 10 and self.zoom > 50):
                self.stationSize = 0.5
            self.draw()
    
    #take coordinates of a station and normalise them for drawing on the canvas
    def normalise(self, crds):
        #nlat =   ((crds[0]-min)/(max-min))*width
        nlat =   int(((crds[0]-51.4022)/0.303)*self.cheight)
        #1 has to be added to make all the values positive.
        nlong = int((((crds[1]+1)-0.389)/0.862)*self.cwidth)
        return (nlat, nlong)    
    
    #Convert the two text inputs to station IDs if possible, then pass those to the Network's findRoute function and output the result to the output box
    def showRoute(self):
        self.routeOutput.configure(state='normal')
        self.routeOutput.delete(1.0,tk.END)
        SID1 = ""
        SID2 = ""
        routeSave = []
        try:
            SID1 = self.choices[self.inputOne.get()]
            SID2 = self.choices[self.inputTwo.get()]
            self.log.configure(state='normal')
            self.log.insert(tk.END, ( "Route calculated \n"))
            self.log.configure(state='disabled')
        except KeyError:
            print("")
            
        path = theNetwork.findRoute(SID1, SID2)
        if (path is None):
            self.routeOutput.insert(tk.END, ("Route not reachable. Check closures"))
            self.saveButton.config(state = "disabled")
        else:
            for item in path[0]:
                try:
                    self.routeOutput.insert(tk.END, (theNetwork.stations[item].getName()) + "\n")
                    routeSave.append(theNetwork.stations[item].getName() + "\n")
                    self.saveButton.config(state = "normal")
                except KeyError:
                    self.routeOutput.insert(tk.END, (item + "\n"))
                    self.saveButton.config(state = "disabled")
            if (path[0][0] is not "Destination or starting station not found."):
                self.routeOutput.insert(tk.END, ("Total length: " + str(path[1])))
        self.routeOutput.configure(state='disabled')
        self.routeList = routeSave
        try:
         self.routeLength = str(path[1])
         
        except:
         self.routeLength = 0
        
        
  
    #swap the text in the start and end station inputs
    def inputSwap(self):
        in1 = self.inputOne.get()
        in2 = self.inputTwo.get()
        
        self.inputOne.delete(0, 'end')
        self.inputTwo.delete(0, 'end')
        self.inputOne.insert(0, in2)
        self.inputTwo.insert(0, in1)
    
    #Add or remove lines from the closedLines list 
    def lineToggle(self):
        self.log.configure(state='normal')
        chosen = self.option.get()
        lNumber = theNetwork.lines[chosen]
        if(lNumber in theNetwork.closedLines):
            theNetwork.closedLines.remove(lNumber)
            self.log.insert(tk.END, (chosen + " has been opened \n"))
        else:
            theNetwork.closedLines.append(lNumber)
            self.log.insert(tk.END, (chosen + " has been closed \n"))
        self.log.configure(state='disabled')
        self.draw()
    
    #change the closuresFrame colour to the colour of the line selected
    def colourShow(self, chosen):
        finder = linesCSV.getCol("name").index(chosen)
        colour = ("#" + linesCSV.getCol("colour")[finder])
        self.closuresFrame.configure(background=colour)
    
    #clear the closedStations List
    def openAll(self):
        theNetwork.closedLines.clear()
        self.draw()
        self.log.configure(state='normal')
        self.log.insert(tk.END, ( "All lines open \n"))
        self.log.configure(state='disabled')
        #print(theNetwork.closedLines)
    
    #save the created route as a text file
    def saveRoute(self):
        f= open("route.txt","w+")
        date = datetime.datetime.now()
        f.write("Your train journey for " + str(date.day) + "/" + str(date.month) + "/" + str(date.year) + "\n")
        for l in self.routeList:
            f.write(l)
        f.write("Total journey time: " + self.routeLength + " minutes")
        self.log.configure(state='normal')
        self.log.insert(tk.END, ( "Route saved \n"))
        self.log.configure(state='disabled')
        
    #resets the canvas to its initial zoom and offset    
    def reset(self):
        self.zoom = 1
        self.xOffset = self.stationSize +2
        self.yOffset = self.stationSize  +2 
        self.draw()
        
    #update the canvas. draws stations on top of connections
    def draw(self):
        self.canvas.delete("all")
        #draw the connections
        for item in theNetwork.stations:
            for connec in theNetwork.stations[item].getConnections():
                destID = connec[0]
                finder = linesCSV.getCol("line").index(connec[2])
                colour = ("#" + linesCSV.getCol("colour")[finder])
                crds1 = self.normalise(theNetwork.stations[item].getCoords())
                crds2 = self.normalise(theNetwork.stations[destID].getCoords())
                cx1 = ((crds1[1]) + self.xOffset)*self.zoom
                cy1 = ((self.cheight - (crds1[0])) + self.yOffset)*self.zoom
                cx2 = ((crds2[1]) + self.xOffset)*self.zoom
                cy2 = ((self.cheight - (crds2[0])) + self.yOffset)*self.zoom
                if (connec[2] in theNetwork.closedLines):
                    self.canvas.create_line(cx1, cy1, cx2, cy2, fill = colour, width = self.lineWidth, dash = (5, 2)) + self.yOffset
                else:  
                    self.canvas.create_line(cx1, cy1, cx2, cy2, fill = colour, width = self.lineWidth) + self.yOffset
            
            #draw the stations        
        for item in theNetwork.stations: 
            crds = self.normalise(theNetwork.stations[item].getCoords())   
            x1 = (((crds[1])-self.stationSize) + self.xOffset)*self.zoom
            y1 = ((self.cheight - ((crds[0])-self.stationSize)) + self.yOffset)*self.zoom
            x2 = (((crds[1])+self.stationSize) + self.xOffset)*self.zoom
            y2 = ((self.cheight - ((crds[0])+self.stationSize)) + self.yOffset)*self.zoom
            if (theNetwork.stations[item].isActive()):
                sColour = 'green'
            if not (theNetwork.stations[item].isActive()):
                sColour = 'red' 
            self.canvas.create_rectangle(x1, y1, x2, y2, fill = sColour)
        
        #draw station names
        if (self.zoom > 10):
            for item in theNetwork.stations: 
                name = theNetwork.stations[item].getName()
                ncrds = self.normalise( theNetwork.stations[item].getCoords())
                nx = ((ncrds[1]) + self.xOffset)*self.zoom
                ny = (((self.cheight - (ncrds[0])) + self.yOffset)*self.zoom) - ((self.stationSize*1.6)*self.zoom)
                
                nameSize = str(int(2.2*(self.zoom - 7)))
                if (int(nameSize) > 21):
                    nameSize = 20
                #print(nameSize)
                self.canvas.create_text(nx,ny,fill="black",font=('Comic', nameSize, 'bold'), text=name)
        
        #draw the zoom level
        if (self.zoom > 5):
            self.zoomindex = ("Zoom level: " + str(int(self.zoom)))
        else:
            self.zoomindex = ("Zoom level: " + str(round(self.zoom, 1)))
        self.canvas.create_text(50,490,fill="black",font=('Comic', '10', 'bold'), text=self.zoomindex)  
#///////////////////////////END OF GUI//////////////////////////////////////////// 


#////////////////////////////////END OF CLASSES//////////////////////////////////////////////////


#checks to see whether this program is being used as a module and if not, run the London Underground code.
if __name__ == "__main__":    
    #construct CSV objects
    stationsCSV = CSV("london.stations.CSV")    
    connectionsCSV = CSV("london.connections.csv")
    linesCSV = CSV("london.lines.csv")
    #give connectionsCSV an additional column for unique IDs to be used for iteration
    newids = list(range(1, len(connectionsCSV.getCol("station1"))))
    connectionsCSV.addCol("ID", newids)

    #Construct Network
    theNetwork = Network()

    #generate stations from the stations CSV file and add them to the network
    for item in stationsCSV.getCol("id"):
        finder = stationsCSV.getCol("id").index(item)
        lat = float(stationsCSV.getCol("latitude")[finder])
        long = float(stationsCSV.getCol("longitude")[finder])
        nom = stationsCSV.getCol("name")[finder]
        theNetwork.addStation(item, (lat,long),nom)


    #populate each station's list of connections from the connections CSV file
    for id1 in theNetwork.stations:
    
        for item in connectionsCSV.getCol("ID"):
            finder = connectionsCSV.getCol("ID").index(item)
            s1 = connectionsCSV.getCol("station1")[finder]
            s2 = connectionsCSV.getCol("station2")[finder]
            line = connectionsCSV.getCol("line")[finder]
            time = connectionsCSV.getCol("time")[finder]
        
            #add connections where the station is station 1, and where it's station 2
            if (s1 == id1):
                theNetwork.stations[id1].addConnection(s2, time, line)
            
            if(s2 == id1):
                theNetwork.stations[id1].addConnection(s1, time, line)

    for item in linesCSV.getCol("name"):
        finder = linesCSV.getCol("name").index(item)
        theNetwork.lines[item] = linesCSV.getCol("line")[finder]
    
    #create the GUI object
    gui = GUI()

    #start the GUI
    gui.draw()

    gui.window.mainloop()