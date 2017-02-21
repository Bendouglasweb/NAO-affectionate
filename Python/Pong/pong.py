from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import math
import random

import cocos
from cocos.director import director
from cocos.actions import Delay, Rotate

import pyglet

class Scores(cocos.layer.Layer):
    def __init__(self):
        super(Scores,self).__init__()

        win_x = director.get_window_size()[0]
        win_y = director.get_window_size()[1]
        self.hits_pos = [0.1 * win_x,win_y-20]
        self.miss_pos = [0.4 * win_x,win_y-20]

        self.hits = 0
        self.misses = 0
        self.hits_goal = 1
        self.misses_goal = 15

        # Create hits label 10% from left border
        self.hits_label = cocos.text.Label("", x=self.hits_pos[0], y=self.hits_pos[1])

        # Create misses label 40% from left border
        self.miss_label = cocos.text.Label("", x=self.miss_pos[0], y=self.miss_pos[1])

        self.add(self.hits_label)
        self.add(self.miss_label)

    def update_text(self):
        self.hits_label.element.text = "Hits: " + str(self.hits) + " / " + str(self.hits_goal)
        self.miss_label.element.text = "Misses: " + str(self.misses) + " / " + str(
                self.misses_goal)





class UserPaddle(cocos.sprite.Sprite):

    def __init__(self,img='Resources/Paddle.png'):
        super(UserPaddle, self).__init__(img)
        self.x_pos = self.width/2
        self.y_pos = 120
        self.speed = 5
        self.position = self.x_pos, self.y_pos
        # self.c = 0

        sprite = cocos.sprite.Sprite('Resources/Paddle.png')
        # sprite.position = self.x_pos,self.y_pos

        # # create a ScaleBy action that lasts 2 seconds
        # scale = ScaleBy(3, duration=2)
        #
        # # tell the label to scale and scale back and repeat these 2 actions forever
        # label.do(Repeat(scale + Reverse(scale)))

class Ball(cocos.sprite.Sprite):

    def __init__(self,img='Resources/Ball.png'):
        super(Ball, self).__init__(img)

        # Direction the ball is traveling. 0 = right, Pi/2 = up, Pi = left, etc
        self.dir = math.pi/5
        self.vel = 4
        self.x_pos = 300
        self.y_pos = 300

    def set_dir(self,dir):

        # Randomize direction just slightly
        fudge = 2*math.pi * 0.05 * random.random()
        fudge -= 2*math.pi * 0.025

        self.dir = dir + fudge
        if self.dir < 0:
            self.dir = (2*math.pi) - abs(self.dir)
        elif self.dir > (2*math.pi):
            self.dir -= 2*math.pi

    def reset(self):
        # Start ball off in a random direction, heading to the right, within 45 degrees of 0

        if random.random() > 0.5:
            self.set_dir(random.random() * math.pi/8 + math.pi/4)
        else:
            self.set_dir((random.random() * math.pi/8 + math.pi/4) * -1)

        # Start ball in random position, roughly near the center of screen

        dx = director.get_window_size()[0]/6 * random.random() - director.get_window_size()[0]/12
        dy = director.get_window_size()[1]/6 * random.random() - director.get_window_size()[1]/12
        self.x_pos = director.get_window_size()[0]/2 + dx
        self.y_pos = director.get_window_size()[1]/2 + dy
        self.position = self.x_pos,self.y_pos


    def bounce(self,side):
        print("BOUNCE:",side)
        if side == "TOP" or side == "BOTTOM":
            self.set_dir(self.dir * -1)
        elif side == "RIGHT" or "PADDlE":
            if self.dir < math.pi:
                self.set_dir(math.pi - self.dir)
            else:
                self.set_dir(3*math.pi - self.dir)

class IntroText(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self):
        super(IntroText, self).__init__()
        self.text = cocos.text.Label("x", x=director.get_window_size()[0]/3,
                                     y=director.get_window_size()[1]/2)

        self.text.element.text = "Welcome to pong, click to begin"
        self.add(self.text)

    def on_mouse_press(self, x, y, buttons, modifiers):

        director.replace(main_scene)




class WorldView(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super(WorldView,self).__init__()

        self.c = 0
        self.keys = [0,0]   # W/S

        self.user = UserPaddle()
        self.ball = Ball()

        self.labels = Scores()
        self.labels.update_text()

        #Schedule function to be called every frame of game
        self.schedule(self.update)

        # Add paddle to screen
        self.add(self.user)
        self.add(self.ball)
        self.add(self.labels)
        self.ball.reset()



    # Event handler for pressing a key
    # Sets a value in the key[] variable to 1 (i.e., set state)
    def on_key_press(self, ikey, modifiers):
        key = pyglet.window.key.symbol_string(ikey) # Get ASCII val
        if key == 'W' or key == 'UP':          # Go up
            self.keys[0] = 1
        elif key == 'S' or key == 'DOWN':      # Go down
            self.keys[1] = 1;

        print(self.keys)

    # Event handler for releasing a key
    # Sets a value in key[] variable to 0 (i.e., clear state)
    def on_key_release(self, ikey, modifiers):
        key = pyglet.window.key.symbol_string(ikey)
        if key == 'W' or key == 'UP':
            self.keys[0] = 0
        elif key == 'S' or key == 'DOWN':
            self.keys[1] = 0;

    # Function that is run every frame of the game. Handles movement, collision detection, and most
    # motion of any kind.
    def update(self, dt):       # dt is time elapsed
        self.c += 1
        win_x = director.get_window_size()[0]
        win_y = director.get_window_size()[1]
        if self.keys[0] == 1:       # User wants to go up
            self.user.y_pos += self.user.speed
            self.user.position = self.user.x_pos,self.user.y_pos
            print(self.user.position)
        elif self.keys[1] == 1:     # User wants to go down
            self.user.y_pos -= self.user.speed
            self.user.position = self.user.x_pos,self.user.y_pos
            print(self.user.position)

        # Update ball position
        self.ball.x_pos += self.ball.vel * math.cos(self.ball.dir)
        self.ball.y_pos += self.ball.vel * math.sin(self.ball.dir)
        self.ball.position = self.ball.x_pos,self.ball.y_pos

        # Detect bounce
        # Origin of ball is bottom left corner
        if self.ball.y_pos > win_y-self.ball.height/2:
            self.ball.bounce("TOP")
        elif self.ball.y_pos < 0+self.ball.height/2:
            self.ball.bounce("BOTTOM")
        elif self.ball.x_pos > win_x-self.ball.width/2:
            self.ball.bounce("RIGHT")
        elif self.ball.x_pos < self.user.width + self.ball.width/2:
            #self.ball.x_pos += 5
            if self.ball.y_pos > (self.user.y_pos - self.user.height/2) and self.ball.y_pos < (self.user.y_pos + self.user.height/2):
                self.ball.bounce("PADDLE")
                self.labels.hits += 1
                self.labels.update_text()
            elif self.ball.x_pos < 0:
                self.ball.x_pos = win_x/2
                self.ball.y_pos = win_y/2
                self.ball.position = win_x/2,win_y/2
                self.ball.reset()
                self.labels.misses += 1
                self.labels.update_text()

            if self.labels.hits >= self.labels.hits_goal:
                director.replace(intro_scene)


if __name__ == "__main__":
    director.init(resizable=True)
    # Run a scene with our event displayers:
    intro_scene = cocos.scene.Scene()
    main_scene = cocos.scene.Scene()



    intro_scene.add(IntroText())
    main_scene.add(WorldView())

    director.run(intro_scene)
    #director.run(cocos.scene.Scene(IntroScene()))
