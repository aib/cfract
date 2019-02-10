import colorsys
import math
import random
import time

import dotdict
import numpy as np
import pygame

TAU = 2. * math.pi

SIZE = (600, 600)
DOTS = 128
RADIUS = 250

CENTER = np.array([SIZE[0] / 2, SIZE[1] / 2])

def mag(v):
	return math.sqrt(v[0]**2 + v[1]**2)

def norm(v):
	return v / mag(v)

class Dot:
	def __init__(self, fract):
		self.path = []

		theta = random.random() * TAU
		self.pos = np.array([CENTER[0] + RADIUS * math.cos(theta), CENTER[1] + RADIUS * math.sin(theta)])

		csys = colorsys.hsv_to_rgb(fract / 6, 1, 1)
		self.color = (csys[0]*255, csys[1]*255, csys[2]*255)

	def int_pos(self):
		return (int(self.pos[0]), int(self.pos[1]))

	def draw(self, surface):
		for line in self.path:
			pygame.draw.line(surface, self.color, line[0], line[1])
		pygame.draw.circle(surface, self.color, self.int_pos(), 4)

	def think(self, state, t):
		gvec = np.array([0., 0.])
		for dot in state.dots:
			if dot is self:
				continue

			dpos = (dot.pos - self.pos)
			dgrav = dpos / (mag(dpos) ** 2)

			gvec += dgrav

		cgrav = norm(CENTER - self.pos)

		self.gravity = norm(gvec) + cgrav

	def advance(self, state, t):
		line_start = self.int_pos()
		self.pos += norm(self.gravity) * 20 * t
		line_end = self.int_pos()

		self.path.append((line_start, line_end))


def reset_state():
	state = dotdict.dotdict()

	state.dots = []
	for i in range(DOTS):
		dot = Dot(float(i) / DOTS)
		state.dots.append(dot)

	return state

def advance_state(state, t):
	for dot in state.dots:
		dot.think(state, t)

	for dot in state.dots:
		dot.advance(state, t)

def draw_state(state, surface):
	for dot in state.dots:
		dot.draw(surface)

def main():
	pygame.init()
	screen = pygame.display.set_mode((600, 600))
	state = reset_state()

	running = True
	paused = True
	last_advance_time = time.monotonic()
	while running:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				if event.key == pygame.K_SPACE:
					state = reset_state()
				if event.key == pygame.K_p:
					paused = not paused
			elif event.type == pygame.QUIT:
				running = False

		now = time.monotonic()
		dt = now - last_advance_time
		last_advance_time = now
		if not paused:
			advance_state(state, dt)

		screen.fill((0, 0, 0))
		draw_state(state, screen)
		pygame.display.flip()

if __name__ == '__main__':
	main()
