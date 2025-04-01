## Project7 3/27/25 3DGameEngineConcepts
## Comments on column 89
## All file names and folder names are capitalized (Assets/Planets/Textures/WhitePlanet.png)

## ToDo:
## HUD element to show ammo indicator and show when the rocket can fire again, it would flash.
## Add sun to game for lighting.
## Maybe fix the bug that crashes the game when shooting colliding missiles at certain angles (not sure what the problem is)
## Fix drone health being high somehow??? (maybe bad collider or multiple drones in one spot?)

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

        self.accept('escape', self.quit)  ## Esc to escape
        self.setupScene()
        self.setCamera()

        self.pusher.addCollider(self.player.collisionNode, self.player.modelNode)       # adds collider to player, the from object in this scenario
        self.cTrav.addCollider(self.player.collisionNode, self.pusher)                  # allows player collider to be interacted with by other objects by pushing
        self.cTrav.showCollisions(self.render)
        self.player.collisionNode.reparentTo(self.player.modelNode)

        #self.render.ls() ##Lists off the final version of the scene graph before making all of the drones

        fullCycle = 60               ## Change this to load faster
        for i in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCloudDefense(self.planet1, nickName)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawBaseballSeams(self.sun, nickName, i, fullCycle, 2)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCircleX(self.planet3, nickName, i, fullCycle, 225)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCircleY(self.planet4, nickName, i, fullCycle, 175)

            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)  ##Concantenation of nicknames for each drone made
            self.drawCircleZ(self.planet5, nickName, i, fullCycle, 425)
            
    def setupScene(self): ## snailCase for entire project
        self.universe = spaceJamClasses.Universe(self.loader, "Assets/Universe/Universe.x", self.render, "Universe", "Assets/Universe/Universe.jpg", (0,0,0), 14000)

        self.planet1 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Planet1", "Assets/Planets/Textures/Mercury.jpg",        160,   5000, 1890, 320) 
        self.planet2 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Planet2", "Assets/Planets/Textures/Moon.jpg",           400,   5400, 2270, 120) 
        self.planet3 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Planet3", "Assets/Planets/Textures/WhitePlanet.jpg",   -2700,  6200, 1270, 150) 
        self.planet4 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Planet4", "Assets/Planets/Textures/Neptune.jpg",       -2500,  6000, 970,  100) 
        self.planet5 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Planet5", "Assets/Planets/Textures/Venus.jpg",          3000, -6000, 230,  350)
        self.planet6 = spaceJamClasses.Planet(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Planet6", "Assets/Planets/Textures/GreyPlanet.jpg",    -3000, -6000, 730,  250) 
        
        self.sun     = spaceJamClasses.Sun(self.loader, "Assets/Planets/protoPlanet.x", self.render, "Sun", "Assets/Planets/Textures/Sun.jpg",            0,  2000,   0,  400, self.render) 
        
        self.spaceStation1 = spaceJamClasses.SpaceStation(self.loader, "Assets/SpaceStation/SpaceStation1B/spaceStation.x", self.render, "SpaceStation1", "Assets/SpaceStation/SpaceStation1B/SpaceStation1_Dif2.png", (200, -570, 0), 5) 
        #self.spaceStation2 = spaceJamClasses.SpaceStation(self.loader, "Assets/SpaceStation/SpaceStation1B/spaceStation.x", self.render, "SpaceStation2", "Assets/SpaceStation/SpaceStation1B/SpaceStation1_Dif2.png", (740, 0, 0), 6) 

        self.player = spaceJamClasses.Player(self.loader, self.taskMgr, self.accept, "Assets/Spaceships/Dumbledore/Dumbledore.x", self.render, "Player", (0, 0, 0), 1, (0, 0, 0), self.render, self.cTrav)

        self.sentinel1 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.render, "Sentinel1", 6.0, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet3, 250, "MLB", self.player)
        self.sentinel2 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.render, "Sentinel2", 6.0, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet3, 265, "MLB", self.player)
        
        self.sentinel3 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.render, "Sentinel3", 8.0, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet6, 20, "Cloud", self.player)
        self.sentinel4 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "Assets/DroneDefender/DroneDefender.obj", self.render, "Sentinel4", 8.0, "Assets/DroneDefender/octotoad1_auv.png", 
                                                 self.planet6, 20, "Cloud", self.player)

    def drawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 5)
        spaceJamClasses.Drone.droneCount += 1
    
    def drawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 400 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 10)
        spaceJamClasses.Drone.droneCount += 1
    
    def drawCircleX(self, centralObject, droneName, step, fullCircle, radius):
        unitVec = defensePaths.CircleX(step, fullCircle)
        unitVec.normalize()
        position = unitVec * radius + centralObject.modelNode.getPos() # adds relativity to the central object
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 5)
        spaceJamClasses.Drone.droneCount += 1

    def drawCircleY(self, centralObject, droneName, step, fullCircle, radius):
        unitVec = defensePaths.CircleY(step, fullCircle)
        unitVec.normalize()
        position = unitVec * radius + centralObject.modelNode.getPos() # adds relativity to the central object
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 5)
        spaceJamClasses.Drone.droneCount += 1
    
    def drawCircleZ(self, centralObject, droneName, step, fullCircle, radius):
        unitVec = defensePaths.CircleZ(step, fullCircle)
        unitVec.normalize()
        position = unitVec * radius + centralObject.modelNode.getPos() # adds relativity to the central object
        spaceJamClasses.Drone(self.loader, "Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "Assets/DroneDefender/octotoad1_auv.png", position, 5)
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