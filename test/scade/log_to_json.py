#!/usr/bin/env python3


"""""


POINT	P1	<lat>	<lon>
LINE	<a_lat>	<a_lon>	<b_lat>	<b_lon>
ARC	<a_lat>	




"""""

import sys

from cc_pathlib import Path

from goto.globe.plot import GlobePlotGps
from goto.globe.blip import Blip, gpoint

src_pth = Path(sys.argv[1]) # recupérer le chemin du fichier .tsv
dst_pth = src_pth.with_suffix('.json') # construire un chemin pour le fichier .json

with GlobePlotGps(dst_pth) as gpl :
	for line in src_pth.read_text().splitlines() :
		print(line)

		line_lst = [u.strip() for u in line.split('\t')]
		
		if line_lst[0] == "POINT" :
			a_lat = float(line_lst[2])
			a_lon = float(line_lst[3])
			gpl.add_point(Blip(a_lat, a_lon), line_lst[1])

		elif line_lst[0] == "LINE" :
			pass

		elif line_lst[0] == "ARC" :
			pass



