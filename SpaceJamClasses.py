import math
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.interval.IntervalGlobal import Sequence
from direct.task import Task
from direct.task.Task import TaskManager

import DefensePaths as defensePaths
from typing import Callable
from panda3d.core import Loader, NodePath, Vec3, CollisionHandlerEvent, Material, TransparencyAttrib
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
import re # Regex module import for string editing.
from CollideObjectBase import InverseSphereCollideObject, CapsuleCollidableObject, SphereCollidableObject, SphereCollidableObjectVec3, PlacedObject # type: ignore
from direct.gui.OnscreenImage import OnscreenImage

# --------------------------------------- Programmer controls ------------------------------------------|
printMissileInfo = 0    # Enables terminal output of missile string info, keeps destruction messages    |
printPosHprInfo = 0     # Enables terminal output of Pos and Hpr information of the model               |
printReloads = 0        # Enables reload messages                                                       |
# ------------------------------------------------------------------------------------------------------|

class Player(SphereCollidableObjectVec3):
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float, Hpr: Vec3, render, traverser, 
                 sun, planet1, planet3, planet5):
        super(Player, self).__init__(loader, modelPath, parentNode, nodeName, posVec, 10) ##Uses __init__ function from SphereCollideObject
        self.enableHUD()
        self.taskMgr = taskMgr
        self.accept = accept
        self.loader = loader
        self.render = render
        self.sun = sun
        self.planet1 = planet1
        self.planet3 = planet3
        self.planet5 = planet5
        
        #self.modelNode = loader.loadModel(modelPath)
        #self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        
        #self.modelNode.setName(nodeName)
        self.modelNode.setHpr(Hpr)
        self.fireMode = 'Single'                # Default firing mode
        self.reloadTime = 2.00
        self.missileDistance = 4000             # Time until missile explodes
        self.missileBay = 1                     # Only one missile at a time can be launched (originally)

        self.cntExplode = 0                     # Count of explosions (project6 slides)
        self.explodeIntervals = {}
        self.traverser = traverser
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.handleInto)    # "into" pattern under the CollisionHandlerEvent passed in to this method for analyzation 
                                                #   and for passing in information
        self.SetParticles()
        self.setKeyBindings()

        self.taskMgr.add(self.checkIntervals, 'checkMissiles', 34)
    
    def checkIntervals(self, task): #Object Polling in the dictionaries
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying(): # isPlaying returns true or false to see if the missile has gotten to the end of its path
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + " has reached the end of its fire solution")
                break # We break because when things are deleted from a dictionary, we have to refactor the dictionary so we can reuse it. 
                      # This is because when we delete things, there's a gap at that point
        return Task.cont

    def thrust(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyThrust, 'forward-thrust') # might be taskManager instead, taskMgr is whats on the website
        else:
            self.taskMgr.remove('forward-thrust')

    def applyThrust(self, task):
        rate = 15
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        self.printPosHpr()
        return task.cont                                    # Continue moving the players ship when returning
    
    def setKeyBindings(self): ##Movement for the player, review Warmup3
        self.accept('space', self.thrust, [1])
        self.accept('space-up', self.thrust, [0])

        self.accept('q', self.leftRoll, [1])
        self.accept('q-up', self.leftRoll, [0])

        self.accept('e', self.rightRoll, [1])
        self.accept('e-up', self.rightRoll, [0])

        self.accept('a', self.LeftTurn, [1])
        self.accept('a-up', self.LeftTurn, [0])

        self.accept('d', self.rightTurn, [1])
        self.accept('d-up', self.rightTurn, [0])

        self.accept('w', self.Up, [1])
        self.accept('w-up', self.Up, [0])

        self.accept('s', self.Down, [1])
        self.accept('s-up', self.Down, [0])

        self.accept('f', self.fire)
        self.accept('f-up', self.checkReload)

        self.accept('1', self.toggleFireMode)
        #self.accept('1-up', self.checkReload)

    def leftRoll(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyLeftRoll, 'left-roll')
        else:
            self.taskMgr.remove('left-roll')
    def rightRoll(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyRightRoll, 'right-roll')
        else:
            self.taskMgr.remove('right-roll')
    def applyLeftRoll(self, task):
        rate = 1
        #print('leftroll')
        self.printPosHpr()
        self.modelNode.setR(self.modelNode.getR() - rate)
        return task.cont
    def applyRightRoll(self, task):
        rate = 1
        #print('rightroll')
        self.printPosHpr()
        self.modelNode.setR(self.modelNode.getR() + rate)
        return task.cont
