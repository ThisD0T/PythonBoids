import numpy as np
import random
import math
import pyglet
from pyglet.window import FPSDisplay

from Functions import normalize_vector, limit_vector, magnitude, set_magnitude, distance, get_vector

FPS = 1/144;

WWidth = 1280# terrible var names lol
WHeight = 720

mainBatch = pyglet.graphics.Batch()
arrows = []

#pyglet.resource.path = ['res']
#pyglet.resource.reindex()# you have to do this (remember)
triangle_image = pyglet.image.load("triangle.png")
triangle_image.anchor_x = triangle_image.height//2
triangle_image.anchor_y = triangle_image.width//2

mouseX = 0
mouseY = 0
# test comment

class Arrow():
    def __init__(self, x, y, batch, maxSpeed, maxForce, viewDistance):
        self.x = x
        self.y = y
        self.velocity = np.array([random.uniform(-2, 2), random.uniform(-2, 2)])
        self.position = np.array([self.x, self.y])
        self.acceleration = np.array([0, 0])

        # maxSpeed is the cap on how fast they can move
        # maxForce is how hard the autonomous character can steer
        self.maxSpeed = maxSpeed
        self.maxForce = maxForce

        self.viewDistance = viewDistance

        self.junge = pyglet.sprite.Sprite(triangle_image, self.x, self.y, batch=mainBatch)

        self.inView = []# I know this is a terrible name but I'm too lazy to fix right now


    def Seek(self, target=(0, 0)):# steering = desired - velocity
        desired = target - self.position
        steering = desired - self.velocity
        steering = set_magnitude(self.maxForce, steering)

        return steering

    def flee(self, target=(0, 0)):
        steering = target - self.position
        d = distance(self.position, target)
        steering = steering / (d * d)
        steering = set_magnitude(self.maxSpeed, steering)
        steering = steering - self.velocity
        steering = limit_vector(self.maxForce, steering)
        steering *= -1

        return steering


    def separation(self):
        steering = np.array([0, 0])
        for arrow in self.inView:
            d = distance(self.position, arrow.position)
            diff = get_vector(self.position, arrow.position)
            diff_numpy = np.array([diff[0], diff[1]])
            diff_numpy = diff_numpy / (d * d)# funny inverse square law
            steering = steering + diff_numpy

        steering = steering/len(self.inView)
        steering = set_magnitude(self.maxSpeed, steering)
        steering = steering - self.velocity
        steering = limit_vector(self.maxForce, steering)

        steering *= (-1)

        return steering

    def cohesion(self):
        steering = np.array([0, 0])
        for arrow in self.inView:
            steering = steering + arrow.position

        steering = steering/len(self.inView)
        steering -= self.position
        steering = set_magnitude(self.maxSpeed, steering)
        steering = steering - self.velocity
        steering = limit_vector(self.maxForce, steering)

        return steering

    def alignment(self):
        steering = np.array([0, 0])
        for arrow in self.inView:
            steering = steering + arrow.velocity

        steering = steering/len(self.inView)
        steering = set_magnitude(self.maxSpeed, steering)
        steering = steering - self.velocity
        steering = limit_vector(self.maxForce, steering)

        return steering

    def flock(self, dt):
        flee = self.flee((mouseX, mouseY))
        #separationForce = self.separation()
        if (len(self.inView) > 0):
            cohesion = self.cohesion()
            alignment = self.alignment()
            separation = self.separation()

            self.acceleration = self.acceleration + cohesion
            self.acceleration = self.acceleration + alignment
            self.acceleration = self.acceleration + separation
            #self.acceleration = self.acceleration + flee
            #self.acceleration *= dt

    def fovCalc(self):
        for arrow in arrows:
            if (distance(self.position, arrow.position) < self.viewDistance):
                if (arrow != self):# exclude self
                    self.inView.append(arrow)
                else:
                    pass
            else:
                try:
                    self.inView.remove(arrow)
                except:
                    pass

    def update(self, dt):
        self.velocity = self.velocity + self.acceleration# add acceleration to velocity
        self.velocity = limit_vector(self.maxSpeed, self.velocity)# limit the velocity
        self.position += self.velocity

        # sort out the rotation of the sprite to make it face the direction it's travelling
        self.radians = math.atan(self.velocity[0] / self.velocity[1])
        self.degrees = math.degrees(self.radians)
        self.velocityCheck = self.velocity# this is my hacky way of getting around having to do math
        if (self.velocityCheck[1] < 0):
            self.degrees += 180
        
        # set up the sprite's position and rotation
        self.junge.rotation = self.degrees
        self.junge.position = self.position

        self.acceleration = np.array([0, 0])# reset the acceleration vector

    def draw(self):
        self.junge.draw()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.FPSLabel = FPSDisplay(self)

        self.set_location(300, 50)
        

    def on_mouse_motion(self, x, y, dx, dy):
        global mouseX
        global mouseY
        mouseX = x
        mouseY = y
    
    def update(self, dt):# update objects
        for arrow in arrows:
            arrow.fovCalc()
            arrow.flock(dt)
            arrow.update(dt)

        self.keepInBounds()
             
    def on_draw(self):# purely the spot for DRAWING objects
        self.clear()

        mainBatch.draw()
        for arrow in arrows:
            arrow.draw()

        self.FPSLabel.draw()
        
    def keepInBounds(self):
        for arrow in arrows:
            if arrow.position[0] > self.width:
                arrow.position[0] = 0
            if arrow.position[0] < 0:
                arrow.position[0] = self.width

            if arrow.position[1] > self.height:
                arrow.position[1] = 0
            if arrow.position[1] < 0:
                arrow.position[1] = self.height

    def make_characters(self, num):
        for i in range(num):
            character = Arrow(random.uniform(0, self.width), random.uniform(0, self.height), mainBatch, 3, .2, 75)
            arrows.append(character)
            

if __name__ == "__main__":
    mainWindow = Window(WWidth, WHeight, "Steering Behaviours", resizable=False)
    mainWindow.make_characters(25)

    pyglet.clock.schedule_interval(mainWindow.update, FPS)

    pyglet.app.run()
