#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

import goto.globe

from goto.globe.segment.arc import SegmentArc

line_AE, arc_EF, line_FB = SegmentArc.from_turn_3pt(
	goto.globe.Blip(45.0, 0.0),
	goto.globe.Blip(0.0, 0.0), 
	goto.globe.Blip(0.0, 45.0),
	-1000000.0
)

x_lst, y_lst = list(), list()

for x in np.linspace(0.0, 1.0, 1024) :
	t = 30.0*(x**5/5 - x**4/2 + x**3/3)
	p = arc_EF.position_at(t)
	b = goto.globe.Blip.from_vector(p)
	x_lst.append(b.lat)
	y_lst.append(b.lon)

plt.subplot(1,2,1)
plt.plot(x_lst, y_lst)
plt.grid()

xz_lst = list()
for x in np.linspace(1.0 - 1e-3, 1.0, 1024) :
	t = 30.0*(x**5/5 - x**4/2 + x**3/3)
	p = arc_EF.position_at(t)
	b = goto.globe.Blip.from_vector(p)
	xz_lst.append(b.lat)
	# yz_lst.append(b.lon)

yz_lst = list()
for x in np.linspace(0.0, 1e-3, 1024) :
	t = 30.0*(x**5/5 - x**4/2 + x**3/3)
	p = arc_EF.position_at(t)
	b = goto.globe.Blip.from_vector(p)
	# xz_lst.append(b.lat)
	yz_lst.append(b.lon)

plt.subplot(2,2,2)
plt.axhline(0.0, color="red")
# plt.plot(x_lst)
plt.plot(xz_lst)
plt.grid()

plt.subplot(2,2,4)
plt.axhline(0.0, color="red")
plt.plot(yz_lst)
plt.grid()
plt.show()
