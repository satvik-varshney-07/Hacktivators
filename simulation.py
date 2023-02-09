import random
import time
import threading
import pygame
import sys
import os
import math



defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
simTime = 300
timeElapsed = 0

currentGreen = 0
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = 0

carTime = 2
pcarTime = 1
sTruckTime = 2.25
truckTime = 2.5
busTime = 2.5

noOfCars = 0
noOfPcars = 0
noOfBuses =0
noOfTrucks = 0
noOfSTrucks = 0
noOfLanes = 2
speeds = {'car':1.25, 'pcar':2.25, 'truck':1.15, 'sTruck':1.20, 'bus':1.0}

detectionTime = 5


# Coordinates of vehicles’ start
x = {'right':[0,0,0], 'down':[755,720,790], 'left':[1400,1400,1400], 'up':[602,583,650]}
y = {'right':[348,380,421], 'down':[0,0,0], 'left':[498,472,515], 'up':[800,800,800]}
vehicles = {'right': {0:[], 1:[], 2:[],'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'up':0}}
vehicleTypes = {0:'car', 1:'pcar', 2:'truck', 3:'sTruck', 4:'bus'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}
# Coordinates of signal image, timer, and vehicle count
signalCoods = [(502,257),(846,250),(838,553),(507,557)]
signalTimerCoods = [(472,263),(908,261),(897,562),(484,563)]
# Coordinates of stop lines
stopLines = {'right': 510, 'down': 330, 'left': 910, 'up': 595}
defaultStop = {'right': 480, 'down': 320, 'left': 920, 'up': 605}
stops = {'right': [510,510,510], 'down': [330,330,330], 'left': [910,910,910], 'up': [595,595,595]}
# Gap between vehicles
gap = 15    # stopping gap
movingGap = 15   # moving gap

timeElapsed = 0
simulationTime = 300
timeElapsedCoods = (1100,50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]




pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum , maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

        if (direction == 'right'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][
                self.index - 1].crossed == 0):  # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().width - gap  # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            else:
                self.stop = defaultStop[direction]
            # Set new starting and stopping coordinate
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif (direction == 'left'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif (direction == 'down'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif (direction == 'up'):
            if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp

        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if (self.direction == 'right'):
            if (self.crossed == 0 and self.x + self.currentImage.get_rect().width > stopLines[self.direction]):
                self.crossed =1
                vehicles[self.direction]['crossed'] += 1
            if ((self.x + self.currentImage.get_rect().width <= self.stop
                 or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0))
                    and (self.index == 0 or self.x + self.currentImage.get_rect().width
                         < (vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                self.x += self.speed
        elif (self.direction == 'down'):
            if (self.crossed == 0 and
                    self.y + self.currentImage.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
            if ((self.y + self.currentImage.get_rect().height <= self.stop
                 or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0))
                    and (self.index == 0 or self.y + self.currentImage.get_rect().height
                         < (vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                self.y += self.speed
        elif (self.direction == 'left'):
            if (self.crossed == 0 and
                    self.x < stopLines[self.direction]):
                self.crossed = 1
            if ((self.x >= self.stop or self.crossed == 1
                 or (currentGreen == 2 and currentYellow == 0))
                    and (self.index == 0 or self.x
                         > (vehicles[self.direction][self.lane][self.index - 1].x
                            + vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().width
                            + movingGap))):
                self.x -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and
                    self.y < stopLines[self.direction]):
                self.crossed = 1
            if ((self.y >= self.stop or self.crossed == 1
                 or (currentGreen == 3 and currentYellow == 0))
                    and (self.index == 0 or self.y
                         > (vehicles[self.direction][self.lane][self.index - 1].y
                            + vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().height
                            + movingGap))):
                self.y -= self.speed

def initialize():
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
        signals.append(ts4)
        repeat()

def setTime():
    global noOfCars, noOfPcars, noOfBuses, noOfTrucks, noOfSTrucks, noOfLanes
    global carTime, busTime, truckTime, pcarTime, sTruckTime
    os.system("say detecting vehicles, "+directionNumbers[(currentGreen+1)%noOfSignals])

    noOfCars, noOfPcars, noOfBuses, noOfTrucks, noOfSTrucks = 0,0,0,0,0
    for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
        vehicle = vehicles[directionNumbers[nextGreen]][0][j]
        if(vehicle.crossed==0):
            vclass = vehicle.vehicleClass
            # print(vclass)
            noOfPcars += 1
    for i in range(1,3):
        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
            vehicle = vehicles[directionNumbers[nextGreen]][i][j]
            if(vehicle.crossed==0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if(vclass=='car'):
                    noOfCars += 1
                elif(vclass=='bus'):
                    noOfBuses += 1
                elif(vclass=='truck'):
                    noOfTrucks += 1
                elif(vclass=='sTruck'):
                    noOfSTrucks += 1
    # print(noOfCars)
    greenTime = math.ceil(((noOfCars*carTime) + (noOfSTrucks*sTruckTime) + (noOfBuses*busTime) + (noOfTrucks*truckTime)+ (noOfPcars*pcarTime))/(noOfLanes+1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
    print('Green Time: ',greenTime)
    if(greenTime<defaultMinimum):
        greenTime = defaultMinimum
    elif(greenTime>defaultMaximum):
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[(currentGreen+1)%(noOfSignals)].green = greenTime




def repeat():
    global currentGreen, currentYellow, nextGreen
    while (signals[currentGreen].green > 0):
        updateValues()
        if (signals[(currentGreen + 1) % (noOfSignals)].red == detectionTime):  # set time of next green signal
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"
    for i in range(0, 3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while (signals[currentGreen].yellow > 0):
        updateValues()
        time.sleep(1)
    currentYellow = 0

    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = (nextGreen)
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()

def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

def generateVehicles():
    while(True):
        vehicle_type = random.randint(0,4)
        lane_number = random.randint(1,2)
        temp = random.randint(0,99)
        direction_number = 0
        dist= [25,50,75,100]
        if(temp<dist[0]):
            direction_number = 0
        elif(temp<dist[1]):
            direction_number = 1
        elif(temp<dist[2]):
            direction_number = 2
        elif(temp<dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
        time.sleep(1)



def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane',i+1,':',vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ',totalVehicles)
            print('Total time passed: ',timeElapsed)
            print('No. of vehicles passed per unit time: ',(float(totalVehicles)/float(timeElapsed)))
            os._exit(1)




class Main:
    thread4 = threading.Thread(name="simulationTime",target=simulationTime, args=())
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization", target=initialize, args=())
    thread2.daemon = True
    thread2.start()

    black = (0, 0, 0)
    white = (255, 255, 255)
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)
    background = pygame.image.load('images/intersection.jpeg')
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)
    thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
    thread3.daemon = True
    thread3.start()



    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                sys.exit()

        screen.blit(background, (0, 0))
        for i in range(0, noOfSignals):
            if (i == currentGreen):
                if (currentYellow == 1):
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if (signals[i].red <= 10):
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])


        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, timeElapsedCoods)

        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()

Main()




