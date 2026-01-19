#!/usr/bin/env python3

import math

import goto.globe
import goto.globe.plot
import goto.globe.segment

from cc_pathlib import Path

def check(a, b, rel_tol) :
	assert math.isclose(a, b, rel_tol=rel_tol), f"\na={a}\nb={b}"

def bam2deg(i) :
	return 360.0 * float(i) / 2**32

# at 30.0 dans 4567g7rtez97re


R_XtkCurrSegmGeo = 25.938452

I_LatPrevWpt = 518682729
I_LonPrevWpt = 62469634
I_LatNextWpt = 529871706
I_LonNextWpt = 105435481
I_LatHel = 518736781
I_LonHel = 62651810

R_Vn = 9.063788414001465
R_Ve = 23.586193084716797
R_Tk = 68.97904968261719 # 68.97904835629065
R_ZUav = 950.7836303710938

R_XtkCurrSegmGeo = 25.938451766967773

Re = goto.globe.earth_radius + R_ZUav

trk_rad = math.atan2(R_Ve, R_Vn)
trk = math.degrees(trk_rad)
vgnd = math.sqrt(R_Ve**2+R_Vn**2)

assert math.isclose(R_Tk, trk, rel_tol=1e-5)

Wp = goto.globe.Blip(bam2deg(I_LatPrevWpt), bam2deg(I_LonPrevWpt))
Wn = goto.globe.Blip(bam2deg(I_LatNextWpt), bam2deg(I_LonNextWpt))
L = goto.globe.segment.SegmentLine(Wp, Wn)

H = goto.globe.Blip(bam2deg(I_LatHel), bam2deg(I_LonHel))

Hx, Hy = H.as_vector.oriented_frame(trk_rad)

V = H.as_vector.deflect(Hx, vgnd / Re)

L.compute_sta(H)

check(R_XtkCurrSegmGeo, -L.dev_lat * Re, 1e-3)

with goto.globe.plot.GlobePlotGps(Path("loil0.json")) as plt :
	plt.add_point(Wp, "Wp")
	plt.add_point(Wn, "Wn")
	plt.add_polyline([Wp, Wn])
	plt.add_point(H, "H")
	plt.add_point(L.Px, "Px")
	plt.add_polyline([H, V])
	# plt.add_point(L.Pz, "Pz")
	plt.add_point(Hx, "Hx")