#------------------------------------------------------------------------------------
    def LeftTurn(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyLeftTurn, 'left-turn')
        else:
            self.taskMgr.remove('left-turn')
    def rightTurn(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyRightTurn, 'right-turn')
        else:
            self.taskMgr.remove('right-turn')
    def applyLeftTurn(self, task):
        rate = 1
        #print('leftturn')
        self.printPosHpr()
        self.modelNode.setH(self.modelNode.getH() + rate)
        return task.cont
    def applyRightTurn(self, task):
        rate = 1
        #print('rightturn')
        self.printPosHpr()
        self.modelNode.setH(self.modelNode.getH() - rate)
        return task.cont
#------------------------------------------------------------------------------------
    def Up(self, keyDown):
        
        if (keyDown):
            self.taskMgr.add(self.applyUp, 'up')
        else:
            self.taskMgr.remove('up')
    def Down(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyDown, 'down')
        else:
            self.taskMgr.remove('down')
    def applyUp(self, task):
        rate = 1
        #print('applyUp')
        self.printPosHpr()
        self.modelNode.setP(self.modelNode.getP() + rate)
        return task.cont
    def applyDown(self, task):
        rate = 1
        #print('applyDown')
        self.printPosHpr()
        self.modelNode.setP(self.modelNode.getP() - rate)
        return task.cont
    
    def printPosHpr(self):
        #print("renderPos: " + str(self.render.getPos()))
        #print("renderHPR: " + str(self.render.getHpr()))
        Pattern = r'LVecBase3f'
        
        if printPosHprInfo == 1:
            self.posRounded = (int(round(self.modelNode.getX(), 0)),int(round(self.modelNode.getY(), 0)), int(round(self.modelNode.getZ(), 0)))
            print("modelPOS:  " + str(self.posRounded))
            strippedHpr = re.sub(Pattern, '', str(self.modelNode.getHpr()))
            print("modelHPR:  " + strippedHpr)
        return

    def fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())  # The dirction the spaceship is facing (changed from self.render)
            aim.normalize()                                                         # Normalizing a vector makes it consistent all the time
            fireSolution = aim * travRate
            inFront = aim * 150                                                     # Stores where the missile starts its path in comparison to the spaceship
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)                             # Creates a tag for each missile that details the number of the missile
            posVec = self.modelNode.getPos() + inFront

            #Create our missile
            currentmissile = Missile(self.loader, 'Assets/Phaser/phaser.egg', self.render, tag, posVec, 3.0)
            self.traverser.addCollider(currentmissile.collisionNode, self.handler)  # (project6) used to allow the traverser to traverse through this collider
            self.updateHUDAmmo("Empty")
            Missile.Intervals[tag] = currentmissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
            
        else: #Start reloading
            self.checkReload()
            
    def reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            if printReloads == 1: print("reload complete")
            self.updateHUDAmmo("Full")
            return Task.done
        elif task.time <= self.reloadTime:
            if printReloads == 1: print("Still reloading!")
            return Task.cont
        if self.missileBay > 1: # if the missiles ever glitch out
            self.missileBay = 1
            return Task.done
        
    def getReloadTime(self):
        return self.reloadTime
    
    def checkReload(self):
        if not self.taskMgr.hasTaskNamed('reload'):
                if printReloads == 1: print('Reloading')
                self.taskMgr.doMethodLater(0, self.reload, 'reload')
                return Task.cont
        
    def toggleFireMode(self):
        if not self.taskMgr.hasTaskNamed('reload'): # Cannot switch while reloading
            if self.fireMode == 'Single':
                self.fireMode = 'Cluster'
                print(self.fireMode)
                self.updateHUDAmmo('Full')

                self.crosshair.destroy()
                self.crosshair = OnscreenImage(image = "Assets/Hud/ClusterCrosshair.png", pos = Vec3(0,0,0), scale = 0.4)
                self.crosshair.setTransparency(TransparencyAttrib.MAlpha)
            else:
                self.fireMode = 'Single'
                print(self.fireMode)
                self.updateHUDAmmo('Full')

                self.crosshair.destroy()
                self.crosshair = OnscreenImage(image = "Assets/Hud/crosshair4.png", pos = Vec3(0,0,0), scale = 0.3)
                self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

    def enableHUD(self): #Used to be in MyApp before
        self.controls = OnscreenImage(image = "Assets/Hud/hudControls.png", pos = Vec3(0,0,0), scale = 1.0)
        self.controls.setTransparency(TransparencyAttrib.MAlpha)

        self.crosshair = OnscreenImage(image = "Assets/Hud/crosshair4.png", pos = Vec3(0,0,0), scale = 0.3)
        self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

        self.hud = OnscreenImage(image = "Assets/Hud/hudV3ExFullAmmo.png", pos = Vec3(0,0,0), scale = 1)
        self.hud.setTransparency(TransparencyAttrib.MAlpha)

    def updateHUDAmmo(self, ammoStr: str): #Updates the HUD to show ammo
        if (ammoStr == "Empty" and self.fireMode == 'Single'):
            self.hud.destroy()
            self.hud = OnscreenImage(image = "Assets/Hud/hudV3ExNoAmmo.png", pos = Vec3(0,0,0), scale = 1)
            self.hud.setTransparency(TransparencyAttrib.MAlpha)
            
        elif (ammoStr == "Full" and self.fireMode == 'Single'):
            self.hud.destroy()
            self.hud = OnscreenImage(image = "Assets/Hud/hudV3ExFullAmmo.png", pos = Vec3(0,0,0), scale = 1)
            self.hud.setTransparency(TransparencyAttrib.MAlpha)

        elif (ammoStr == "Empty" and self.fireMode == 'Cluster'):
            self.hud.destroy()
            self.hud = OnscreenImage(image = "Assets/Hud/hudV3ClstNoAmmo.png", pos = Vec3(0,0,0), scale = 1)
            self.hud.setTransparency(TransparencyAttrib.MAlpha)

        elif (ammoStr == "Full" and self.fireMode == 'Cluster'):
            self.hud.destroy()
            self.hud = OnscreenImage(image = "Assets/Hud/hudV3ClstFullAmmo.png", pos = Vec3(0,0,0), scale = 1)
            self.hud.setTransparency(TransparencyAttrib.MAlpha)

    def handleInto(self, entry):    # entry contains the collision information (name and pos of hit) also decides which objects are to be destroyed (project6)
                                    # entry is a search pattern under the CollisionHandler that searches for "From" and "Into" collisions and other info about those collisions
        fromNode = entry.getFromNodePath().getName()
        if printMissileInfo == 1: print("fromNode:" + fromNode)

        intoNode = entry.getIntoNodePath().getName()
        if printMissileInfo == 1: print("intoNode:" + intoNode)

        intoPosition = Vec3(entry.getSurfacePoint(self.render))     # logs where the into object was hit

        tempVar = fromNode.split('_')                               # All of this makes variables out of the names of the strings, splitting where certain characters are
        if printMissileInfo == 1: print("tempVar: " + str(tempVar))

        shooter = tempVar[0]
        if printMissileInfo == 1: print("Shooter: " + str(shooter))

        tempVar = intoNode.split('-')       # splits into an array at every -
        if printMissileInfo == 1: print("tempVar1: " + str(tempVar))

        tempVar = intoNode.split('_')
        if printMissileInfo == 1: print("tempVar2: " + str(tempVar))

        victim = tempVar[0]
        if printMissileInfo == 1: print("Victim: " + str(victim))
        
        pattern = r'[0-9]' # pattern to remove the numbers 0-9, uses Regex import
        strippedString = re.sub(pattern, '', victim) # replaces numbers with nothing, removes numbers from victim
        if printMissileInfo == 1: print("StrippedString: ", strippedString)

        if (strippedString == "Drone" or strippedString == "Planet" or strippedString == "SpaceStation" or strippedString == "Sentinel" or strippedString == "Wanderer"): #Excludes the sun and the universe
            if printMissileInfo == 1: print(victim, ' hit at ', intoPosition, ' (', intoNode, ')')
            self.destroyObject(victim, intoPosition)
        elif(strippedString == "Sun"):
            self.explodeNode.setPos(intoPosition)
            self.explode()
            Missile.Intervals[shooter].finish()
        elif(strippedString == "Universe"):
            self.explodeNode.setPos(intoPosition)
            self.explode()
            Missile.Intervals[shooter].finish()
        
        try:
            if printMissileInfo == 0: print(shooter + " is destroyed")
            Missile.Intervals[shooter].finish()
        except:
            print("Multiple different targets hit at once, known bug occured")

    def destroyObject(self, hitID, hitPos):
        try:
            nodeID = self.render.find("**/" + hitID + "*") # used to be self.render.find(hitID)
            nodeID.detachNode()
            #print("nodeID found under render")
        except:
            try:
                nodeID = self.sun.modelNode.find(hitID)
                nodeID.detachNode()
                #print("nodeID found under sun")
            except:
                print("No nodeID found")
        #
        
        self.explodeNode.setPos(hitPos)
        self.explode()
    
    def explode(self):
        self.cntExplode += 1
        tag = "particles-" + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.explodeLight, duration = 2.0) # 2.0 was 4.0, set to 2 so it wouldn't explode twice
        self.explodeIntervals[tag].start()

    def explodeLight(self, t):
        #for i in range(len(self.explodeEffect)):
        if (t == 1.0) and self.fireMode == 'Single':
            self.explodeEffect[0].disable()

        elif (t == 1.0) and self.fireMode == 'Cluster':
            if self.explodeEffect[0]: self.explodeEffect[0].disable()
            if self.explodeEffect[1]: self.explodeEffect[1].disable()
            if self.explodeEffect[2]: self.explodeEffect[2].disable()

        elif t == 0 and self.fireMode == 'Single':
            self.explodeEffect[0].start(self.explodeNode)
        
        elif t == 0 and self.fireMode == 'Cluster':
            self.explodeEffect[0].start(self.explodeNode)
            self.explodeEffect[1].start(self.explodeNode)
            self.explodeEffect[2].start(self.explodeNode)
    
    def SetParticles(self):
        base.enableParticles() # type: ignore
        
        explodeEffect1 = ParticleEffect()
        explodeEffect2 = ParticleEffect()
        explodeEffect3 = ParticleEffect()
        self.explodeEffect = [explodeEffect1, explodeEffect2, explodeEffect3]
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')
        for i in range(len(self.explodeEffect)):
            self.explodeEffect[i].loadConfig("Assets/ParticleEffects/basic_xpld_efx.ptf")
            self.explodeEffect[i].setScale(50)
            particleMat = Material()
            particleMat.setEmission((1, 1, 1, 1))
            self.explodeEffect[i].setMaterial(particleMat, 1)
            if i == 0:
                self.explodeEffect[i].setPos(0,0,0)
            else:
                self.explodeEffect[i].setPos(defensePaths.Cloud(35))
            print(self.explodeEffect[i].getParticlesList())
            #self.explodeEffect[i].reparentTo(self.explodeNode)
        


