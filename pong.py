#!/usr/bin/env python3
# ----------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016, Heiko Möllerke
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ----------------------------------------------------------------------
import collections
import math
import random
import pyglet
from pyglet.window import key


# ----------------------------------------------------------------------
# Essential math
# ----------------------------------------------------------------------

class Vector(collections.namedtuple('Vector', 'x y')):
    """A simple two-dimensional vector."""
    
    def __new__(cls, x, y):
        return tuple.__new__(cls, [x, y])

    
    @property
    def magnitude(self):
        """Returns the vector's magnitude."""
        return math.sqrt(self.x ** 2 + self.y ** 2)
       
        
    def normalized(self):
        """Returns a normalized vector."""
        return self / self.magnitude
        
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Arithmetic operations
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def __add__(self, other):
        x, y = other
        return type(self)(self.x + x, self.y + y)
        
    
    def __sub__(self, other):
        x, y = other
        return type(self)(self.x - x, self.y - y)

        
    def __mul__(self, scalar):
        return type(self)(self.x * scalar, self.y * scalar)
        
        
    def __truediv__(self, scalar):
        return type(self)(self.x / scalar, self.y / scalar)


# ----------------------------------------------------------------------
# Other things
# ----------------------------------------------------------------------

class GameContext(pyglet.window.Window):
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.running = False
        self.score = None
        self.ball = None
        self.paddles = []
        self.label_score = None
        self.reset()
        self.set_score_label()
        pyglet.clock.schedule_interval(self.update, 1 / 120)
        
        
    def update(self, delta_time):
        if self.running:
           self.move_paddles(delta_time)
           self.move_ball(delta_time)
        
     
    def move_paddles(self, delta_time):
        for paddle in self.paddles:
            paddle.y += paddle.direction_y * paddle.speed * delta_time
            if paddle.y < 0:
                paddle.y = 0
            elif paddle.y > (400 - paddle.height):
                paddle.y = 400 - paddle.height
        
        
    def move_ball(self, delta_time):
        x = self.ball.x + self.ball.speed * self.ball.direction_x * delta_time
        y = self.ball.y + self.ball.speed * self.ball.direction_y * delta_time

        # Check collison with upper bounds
        if y < 0:
            y = 0
            self.ball.direction_y = -self.ball.direction_y
        elif y > 400 - self.ball.height:
            self.y = 400 - self.ball.height
            self.ball.direction_y = -self.ball.direction_y
       
        # Check collision with paddles
        if x <= 18 or x >= 614:
            for paddle in self.paddles:
                if y > paddle.y and y < paddle.y + paddle.height:
                    paddle_center = paddle.y - paddle.height / 2
                    self.ball.direction_x = -self.ball.direction_x
                    self.ball.direction_y += 0.005 * (paddle_center - y)
        

        
        # Check if ball left horizontal bounds
        if x < 0:
            self.ball = Ball((640 // 2, 400 // 2))
            self.score = self.score[0], self.score[1] + 1
            self.set_score_label()
            self.toggle_pause()
            return
        elif x > 640 - 8:
            self.ball = Ball((640 // 2, 400 // 2))
            self.score = self.score[0] + 1, self.score[1]
            self.set_score_label()
            self.toggle_pause()
            return

        # Finally update ball's position
        self.ball.position = x, y

        
    def on_draw(self):  # overrides
        self.clear()
        self.board.draw()
        for paddle in self.paddles:
            paddle.draw()
        self.ball.draw()
        self.label_score.draw()

        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.paddles[0].up()
        elif symbol == key.S:
            self.paddles[0].down()
        elif symbol == key.UP:
            self.paddles[1].up()
        elif symbol == key.DOWN:
            self.paddles[1].down()
        
    
    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self.paddles[0].halt()
        elif symbol == key.S:
            self.paddles[0].halt()
        elif symbol == key.UP:
            self.paddles[1].halt()
        elif symbol == key.DOWN:
            self.paddles[1].halt()
        elif symbol == key.SPACE:
            self.toggle_pause()
        elif symbol == key.ESCAPE:
            self.reset()

            
    def reset(self):
        self.score = 0, 0
        self.ball = Ball((640 // 2, 400 // 2))
        self.paddles = [Paddle((10, 120)), Paddle((622, 120))]
        self.running = False
        self.set_score_label()
        

    def toggle_pause(self):
        self.running = not self.running

  
    def set_score_label(self):
        a, b = self.score
        self.label_score = pyglet.text.Label('{} : {}'.format(a, b),
                                             x=640 / 2, y = 405,
                                             anchor_x='center')
                                        

class Board(pyglet.sprite.Sprite):
    def __init__(self, position=(0, 0)):
        super().__init__(pyglet.resource.image('board_640x400.png'))
        self.position = position

        
  
class Paddle(pyglet.sprite.Sprite):
    def __init__(self, position):
        super().__init__(pyglet.resource.image('paddle_8x40.png'))
        self.position = position
        self.direction_y = 0
        self.speed = 400 / 2  # Pixel per second
      
      
    def up(self):
        self.direction_y = 1
        
        
    def down(self):
        self.direction_y = -1
        
        
    def halt(self):
        self.direction_y = 0
      

      
class Ball(pyglet.sprite.Sprite):
    def __init__(self, position):
        super().__init__(pyglet.resource.image('ball_8x8.png'))
        self.position = position
        self.direction_x = (-0.5 + random.random()) * 2
        self.direction_y = -0.5 + random.random()
        self.speed = 500 / 2  # Pixel per second

        

def main():
    window = GameContext()
    pyglet.app.run()


if __name__ == '__main__':
    main()
