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
	m = mag(v)
	if m == 0:
		return v
	else:
		return v / mag(v)

class Dot:
	def __init__(self, fract):
		self.size = .5
		self.deleted = False

		theta = random.random() * TAU
		self.pos = np.array([CENTER[0] + RADIUS * math.cos(theta), CENTER[1] + RADIUS * math.sin(theta)])

		csys = colorsys.hsv_to_rgb(fract / 6, 1, 1)
		self.color = np.array(csys) * 255

	def int_pos(self):
		return (int(self.pos[0]), int(self.pos[1]))

	def draw(self, surface):
		pygame.draw.circle(surface, self.color, self.int_pos(), max(int(self.size), 1))

	def think(self, state, t):
		if self.deleted:
			return False

		gvec = np.array([0., 0.])
		for dot in state.dots:
			if dot is self or dot.deleted:
				continue

			dpos = (dot.pos - self.pos)
			dist = mag(dpos)

			if dist < (self.size + dot.size)/2:
				self.merge(dot)
				continue

			dgrav = dpos / (dist ** 2)
			gvec += dgrav

		dcenter = CENTER - self.pos
		if mag(dcenter) < self.size:
			self.deleted = True

		cgrav = norm(dcenter)

		self.gravity = norm(gvec) + cgrav
		return True

	def advance(self, state, t):
		line_start = self.int_pos()
		self.pos += norm(self.gravity) * 20 * t
		line_end = self.int_pos()

		state.paths.append(dotdict.dotdict(start=line_start, end=line_end, color=self.color, width=self.size))

	def merge(self, other):
		total_size = self.size + other.size

		self.color = (self.color*self.size + other.color*other.size) / total_size
		self.size = (self.size/2 + other.size/2) * math.sqrt(3)
		other.deleted = True


def reset_state():
	state = dotdict.dotdict()

	state.dots = []
	for i in range(DOTS):
		dot = Dot(float(i) / DOTS)
		state.dots.append(dot)

	state.paths = []

	return state

def advance_state(state, t):
	new_dots = []
	for dot in state.dots:
		alive = dot.think(state, t)
		if alive:
			new_dots.append(dot)
	state.dots = new_dots

	for dot in state.dots:
		dot.advance(state, t)

def draw_state(state, surface):
	for line in state.paths:
		pygame.draw.line(surface, line.color, line.start, line.end, max(int(line.width*2), 1))
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