class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, posVec, 0.9) ##Uses __init__ function from InverseSphereCollideObject
        #self.modelNode = loader.loadModel(modelPath)
        #self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        #self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class SpaceStation(CapsuleCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 3, 1, 3, -9, -4, -9, 7)     ##Defines ax, ay, az, etc. for capsule
        #self.modelNode = loader.loadModel(modelPath)
        #self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        #self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        #print("spacestation " + nodeName + " created")

class Planet(SphereCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, x: float, y: float, z: float, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, 0, 0, 0, 1.1)
        #self.modelNode = loader.loadModel(modelPath)
        #self.modelNode.reparentTo(parentNode)
        self.modelNode.setPos(x,y,z)
        self.modelNode.setScale(scaleVec)
        self.nodeName = nodeName
        if nodeName == "Sun":
            self.modelNode.setHpr(90,0,0)
        
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
class Drone(SphereCollidableObject):
    droneCount = 61 # having this number below ~30 ish makes the drones take more hits for some reason
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float): # type: ignore
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, 0, 0, 0, 4)
        #self.modelNode = loader.loadModel(modelPath)
        #self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        #self.modelNode.setName(nodeName)
        
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        #print(nodeName, " created")

class Orbiter(SphereCollidableObjectVec3):  # Orbiter is a type of drone that moves around an object (project7)
    numOrbits = 0                       # Used for naming each sentinel's orbit
    velocity = 0.035                    # Speed of orbiting
    cloudTimer = 240                    # Controls how long until the drones move
    def __init__(self, loader: Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, 
                 centralObject: PlacedObject, orbitRadius: float, orbitType: str, staringAt: Vec3):
        super(Orbiter, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.2)
        self.taskMgr = taskMgr
        self.orbitType = orbitType
        self.modelNode.setScale(scaleVec)
        #self.nodeName = nodeName

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.orbitObject = centralObject
        self.orbitRadius = orbitRadius
        self.staringAt = staringAt
        Orbiter.numOrbits += 1

        self.cloudClock = -1                                    # Used to check how long the cloud drone has been in one spot
        self.taskFlag = "Traveler-" + str(Orbiter.numOrbits)    # Custom name for each orbit used for task names
        taskMgr.add(self.orbit, self.taskFlag)
    
    def orbit(self, task):
        if self.orbitType == "MLB":
            positionVec = defensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 2.0)
            self.modelNode.setPos(((positionVec * self.orbitRadius )/80) + self.orbitObject.modelNode.getPos())
            #print(self.nodeName, ":  ", positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())

        elif self.orbitType == "Cloud":
            if self.cloudClock == -1:
                self.modelNode.setPos(3, 3, 0)
            
            if self.cloudClock < Orbiter.cloudTimer:
                self.cloudClock += 1
            else:
                self.cloudClock = 0
                positionVec = defensePaths.Cloud(self.orbitRadius)
                self.modelNode.setPos(((positionVec * self.orbitRadius)/80) + self.orbitObject.modelNode.getPos())
                #print(self.nodeName, ":  ", positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
            
        
        self.modelNode.lookAt(self.staringAt.modelNode)
        return task.cont

