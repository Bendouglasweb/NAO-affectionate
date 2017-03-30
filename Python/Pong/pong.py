from __future__ import division, print_function, unicode_literals
import math
import random
import pprint
import time, threading
import zmq
import sys

import cocos
from cocos.director import director

import pyglet


class Scores(cocos.layer.Layer):
    def __init__(self):
        super(Scores, self).__init__()

        win_x = director.get_window_size()[0]
        win_y = director.get_window_size()[1]
        self.hits_pos = [0.1 * win_x, win_y-20]
        self.miss_pos = [0.4 * win_x, win_y-20]
        self.time_pos = [0.7 * win_x, win_y-20]

        self.hits = 0
        self.misses = 0
        self.hits_goal = 1
        self.misses_goal = 15
        self.time = 0
        self.start_time = 0
        self.end_time = 0

        # Create hits label 10% from left border
        self.hits_label = cocos.text.Label("", x=self.hits_pos[0], y=self.hits_pos[1])

        # Create misses label 40% from left border
        self.miss_label = cocos.text.Label("", x=self.miss_pos[0], y=self.miss_pos[1])

        # Create misses label 70% from left border
        self.time_label = cocos.text.Label("", x=self.time_pos[0], y=self.time_pos[1])

        self.add(self.hits_label)
        self.add(self.miss_label)
        self.add(self.time_label)

    def update_text(self):
        self.hits_label.element.text = "Hits: " + str(self.hits) + " / " + str(self.hits_goal)
        self.miss_label.element.text = "Misses: " + str(self.misses) + " / " + str(
                self.misses_goal)


class UserPaddle(cocos.sprite.Sprite):

    def __init__(self, img='Resources/Paddle.png'):
        super(UserPaddle, self).__init__(img)
        self.x_pos = self.width/2
        self.y_pos = 120
        self.speed = 5
        self.position = self.x_pos, self.y_pos
        self.control = [0,0]
        # self.c = 0

        sprite = cocos.sprite.Sprite("Resources/Paddle.png")
        # sprite.position = self.x_pos,self.y_pos

        # # create a ScaleBy action that lasts 2 seconds
        # scale = ScaleBy(3, duration=2)
        #
        # # tell the label to scale and scale back and repeat these 2 actions forever
        # label.do(Repeat(scale + Reverse(scale)))

    def move(self, dir):
        win_y = director.get_window_size()[1]
        if dir == "UP":
            if self.y_pos + self.speed + self.height/2 < win_y:
                self.y_pos += self.speed
        if dir == "DOWN":
            if self.y_pos - self.speed - self.height/2 >= 0:
                self.y_pos -= self.speed

        self.position = self.x_pos, self.y_pos



class Ball(cocos.sprite.Sprite):

    def __init__(self,img='Resources/Ball.png'):
        super(Ball, self).__init__(img)

        # Direction the ball is traveling. 0 = right, Pi/2 = up, Pi = left, etc
        self.dir = math.pi/5
        self.vel = 8
        self.x_pos = 300
        self.y_pos = 300


    def set_dir(self, dir):

        # Randomize direction just slightly
        fudge = 2*math.pi * 0.05 * random.random()
        fudge -= 2*math.pi * 0.025

        self.dir = math.pi/2

        self.dir = dir + fudge


        if self.dir < 0:
            self.dir = (2*math.pi) - abs(self.dir)
        elif self.dir > (2*math.pi):
            self.dir -= 2*math.pi

        # Check if direction close to straight up
        if abs(self.dir - math.pi/2) < (math.pi * 0.2):
            print("Close to up")
            if self.dir > math.pi/2:
                self.dir += math.pi * 0.05 + math.pi * 0.05 * random.random()
            elif self.dir < math.pi/2:
                self.dir -= math.pi * 0.05 + math.pi * 0.05 * random.random()
        elif abs(self.dir - math.pi*(3/2)) < (math.pi * 0.2):
            print("Close to down")
            if self.dir > math.pi*(3/2):
                self.dir += math.pi * 0.05 + math.pi * 0.05 * random.random()
            elif self.dir < math.pi*(3/2):
                self.dir -= math.pi * 0.05 + math.pi * 0.05 * random.random()

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

    def bounce(self, side):
        print("BOUNCE:",side)
        if side == "TOP" or side == "BOTTOM":
            self.set_dir(self.dir * -1)
            if side == "TOP":
                self.y_pos -= 5
            elif side == "BOTTOM":
                self.y_pos += 5
        elif side == "RIGHT" or "PADDlE":
            if self.dir < math.pi:
                self.set_dir(math.pi - self.dir)
            else:
                self.set_dir(3*math.pi - self.dir)
            if side == "RIGHT":
                self.x_pos -= 5
            elif side == "PADDLE":
                self.x_pos += 10

    def move(self):
        self.x_pos += self.vel * math.cos(self.dir)
        self.y_pos += self.vel * math.sin(self.dir)
        self.position = self.x_pos, self.y_pos


