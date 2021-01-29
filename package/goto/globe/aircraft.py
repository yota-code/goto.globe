#!/usr/bin/env python3

import collections
import math

import geometrik.threed as g3d

import goto.globe.blip
from goto.globe.common import *

class Aircraft() :

	dt_ms = 100
	rec_lst = ['t_ms', 't', 'lat', 'lon', 'alt', 'psi', 'vx', 'vz']

	def __init__(self, lat, lon, alt, psi, vx, vz) :

		self.t_ms = 0 # temps en millisecondes
		self.dt = self.dt_ms / 1000.0

		self.lat = lat
		self.lon = lon

		self.alt = alt

		self.psi = psi
		self.vx = vx
		self.vz = vz

		self.rec = collections.defaultdict(list)

	def step(self, vx=None, vz=None, turn_value=0.0, turn_mode="psid") :

		if vx is None :
			vx = self.vx
		if vz is None :
			vz = self.vz

		if turn_mode == "psid" :
			psid = turn_value
			rol = math.atan( psid * vx / earth_gravity )
		elif turn_mode == "rol" :
			rol = turn_value
			psid = earth_gravity * math.tan(rol) / self.vx
		else :
			raise ValueError

		self.psi += psid * self.dt

		px = goto.globe.blip.Blip(self.lat, self.lon).to_vector()

		north = g3d.Vector(0.0, 0.0, 1.0, True)
		
		nx = px
		ny = (north @ nx).normalized()
		nz = (nx @ ny)
		
		hx = nx
		hz = math.cos(self.psi) * nz + math.sin(self.psi) * ny
		hy = (hz @ hx)

		# l'angle d'avancement autour de la terre est donné par :
		alpha = (self.vx * self.dt) / ( earth_radius + self.alt + 0.5*self.vz*self.dt )

		jx = math.cos(alpha) * hx + math.sin(alpha) * hz

		b = goto.globe.blip.Blip.from_vector(jx)
		self.lat = b.lat
		self.lon = b.lon

		self.alt += self.vz*self.dt

		self.t_ms += self.dt_ms
		self.t = self.t_ms / 1000.0

		self.record()

	def record(self) :
		for k in self.rec_lst :
			self.rec[k].append( getattr(self, k) )

	def dump(self, pth) :

		# pth = Path(pth).with_suffix('.tsv')

		stack = [
			self.rec_lst,
		]
		for i in range(len(self.rec['t'])) :
			stack.append(
				[ self.rec[k][i] for k in self.rec_lst ]
			)

		pth.save(stack)