class Missile(SphereCollidableObject):
    fireModels = {}             # Dictionaries
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0): # type: ignore
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, 0, 0, 0, 3.0)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        print("Fire Missile" + str(Missile.missileCount)) #Moved from below the .show() part below
        Missile.missileCount += 1
        
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        
class Sun(Planet):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, x: float, y: float, z: float, scaleVec: float, render):
        super(Sun, self).__init__(loader, modelPath, parentNode, nodeName, texPath, x, y, z, scaleVec)
        
        self.sunTemp = 5772                             # 5772 is the temperature of our sun (kelvin)
        #self.sunNode = loader.loadModel(modelPath)
        self.brightness = 1

        self.setLight(render, x, y, z)

    def setLight(self, render, x, y, z):
        sunLight = PointLight('sunLight')               # type: ignore
        sunLightNode = render.attachNewNode(sunLight)
        sunLight.attenuation = (1, 0, 0)              # Strength of light
        sunLight.color = (0.93*self.brightness, 1*self.brightness, .40*self.brightness, 1)
        #sunLight.setColorTemperature(self.sunTemp)
        sunLightNode.setPos(x, y, z)
        render.setLight(sunLightNode)

class Wanderer(SphereCollidableObjectVec3):
    numWanderers = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, modelName: str, scaleVec: Vec3, texPath: str, staringAt: Vec3, speed: int):
        super(Wanderer, self).__init__(loader, modelPath, parentNode, modelName, Vec3(0,0,0), 3.2)
        self.speed = speed
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.staringAt = staringAt
        Wanderer.numWanderers += 1
        #self.modelName = modelName #+ str(Drone.droneCount)
        #Drone.droneCount += 1
        #print(self.modelName)

        if Wanderer.numWanderers == 1: # Leader of route 1
            self.defineRoute(Vec3(1, 1, 2), Vec3(-5, -10, 2), Vec3(0, -20, 2), Vec3(10, -20, 1))
            #self.defineRoute(Vec3(0.1, 0, 2), Vec3(0.1, 0, 2), Vec3(0.1, 0, 2), Vec3(0.1, 0, 2))

        elif Wanderer.numWanderers == 2: # Follower of route 1
            self.defineRoute(Vec3(1, 1.25, 2.25), Vec3(-5, -9.75, 2.25), Vec3(0, -19.75, 2.25), Vec3(10, -19.75, 1.25))
            #self.defineRoute(Vec3(0.2, 0, 2), Vec3(0.2, 0, 2), Vec3(0.2, 0, 2), Vec3(0.2, 0, 2))


        elif Wanderer.numWanderers == 3: # Leader of route 2
            self.defineRoute(Vec3(0, 0, 2), Vec3(5, 10, 2), Vec3(0, 20, 2), Vec3(-10, 20, 1))
            #self.defineRoute(Vec3(0.3, 0, 2), Vec3(0.3, 0, 2), Vec3(0.3, 0, 2), Vec3(0.3, 0, 2))

            
        elif Wanderer.numWanderers == 4: # Follower of route 2
            self.defineRoute(Vec3(0, -0.25, 1.75), Vec3(5, 9.75, 1.75), Vec3(0, 19.75, 1.75), Vec3(-10, 19.75, 0.75))
            #self.defineRoute(Vec3(0.4, 0, 2), Vec3(0.4, 0, 2), Vec3(0.4, 0, 2), Vec3(0.4, 0, 2))

        else:
            print("Not enough routes specified for the number of wanderers spawned")

        try:
            self.travelRoute.loop()
        except:
            print("No travelRoute defined for wanderer", Wanderer.numWanderers)

    def defineRoute(self, originPos, pos1, pos2, pos3):
            self.posInterval0 = self.modelNode.posInterval(self.speed, pos1, startPos = originPos)
            self.posInterval1 = self.modelNode.posInterval(self.speed, pos2, startPos = pos1)
            self.posInterval2 = self.modelNode.posInterval(self.speed, pos3, startPos = pos2)
            self.posInterval3 = self.modelNode.posInterval(self.speed*2, originPos, startPos = pos3) # To start point
        
            self.travelRoute = Sequence(self.posInterval0, self.posInterval1, self.posInterval2, self.posInterval3, name = "Traveler" + str(Wanderer.numWanderers))

        #self.travelRoute.loop()
