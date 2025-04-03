## Project7 4/2/25 3DGameEngineConcepts
## Comments on column 89
## All file names and folder names are capitalized (Assets/Planets/Textures/WhitePlanet.png)

import math, sys, random
from direct.showbase.ShowBase import ShowBase 
import DefensePaths as defensePaths # type: ignore
import SpaceJamClasses as spaceJamClasses # type: ignore
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, Vec3, TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task
from direct.task.Task import TaskManager

class MyApp(ShowBase):
    def __init__(self): ## Constructor
        ShowBase.__init__(self)
        print("--------------------------------- Running SpaceJam ----------------------------------------")
        self.cTrav = CollisionTraverser()                                               # Collision setup
        self.cTrav.traverse(self.render)
        self.pusher = CollisionHandlerPusher()
        self.rot = 1
        self.rotationIndex = 0

        self.accept('escape', self.quit)  ## Esc to escape
        self.setupScene()
        self.setCamera()
        self.taskMgr.add(self.setRotations, 'rotatingPlanets', 24) 

        self.pusher.addCollider(self.player.collisionNode, self.player.modelNode)       # adds collider to player, the from object in this scenario
        self.cTrav.addCollider(self.player.collisionNode, self.pusher)                  # allows player collider to be interacted with by other objects by pushing
        self.cTrav.showCollisions(self.render)
        self.player.collisionNode.reparentTo(self.player.modelNode)
        
        self.accept('r', self.changeRotations)
        #self.accept('2', self.pauseRotations)
        #self.accept('1-up', self.changeRotations)  

        #self.render.ls() ##Lists off the final version of the scene graph before making all of the drones

        fullCycle = 60               ## Change this to load faster
        for i in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCloudDefense(self.planet1, nickName)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawBaseballSeams(self.sun, nickName, i, fullCycle, 3)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCircleX(self.planet3, nickName, i, fullCycle, 2)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCircleY(self.planet4, nickName, i, fullCycle, 2)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCircleZ(self.planet5, nickName, i, fullCycle, 2)
            
    def setupScene(self): ## snailCase for entire project
        self.universe = spaceJamClasses.Universe(self.loader, "Assets/Universe/Universe.x", self.render, "Universe", "Assets/Universe/Universe.jpg", (0,0,0), 14000)

        self.sun     = spaceJamClasses.Sun(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Sun", "Assets/Planets/Textures/Sun.jpg",            0,  0,   0,  400, self.render) 
        self.planet1 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.sun.modelNode, "Planet1", "Assets/Planets/Textures/Mercury.jpg",        10,   0, 0, 1) 
        self.planet2 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.sun.modelNode, "Planet2", "Assets/Planets/Textures/Moon.jpg",           -5,   -3, 0, 0.3)
        self.planet3 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.sun.modelNode, "Planet3", "Assets/Planets/Textures/WhitePlanet.jpg",   -10,  0, 0, 0.6) 
        self.planet4 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.sun.modelNode, "Planet4", "Assets/Planets/Textures/Neptune.jpg",       10,  -15, 0,  0.4) 
        self.planet5 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.sun.modelNode, "Planet5", "Assets/Planets/Textures/Venus.jpg",          10, 10, 2,  1)
        self.planet6 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.sun.modelNode, "Planet6", "Assets/Planets/Textures/GreyPlanet.jpg",    20, 5, 0,  1) 
    
        self.planets = [self.sun, self.planet1, self.planet2, self.planet3, self.planet4, self.planet5, self.planet6]

        self.spaceStation1 = spaceJamClasses.SpaceStation(self.loader, "Assets/SpaceStation/SpaceStation1B/spaceStation.x", self.render, "SpaceStation1", "Assets/SpaceStation/SpaceStation1B/SpaceStation1_Dif2.png", (500, -570, 0), 5) 
        #self.spaceStation2 = spaceJamClasses.SpaceStation(self.loader, "Assets/SpaceStation/SpaceStation1B/spaceStation.x", self.render, "SpaceStation2", "Assets/SpaceStation/SpaceStation1B/SpaceStation1_Dif2.png", (740, 0, 0), 6) 

        self.player = spaceJamClasses.Player(self.loader, self.taskMgr, self.accept, "Assets/Spaceships/Dumbledore/Dumbledore.x", self.render, "Player", (0, 0, 0), 1, (0, 0, 0), self.render, self.cTrav, 
                                             self.sun, self.planet1, self.planet3, self.planet5)

        self.sentinel1 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.planet3.modelNode, "Sentinel1", 0.05, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet3, 250, "MLB", self.player)
        self.sentinel2 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.planet3.modelNode, "Sentinel2", 0.05, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet3, 265, "MLB", self.player)
        
        self.sentinel3 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.planet6.modelNode, "Sentinel3", 0.05, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet6, 12, "Cloud", self.player)
        self.sentinel4 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.planet6.modelNode, "Sentinel4", 0.05, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet6, 12, "Cloud", self.player)
        
        #self.wanderer1 = spaceJamClasses.Wanderer(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "Assets/DroneDefender/octotoad1_auv.png", self.player, 10)
        #self.wanderer2 = spaceJamClasses.Wanderer(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "Assets/DroneDefender/octotoad1_auv.png", self.player, 10)
    
    def setRotations(self, task):
        if self.rotationIndex > len(self.planets) - 1:
            self.rotationIndex = 0
        name = self.planets[self.rotationIndex].nodeName
        #print("Sentinel1: " + str(self.sentinel1.modelNode.getPos()))
        #print("Planet3: " + str(self.planet3.modelNode.getPos()))
        #nodeID = self.sun.modelNode.find("Planet1")
        #print("nodeID test: " + str(nodeID))
        #pos = nodeID.getPos()
        #print(pos)
        
        x = self.planets[self.rotationIndex].modelNode.getPos()[0]
        y = self.planets[self.rotationIndex].modelNode.getPos()[1]
        z = self.planets[self.rotationIndex].modelNode.getPos()[2]
        h = self.planets[self.rotationIndex].modelNode.getHpr()[0]
        p = self.planets[self.rotationIndex].modelNode.getHpr()[1]
        r = self.planets[self.rotationIndex].modelNode.getHpr()[2]

        if task.time < 2000.0:
            if name == "Sun":
                self.planets[self.rotationIndex].modelNode.setHpr(h + self.rot*0.05,0,0)
            elif name == "Planet2":
                self.planets[self.rotationIndex].modelNode.setHpr(h + self.rot*1.2,0,0)
            else:
                self.planets[self.rotationIndex].modelNode.setHpr(h + self.rot*1,0,0)
            #print("rotating " + str(name))
            self.rotationIndex += 1
            return Task.cont
        else:
            print(str(name) + ' rotation done')
            return Task.done

    def changeRotations(self):
        self.taskMgr.remove('rotatingPlanets') 
        self.rot = self.rot * -1                # Change rotation direction
        print(self.rot)
        self.taskMgr.add(self.setRotations, 'rotatingPlanets', 24) 
        self.taskMgr.add(self.setRotations, 'rotatingPlanets', 24) 

    def pauseRotations(self):
        self.rotation.pause()

    def drawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 5)
        spaceJamClasses.Drone.droneCount += 1
    
    def drawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.sun.modelNode, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 0.05)
        spaceJamClasses.Drone.droneCount += 1
    
    def drawCircleX(self, centralObject, droneName, step, fullCircle, radius):
        unitVec = defensePaths.CircleX(step, fullCircle)
        unitVec.normalize()
        position = unitVec * radius + centralObject.modelNode.getPos() # adds relativity to the central object
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.sun.modelNode, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 0.05)
        spaceJamClasses.Drone.droneCount += 1

    def drawCircleY(self, centralObject, droneName, step, fullCircle, radius):
        unitVec = defensePaths.CircleY(step, fullCircle)
        unitVec.normalize()
        position = unitVec * radius + centralObject.modelNode.getPos() # adds relativity to the central object
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.sun.modelNode, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 0.05)
        spaceJamClasses.Drone.droneCount += 1
    
    def drawCircleZ(self, centralObject, droneName, step, fullCircle, radius):
        unitVec = defensePaths.CircleZ(step, fullCircle)
        unitVec.normalize()
        position = unitVec * radius + centralObject.modelNode.getPos() # adds relativity to the central object
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.sun.modelNode, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 0.05)
        spaceJamClasses.Drone.droneCount += 1

    def setCamera(self):
        self.disable_mouse()
        self.camera.reparentTo(self.player.modelNode)
        self.camera.setFluidPos(0, 0, 0)              # self.camera.setFluidPos(0, -90, 0) gives 3rd person POV, collision is attached to camera, not ship
        self.camera.setHpr(0, 0, 0)
    
    def quit(self):
        sys.exit()

app = MyApp()
app.run()