from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.task.Task import TaskManager
import DefensePaths as defensePaths
from typing import Callable
from panda3d.core import *
from panda3d.core import Loader, NodePath, Vec3, CollisionHandlerEvent, Material
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
import re # Regex module import for string editing.
from CollideObjectBase import InverseSphereCollideObject, CapsuleCollidableObject, SphereCollidableObject, SphereCollidableObjectVec3, PlacedObject # type: ignore

# --------------------------------------- Programmer controls ------------------------------------------|
printMissileInfo = 0    # Enables terminal output of missile string info, keeps destruction messages    |
printPosHprInfo = 0     # Enables terminal output of Pos and Hpr information of the model               |
printReloads = 0        # Enables reload messages                                                       |
# ------------------------------------------------------------------------------------------------------|

class Player(SphereCollidableObjectVec3):
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float, Hpr: Vec3, render, traverser):
        super(Player, self).__init__(loader, modelPath, parentNode, nodeName, posVec, 10) ##Uses __init__ function from SphereCollideObject
        self.taskMgr = taskMgr
        self.accept = accept
        self.loader = loader
        self.render = render
        #self.modelNode = loader.loadModel(modelPath)
        self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        self.modelNode.setHpr(Hpr)

        self.reloadTime = 1.00
        self.missileDistance = 4000         # Time until missile explodes
        self.missileBay = 1                 # Only one missile at a time can be launched (originally)

        self.cntExplode = 0                 # Count of explosions (project6 slides)
        self.explodeIntervals = {}
        self.traverser = traverser
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.handleInto)

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

            Missile.Intervals[tag] = currentmissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
            
        else: #Start reloading
            self.checkReload()
            
    def reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            if printReloads == 1: print("reload complete")
            return Task.done
        elif task.time <= self.reloadTime:
            if printReloads == 1: print("Still reloading!")
            return Task.cont
        if self.missileBay > 1: # if the missiles ever glitch out
            self.missileBay = 1
            return Task.done
    
    def checkReload(self):
        if not self.taskMgr.hasTaskNamed('reload'):
                if printReloads == 1: print('Reloading')
                self.taskMgr.doMethodLater(0, self.reload, 'reload')
                return Task.cont

    def handleInto(self, entry): # entry contains the collision information (name and pos of hit) also decides which objects are to be destroyed (project6)
        fromNode = entry.getFromNodePath().getName()
        if printMissileInfo == 1: print("fromNode:" + fromNode)

        intoNode = entry.getIntoNodePath().getName()
        if printMissileInfo == 1: print("intoNode:" + intoNode)

        intoPosition = Vec3(entry.getSurfacePoint(self.render)) #logs where the into object was hit

        tempVar = fromNode.split('_')       # All of this makes variables out of the names of the strings, splitting where certain characters are
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

        if (strippedString == "Drone" or strippedString == "Planet" or strippedString == "SpaceStation"): #Excludes the sun and the universe
            print(victim, ' hit at ', intoPosition)
            self.destroyObject(victim, intoPosition)
        
        if printMissileInfo == 1: print(shooter + " is destroyed")
        Missile.Intervals[shooter].finish()

    def destroyObject(self, hitID, hitPos):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        self.explodeNode.setPos(hitPos)
        self.explode()
    
    def explode(self):
        self.cntExplode += 1
        tag = "particles-" + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.explodeLight, duration = 2.0) # 2.0 was 4.0, set to 2 so it wouldn't explode twice
        self.explodeIntervals[tag].start()

    def explodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)
    
    def SetParticles(self):
        base.enableParticles() # type: ignore
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("Assets/ParticleEffects/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(30)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')

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

        #self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
class Drone(SphereCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float): # type: ignore
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, 0, 0, 0, 2)
        #self.modelNode = loader.loadModel(modelPath)
        #self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        #self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
    droneCount = 0

class Orbiter(SphereCollidableObjectVec3):  # Orbiter is a type of drone that moves around an object (project7)
    numOrbits = 0                       # Used for naming each sentinel's orbit
    velocity = 0.005                    # Speed of orbiting
    cloudTimer = 240                    # Controls how long until the drones move
    def __init__(self, loader: Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, 
                 centralObject: PlacedObject, orbitRadius: float, orbitType: str, staringAt: Vec3):
        super(Orbiter, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.2)
        self.taskMgr = taskMgr
        self.orbitType = orbitType
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.orbitObject = centralObject
        self.orbitRadius = orbitRadius
        self.staringAt = staringAt
        Orbiter.numOrbits += 1

        self.cloudClock = 0             # Used to check how long the cloud drone has been in one spot
        self.taskFlag = "Traveler-" + str(Orbiter.numOrbits) # Custom name for each orbit used for task names
        taskMgr.add(self.orbit, self.taskFlag)
    
    def orbit(self, task):
        if self.orbitType == "MLB":
            positionVec = defensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 2.0)
            self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())

        elif self.orbitType == "Cloud":
            if self.cloudClock < Orbiter.cloudTimer:
                self.cloudTimer += 1
            else:
                self.cloudClock = 0
                positionVec = defensePaths.Cloud()
                self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
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
        print("Fire Missile #" + str(Missile.missileCount)) #Moved from below the .show() part below
        Missile.missileCount += 1
        
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        
class Sun(Planet):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, x: float, y: float, z: float, scaleVec: float, render):
        super(Sun, self).__init__(loader, modelPath, parentNode, nodeName, texPath, x, y, z, scaleVec)
        
        self.sunTemp = 5772                             # 5772 is the temperature of our sun (kelvin)
        self.sunNode = loader.loadModel(modelPath)
        
        self.setLight(render, x, y, z)
        self.setMaterial()
        

    def setLight(self, render, x, y, z):
        sunLight = PointLight('sunLight')               # type: ignore
        sunLightNode = render.attachNewNode(sunLight)
        sunLight.attenuation = (1, 0, 0)              # Strength of light
        sunLight.color = (11000, 10000, 10000, 1)
        #sunLight.setColorTemperature(self.sunTemp)
        sunLightNode.setPos(x, y, z)
        render.setLight(sunLightNode)
    
    def setMaterial(self):
        sunMat = Material()
        sunMat.setEmission((0,1000,0,1))
        self.sunNode.setMaterial(sunMat)
        