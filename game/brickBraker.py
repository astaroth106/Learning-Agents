import numpy as np
import sys
import random
import pygame
import pygame.surfarray as surfarray
from pygame.locals import *
from itertools import cycle

SCREEN_SIZE = 640, 480


#object dimensions
BRICK_WIDTH = 60
BRICK_HEIGHT = 15
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 12
BALL_DIAMETER = 16
BALL_RADIUS = BALL_DIAMETER / 2

MAX_PADDLE_X = SCREEN_SIZE[0] - PADDLE_WIDTH
MAX_BALL_X = SCREEN_SIZE[0] - BALL_DIAMETER
MAX_BALL_Y = SCREEN_SIZE[1] - BALL_DIAMETER

# paddle y coordinate
PADDLE_Y = SCREEN_SIZE[1] - PADDLE_HEIGHT - 10 

#color constants
BLACK = (0 ,0 , 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BRICK_COLOR = (0, 255, 0) #GREEN

#state constants
STATE_BALL_IN_PADDLE = 0
STATE_PLAYING = 1
STATE_WON = 2
STATE_GAME_OVER = 3

#learning variables
isTerminal = False
reward = 0

class GameState:
	
	def __init__(self):
		pygame.init()
		
		self.screen = pygame.display.set_mode(SCREEN_SIZE)
		pygame.display.set_caption("brickBreaker")
		
		self.clock = pygame.time.Clock()
		
		if pygame.font:
			self.font = pygame.font.Font(None, 30)
		else:
			self.font = None
		
		#change the variable to load a specific level first
		#variable (level, score, lives)	
		self.init_game(0, 0, 1)


	def init_game(self, thelevel, thescore, thelives):
		self.level = thelevel
		self.lives = thelives
		self.score = thescore
		self.state = STATE_BALL_IN_PADDLE
	
		self.paddle = pygame.Rect(300, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT)
		self.ball = pygame.Rect(300, PADDLE_Y - BALL_DIAMETER, BALL_DIAMETER, BALL_DIAMETER)
	
		self.ball_vel = [50, -50]
	
		if self.level == 0:
			self.create_bricks()

	def  create_bricks(self):
		y_ofs = 35
		self.bricks = []
		for i in range (7):
			x_ofs = 35
			for j in range(8):
				self.bricks.append(pygame.Rect(x_ofs, y_ofs, BRICK_WIDTH, BRICK_HEIGHT))
				x_ofs += BRICK_WIDTH + 10
			y_ofs += BRICK_HEIGHT + 5

	def draw_bricks(self):
		for brick in self.bricks:
			pygame.draw.rect(self.screen, BRICK_COLOR, brick)
	
	def move_ball (self):
		self.ball.left += self.ball_vel[0]
		self.ball.top += self.ball_vel[1]
	
		if self.ball.left <= 0:
			self.ball.left = 0
			self.ball_vel[0] = -self.ball_vel[0]
		elif self.ball.left >= MAX_BALL_X:
			self.ball.left = MAX_BALL_X
			self.ball_vel[0] = -self.ball_vel[0]
		
		if self.ball.top < 0:
			self.ball.top = 0
			self.ball_vel[1] = -self.ball_vel[1]

	def handle_collisions(self):
		reward = 0
		Terminal = True
		for brick in self.bricks:
			if self.ball.colliderect (brick):
				self.score += 3
				reward = 3
				self.ball_vel[1] = -self.ball_vel[1]
				self.bricks.remove(brick)
				break
		
		if len(self.bricks) == 0:
			self.state = STATE_BALL_IN_PADDLE
			Terminal = True
			reward = 5
			
		if self.ball.colliderect (self.paddle):
			self.ball.top = PADDLE_Y - BALL_DIAMETER
			self.ball_vel[1] = -self.ball_vel[1]
			reward = 1
			
		#if the ball hits the ground
		elif self.ball.top > self.paddle.top:
			self.lives -= 1
			if self.lives > 0:
				self.state = STATE_PLAYING
			else:
				self.state = STATE_BALL_IN_PADDLE
				Terminal = True
				reward = -3
		return reward, Terminal
	
	def frame_step(self, input_actions):
		pygame.event.pump()		
		
		reward = 0.1
		terminal = False
		
		if sum(input_actions) != 1:
		    raise ValueError('Multiple input actions!')
		

		if self.state == STATE_PLAYING:
			if input_actions[0]:
				self.paddle.left -= 10
				if self.paddle.left < 0:
					self.paddle.left = 0		
			if input_actions[1]:
				self.paddle.left += 10
				if self.paddle.left > MAX_PADDLE_X:
					self.paddle.left = MAX_PADDLE_X
			self.move_ball()
			reward, terminal = self.handle_collisions()
		elif self.state == STATE_BALL_IN_PADDLE:
			self.ball.left = self.paddle.left + self.paddle.width / 2
			self.ball.top = self.paddle.top - self.ball.height
			self.state = STATE_PLAYING
			self.ball_vel = [50, -50]
	
		self.screen.fill(BLACK)

		#draw paddle
		pygame.draw.rect(self.screen, BLUE, self.paddle)
		
		#draw ball
		pygame.draw.circle(self.screen, WHITE, (self.ball.left + BALL_RADIUS, self.ball.top + BALL_RADIUS), BALL_RADIUS)	

		self.draw_bricks()
		
		if terminal:
			self.__init__(0, 0, 1)	
	
		image_data = pygame.surfarray.array3d(pygame.display.get_surface())
	
		pygame.display.update()
		self.clock.tick(30)
	
		return image_data, reward, terminal