class IntroText(cocos.layer.Layer):
    global var
    is_event_handler = True

    def __init__(self):
        super(IntroText, self).__init__()
        self.text = cocos.text.Label("x", x=director.get_window_size()[0]/3,
                                     y=director.get_window_size()[1]/2)

        self.text.element.text = "Welcome to pong!"
        self.add(self.text)

        print("Intro init!")

    def on_mouse_press(self, x, y, buttons, modifiers):

        director.replace(main_scene)
        print("got it")

    # def on_enter(self):
    #     print("Intrrooo init!")


class OverText(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super(OverText, self).__init__(0,0,0,240)
        wx = director.get_window_size()[0]
        wy = director.get_window_size()[0]
        self.text1 = cocos.text.Label("", x=wx*0.1,
                                     y=wy*0.65,
                                     font_name="Calibri",
                                     font_size=18)

        self.text2 = cocos.text.Label("", x=wx*0.1,
                                     y=wy*0.6,
                                     font_name="Calibri",
                                     font_size=18)

        self.text3 = cocos.text.Label("", x=wx*0.1,
                                     y=wy*0.55,
                                     font_name="Calibri",
                                     font_size=18)

        self.text4 = cocos.text.Label("", x=wx*0.1,
                                     y=wy*0.5,
                                     font_name="Calibri",
                                     font_size=18)

        self.next_button = cocos.layer.ColorLayer(100, 0, 0, 255)
        self.next_button.width = int(wx * 0.25)
        self.next_button.height = int(wy * 0.08)
        self.next_button.position = int(wx/2 - self.next_button.width/2), int(wy*0.1)

        self.next_text = cocos.text.Label()
        self.next_text.element.font_name = "Calibri"
        self.next_text.element.font_size = 18
        self.next_text.position = int(wx/2 - self.next_button.width/6), int(wy*0.125)
        self.next_text.element.text = "Next"

        self.add(self.text1)
        self.add(self.text2)
        self.add(self.text3)
        self.add(self.text4)
        self.add(self.next_button)
        self.add(self.next_text)

    def update_text(self, round_num, hits, misses, time):
        self.text1.element.text = "Round " + str(round_num)
        self.text2.element.text = "Your goal is " + str(hits) + " hits."
        self.text3.element.text = "You can make " + str(misses) + " misses."
        self.text4.element.text = "You have " + str(time) + " seconds in this round."

    def set_text(self, line_1, line_2, line_3, line_4):
        self.text1.element.text = line_1
        self.text2.element.text = line_2
        self.text3.element.text = line_3
        self.text4.element.text = line_4

    def button_timer(self, t):
        self.button_visible(False)
        threading.Timer(t, self.button_visible(True)).start()

    def button_visible(self, setting):
        if setting:
            self.next_button.visible = True
            self.next_text.visible = True
        elif not setting:
            self.next_button.visible = False
            self.next_text.visible = False


class WorldView(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super(WorldView, self).__init__()

        self.c = 0           # Iteration count
        self.cp = 0             # Control period. Number of iterations left for current decision on
                                # "messing up"
        self.con = 0            # Messes up controls this time? 0 = no, 1 = yes
        self.con_op = 0
        self.keys = [0, 0]   # W/S
        self.on_round = 0
        self.options = []
        self.freeze = 1      # 1 = pause game; 0 = play

        self.state = 0
        # 0:    Program just started
        # 1:    Displaying introduction text
        # 2:    Demo 1 introduction text
        # 3:    Playing demo 1
        # 4:    Demo 2 introduction text
        # 5:    Playing demo 2
        # 6:    In between demos and game
        # 7:    In pre-round instructions
        # 8:    Playing current round
        # 9:    Game finished, post instructions
        # 10:   In questions

        self.user = UserPaddle()
        self.ball = Ball()

        # Instructions text
        self.instructions = OverText()
        self.instructions.visible = False

        self.add(self.instructions, z=10)

        self.labels = Scores()
        self.labels.update_text()

        # Schedule function to be called every frame of game
        self.schedule(self.update)

        # Add paddle to screen
        self.add(self.user)
        self.add(self.ball)
        self.add(self.labels)
        self.ball.reset()

        self.read_settings()

        self.progress()

    # Event handler for pressing a key
    # Sets a value in the key[] variable to 1 (i.e., set state)
    def on_key_press(self, ikey, modifiers):
        key = pyglet.window.key.symbol_string(ikey) # Get ASCII val
        if key == 'W' or key == 'UP':          # Go up
            self.keys[0] = 1
        elif key == 'S' or key == 'DOWN':      # Go down
            self.keys[1] = 1

        print(self.keys)

    # Event handler for releasing a key
    # Sets a value in key[] variable to 0 (i.e., clear state)
    def on_key_release(self, ikey, modifiers):
        key = pyglet.window.key.symbol_string(ikey)
        if key == 'W' or key == 'UP':
            self.keys[0] = 0
        elif key == 'S' or key == 'DOWN':
            self.keys[1] = 0

    # Function that is run every frame of the game. Handles movement, collision detection, and most
    # motion of any kind.
    def update(self, dt):       # dt is time elapsed
        if self.freeze == 1:
            return
        self.c += 1


        if self.cp <= 0:
            if self.user.control[0] == 1:
                self.cp = int(random.random() * 100) + 25
                self.con = 1 if random.random() > 0.5 else 0
            elif self.user.control[1] == 1:
                self.cp = int(random.random() * 15) + 15
                self.con = 1 if random.random() < 0.3 else 0
                self.con_op = 1 if random.random() > 0.5 else 0
        self.cp -= 1

        self.labels.time_label.element.text = "Time: " + str(int(self.labels.end_time -
                                                                time.time())) + "s"

        # Get user input, glitch if desired.
        win_x = director.get_window_size()[0]
        win_y = director.get_window_size()[1]
        if self.keys[0] == 1:       # User wants to go up
            # Controls will randomly inverse
            if self.user.control[0] == 1 and self.con == 1:
                self.user.move("DOWN")
            else:
                self.user.move("UP")
        elif self.keys[1] == 1:     # User wants to go down
            # Controls will randomly inverse
            if self.user.control[0] == 1 and self.con == 1:
                self.user.move("UP")
            else:
                self.user.move("DOWN")

        if self.user.control[1] == 1:
            if self.con == 1:
                if self.con_op == 1:
                    self.user.move("UP")
                else:
                    self.user.move("DOWN")

        # Update ball position
        self.ball.move()

        # Detect bounce
        # Origin of ball is bottom left corner
        if self.ball.y_pos > win_y-self.ball.height/2:
            self.ball.bounce("TOP")
        elif self.ball.y_pos < 0+self.ball.height/2:
            self.ball.bounce("BOTTOM")
        elif self.ball.x_pos > win_x-self.ball.width/2:
            self.ball.bounce("RIGHT")
        elif self.ball.x_pos < self.user.width + self.ball.width/2:
            if self.ball.y_pos > (self.user.y_pos - self.user.height/2) and self.ball.y_pos < (self.user.y_pos + self.user.height/2):
                self.ball.bounce("PADDLE")
                self.labels.hits += 1
                self.labels.update_text()
            elif self.ball.x_pos < 0:
                self.ball.reset()
                self.labels.misses += 1
                self.labels.update_text()

            if self.labels.hits >= self.labels.hits_goal or self.labels.misses >= \
                    self.labels.misses_goal:
                self.progress()

    def read_settings(self):
        input_file = open("options.txt", "r")
        for line in input_file:
            if '*' not in line and ',' in line:
                t_vals = line.split(",")
                vals = []
                for i in t_vals:
                    vals.append(int(i))
                self.options.append(vals)

    def parse_settings(self):
        vals = self.options[self.on_round-1]
        print(self.options)
        self.user.speed = vals[1]
        self.ball.vel = vals[3]
        self.user.control = [vals[4], vals[5]]
        self.labels.time = vals[6]
        self.labels.hits_goal = vals[7]
        self.labels.misses_goal = vals[8]


    def unfreeze(self):
        self.instructions.visible = False
        self.freeze = 0
        self.labels.start_time = int(time.time())
        self.labels.end_time = self.labels.time + self.labels.start_time + 2
        if skip_zmq == 0:
            msg = str(self.on_round) + ",0," + str(self.labels.hits) + "," + str(self.labels.misses)
            msg += ",-1"    # unknown
            try:
                socket.send_string(msg)
            except:
                print("Error in communicating to Grapher script")
                print(sys.exc_info()[0])

            try:
                socket.recv()
            except:
                print("Error in communicating to Grapher script")
                print(sys.exc_info()[0])


    def progress(self):
        out_file.write("round_" + str(self.on_round) + ":")
        out_file.write(str(self.labels.hits) + "," + str(self.labels.misses) + "\n")

        self.on_round += 1

        # Data format:
        #   [0] = Round number
        #   [1] = On instruction? 0 = no, 1 = yes
        #   [2] = Hits
        #   [3] = Misses
        #   [4] = Glitches
        if skip_zmq == 0:
            msg = str(self.on_round) + ",1,"
            msg += str(self.labels.hits) + ","
            msg += str(self.labels.misses) + ","
            # This variable will be the data for the round we just ended because we haven't
            # changed the values with .parse_settings() yet
            msg += "1" if self.user.control[0] == 1 or self.user.control[1] == 1 else "0"
            try:
                socket.send_string(msg)
            except:
                print("Error in communicating to Grapher script")
                print(sys.exc_info()[0])

            try:
                socket.recv()
            except:
                print("Error in communicating to Grapher script")
                print(sys.exc_info()[0])

        if self.on_round > len(self.options):
            director.replace(questions_scene)
        else:
            self.instructions.visible = True
            self.freeze = 1
            self.labels.hits = 0
            self.labels.misses = 0
            self.ball.reset()

            self.parse_settings()
            self.instructions.update_text(self.on_round,1,2,30)
            self.instructions.update_text(self.on_round,self.labels.hits_goal,
                                          self.labels.misses_goal,self.labels.time)
            self.labels.update_text()
            threading.Timer(6,self.unfreeze).start()


class Questions(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(Questions, self).__init__()

        wx = director.get_window_size()[0]  # Window width
        wy = director.get_window_size()[1]  # Window height

        self.on_question = -1
        self.question_answers = []
        self.selection = 0

        # Add background boxes and numbers to screen for selection
        self.boxes = []
        self.numbers = []
        self.lines = []
        for i in range(11):
            self.boxes.append(cocos.layer.ColorLayer(100, 0, 0, 255))
            self.boxes[i].width = int(wx * 0.09)
            self.boxes[i].height = int(wy * 0.06)
            self.boxes[i].position = int(wx * (0.10*i + 0.005)), int(wy*0.2)
            self.add(self.boxes[i])

            self.numbers.append(cocos.text.Label())
            self.numbers[i].element.text = str(i+1)
            self.numbers[i].element.font_name = "Calibri"
            self.numbers[i].element.font_size = 18
            if i == 9:
                self.numbers[i].position = int(wx * (0.10*i + 0.03)), int(wy*0.215)
            elif i == 10:
                self.boxes[i].width = int(wx * 0.25)
                self.boxes[i].height = int(wy * 0.08)
                self.boxes[i].position = int(wx/2 - self.boxes[i].width/2), int(wy*0.1)
                self.numbers[i].position = int(wx/2 - self.boxes[i].width/6), int(wy*0.125)
                self.numbers[i].element.text = "Next"
            else:
                self.numbers[i].position = int(wx * (0.10*i + 0.042)), int(wy*0.215)
            self.add(self.numbers[i])

        for i in range(6):
            self.lines.append(cocos.text.Label())
            self.lines[i].element.text = str(i+1)
            self.lines[i].element.font_name = "Calibri"
            self.lines[i].element.font_size = 12
            self.lines[i].position = int(wx * 0.05),int(wy * (0.9 - i*0.05))
            self.add(self.lines[i])

        # Read in and parse question data

        input_file = open("questions.txt","r")
        cur_question = -1
        self.questions = []
        for line in input_file:
            if line[0] == "*" or line[0] == "\n":
                continue
            elif line[0] == "-":
                cur_question += 1
                self.questions.append({"lines": [], 'left_op': '', 'right_op': ''})
            elif "=" in line:
                op = line.split("=")
                if "line" in op[0]:
                    self.questions[cur_question]['lines'].append(str(op[1]).strip())
                elif "left_option" in op[0]:
                    self.questions[cur_question]['left_op'] = op[1].strip()
                elif "right_option" in op[0]:
                    self.questions[cur_question]['right_op'] = op[1].strip()

        self.next_question()



    def on_mouse_press(self, mouse_x, mouse_y, buttons, modifiers):
        for i in range(11):
            if mouse_x > self.boxes[i].x and mouse_x < self.boxes[i].x + self.boxes[i].width:
                if mouse_y > self.boxes[i].y and mouse_y < self.boxes[i].y + self.boxes[i].height:

                    for j in range(10):
                        self.boxes[j].color = 100, 0, 0

                    if i == 10:
                        self.boxes[i].color = 100, 0, 0
                        self.question_answers.append(self.selection+1)
                        self.next_question()
                    else:
                        self.boxes[i].color = 255, 0, 0
                        self.selection = i

    def next_question(self):
        self.on_question += 1

        # Clear any previous text
        for i in range(6):
            self.lines[i].element.text = ""

        if self.on_question >= len(self.questions):
            self.lines[5].element.text = "Thanks for participating!"
            self.set_visible(1)
            for i in range(len(self.question_answers)):
                out_file.write("Question " + str(i) + ": " + str(self.question_answers[i]) + "\n")
        else:
            for i in range(len(self.questions[self.on_question]['lines'])):
                self.lines[i].element.text = self.questions[self.on_question]['lines'][i]

    def set_visible(self, op):
        if op == 0:         # Set all invisible
            for i in range(11):
                self.boxes[i].visible = False
                self.numbers[i].visible = False
            for i in range(6):
                self.lines[i].visible = False
        elif op == 1:       # Set buttons invisible, text lines visible
            for i in range(11):
                self.boxes[i].visible = False
                self.numbers[i].visible = False
            for i in range(6):
                self.lines[i].visible = True
        elif op == 2:       # Set all visible
            for i in range(11):
                self.boxes[i].visible = True
                self.numbers[i].visible = True
            for i in range(6):
                self.lines[i].visible = True


if __name__ == "__main__":

    skip_zmq = 1    # 0 = Talk to Graphing script, 1 = Skip zmq com

    out_file = open("pong_output_file.txt","w")

    if skip_zmq == 0:
        context = zmq.Context()
        # Connect to Graphing script
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:5679")
        # socket = context.socket(zmq.PUB)
        # socket.bind("tcp://*:5556")

        socket.RCVTIMEO = 3000


    director.init(resizable=True)
    # Run a scene with our event displayers:
    main_scene = cocos.scene.Scene()
    questions_scene = cocos.scene.Scene()

    main_scene.add(WorldView())
    questions_scene.add(Questions())

    director.run(main_scene)
    #director.run(cocos.scene.Scene(IntroScene()))
