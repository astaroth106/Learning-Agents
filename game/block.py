import numpy as np
import sys
import random
import pygame
import pygame.surfarray as surfarray
from pygame.locals import *
from itertools import cycle

FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
BASEY = SCREENHEIGHT * 0.79

PLAYER_WIDTH, PLAYER_HEIGHT = 20, 20

pygame.init()
FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Jumping Jack')

isCrash = False
PLAYER_INDEX_GEN = cycle([0, 1, 2, 1])

class GameState:
    def __init__(self):
        self.score = self.playerIndex = self.loopIter = 0
        self.playerx = int((SCREENWIDTH - PLAYER_WIDTH) /2 )
        self.playery = int((SCREENHEIGHT - PLAYER_HEIGHT) / 2)
	self.basex = 0
	self.baseShift = 1
        self.rectangle = pygame.Rect(self.playerx, self.playery, PLAYER_WIDTH, PLAYER_HEIGHT)

        # player velocity, max velocity, downward accleration, accleration on flap
        self.pipeVelX = -4
        self.playerVelY    =  0    # player's velocity along Y, default same as playerJumped
        self.playerMaxVelY =  10   # max vel along Y, max descend speed
        self.playerMinVelY =  -8   # min vel along Y, max ascend speed
        self.playerAccY    =   1   # players downward accleration
        self.playerFlapAcc =  -9   # players speed on flapping
        self.playerJumped = False # True when player flaps

    def frame_step(self, input_actions):
        pygame.event.pump()

        reward = 0.1
        terminal = False

        if sum(input_actions) != 1:
            raise ValueError('Multiple input actions!')

        # input_actions[0] == 1: do nothing
        # input_actions[1] == 1: flap the bird
        if input_actions[1] == 1:
            if self.playery > -2 * PLAYER_HEIGHT:
                self.playerVelY = self.playerFlapAcc
                self.playerJumped = True

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerJumped:
            self.playerVelY += self.playerAccY
        if self.playerJumped:
            self.playerJumped = False
        self.playery += min(self.playerVelY, SCREENHEIGHT - self.playery - PLAYER_HEIGHT)
        if self.playery < 0:
            self.playery = 0
	
	if self.playery + PLAYER_HEIGHT >= SCREENHEIGHT - 100:
		reward = 1
	elif self.playery - PLAYER_HEIGHT <= 100:
		reward = 1	

        # check if crash here
        if self.playery + PLAYER_HEIGHT >= SCREENHEIGHT:
		print "you lost down"
		isCrash = True
	elif self.playery - PLAYER_HEIGHT <= 0:
		print "you lost up"
		isCrash = True
	else:
		isCrash = False

        if isCrash:
            terminal = True
            self.__init__()
            reward = -1

        # draw sprites
        SCREEN.fill((0,0,0))

	self.rectangle = pygame.Rect(self.playerx, self.playery, PLAYER_WIDTH, PLAYER_HEIGHT)
	pygame.draw.rect(SCREEN, (255,255,255), self.rectangle)        

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        return image_data, reward, terminal
	
