#!/usr/bin/env python3
import sys
import os
import math
import struct
import numpy as np
from cc_pathlib import Path

import goto.globe

from goto.globe.plot import GlobePlotMpl,GlobePlotGps
from goto.globe.segment import *

"""
typedef struct {
    double latitude;  /**< latitude used to compute the grid @range{-90.0, 90.0} @unit{degrees} */
    double longitude; /**< longitude used to compute the grid @range{-180.0, 180.0} @unit{degrees} */

    float direction; /**< direction of reference, used to compute the grid can either be based on the current heading or track, depending on the value set in the configuration */

    float offset_x;        /**< distance to the origin of the pattern, in front of the position described in lat, lon @unit{meter} */
    float dist_min;        /**< distance to the closest point of the grid */
    float dist_max;        /**< distance to the farthest point of the grid */
    float sector_aperture; /**< angle of the conical part of the grid @unit{dregree} */
    float sector_bias;     /**< extra offset added to the current direction of the grid @unit{degree} */
    float corridor_width;  /**< width of the corridor @unit{meter} */

    uint16_t elevation[51]; /**< highest terrain elevation value in the considered cell @unit{feet} */
    uint8_t padding[6];

} RcmTerrainGridInfo_t;
"""
RCM_GRID_HEADER_FORMAT = '=ddfffffff' # Total size:
SIZE_RCM_GRID_HEADER = struct.calcsize(RCM_GRID_HEADER_FORMAT)
RCM_GRID_ELEV_FORMAT = '=h' # Total size:
SIZE_RCM_GRID_ELEV = struct.calcsize(RCM_GRID_ELEV_FORMAT)

NB_ROW_MAX = 5
NB_COL_MAX = 10

## utils
def cosd(deg):
    return np.cos(deg*np.pi/180)

def sind(deg):
    return np.sin(deg*np.pi/180)

def asind(d):
    return np.arcsin(d)*180/np.pi

def get_terrain_hull(latitude, longitude,direction,offset_x,dist_min,dist_max,sector_aperture,sector_bias,corridor_width):
	"""
	Compute terrain grid using parallel layout : divide separator arc by NB_ROW_MAX
	"""

	# compute sectors dimensions
	col_width = (dist_max - dist_min)/NB_COL_MAX
	row_aper = sector_aperture/NB_ROW_MAX

	# compute sector 50
	helico_pos = goto.globe.Blip(latitude, longitude)
	helico_dir = math.radians(direction)
	direction = 0 #point based on oreinted gframe

	point0 = Hz = helico_pos.as_vector
	Hx, Hy = Hz.oriented_frame(helico_dir)
	#point1 = point0 + np.array([offset_x*cosd(direction),offset_x*sind(direction)])
	point1 = Hz.deflect(Hx, offset_x / goto.globe.earth_radius)
    
	#compute min arc
	th2 = sector_aperture/2.0 + direction + sector_bias
	th2b = th2 - sector_aperture
	#point2 = point1+np.array([dist_min*cosd(th2),dist_min*sind(th2)])
	#point2b = point1+np.array([dist_min*cosd(th2b),dist_min*sind(th2b)])
    
	#point2 = point1.deflect(Hy, dist_min*sind(th2) / goto.globe.earth_radius)
	#point2 = point3.deflect(Hx, dist_min*cosd(th2) / goto.globe.earth_radius)

	# compute separator arc
	distp3 = (corridor_width/2)/sind(sector_aperture/2)
	#point3 = point1+np.array([distp3*cosd(th2),distp3*sind(th2)])
	#point3b = point1+np.array([distp3*cosd(th2b),distp3*sind(th2b)])

	point3 = point1.deflect(Hy, distp3*sind(th2) / goto.globe.earth_radius)
	point3 = point3.deflect(Hx, distp3*cosd(th2) / goto.globe.earth_radius)

	point3b = point1.deflect(Hy, distp3*sind(th2b) / goto.globe.earth_radius)
	point3b = point3b.deflect(Hx, distp3*cosd(th2b) / goto.globe.earth_radius)

	# compute max arc
	th4 = asind((corridor_width/2)/dist_max)+direction+sector_bias
	th4b = -asind((corridor_width/2)/dist_max)+direction+sector_bias
	
	#point4 = point1+np.array([dist_max*cosd(th4+direction+sector_bias),dist_max*sind(th4+direction+sector_bias)])
	#point4b = point1+np.array([dist_max*cosd(-th4+direction+sector_bias),dist_max*sind(-th4+direction+sector_bias)])
    
	point4 = point1.deflect(Hy, dist_max*sind(th4) / goto.globe.earth_radius)
	point4 = point4.deflect(Hx, dist_max*cosd(th4) / goto.globe.earth_radius)

	point4b = point1.deflect(Hy, dist_max*sind(th4b) / goto.globe.earth_radius)
	point4b = point4b.deflect(Hx, dist_max*cosd(th4b) / goto.globe.earth_radius)

	hull_coord = (point0,point1,point3,point4,point4b,point3b)
    #angl_coord = [0,0,th2,th2,th4+direction+sector_bias,-th4+direction+sector_bias,th2b,th2b]


	# compute grid nodes coordinates
	nodes_coord= []
	for u in range(NB_ROW_MAX+1): 
		coordr = []
		for v in range(NB_COL_MAX+1):
			#compute sector radius
			sub_dist = (v)*col_width+dist_min 
			sub_th = (sector_aperture/2 - u*row_aper)
            
			#switch from cone to corridor
			if sub_dist > distp3: 
				sub_width = distp3*sind(sub_th)
				sub_th = asind((sub_width)/sub_dist)
            
			#pointx = point1+np.array([sub_dist*cosd(sub_th+direction+sector_bias),sub_dist*sind(sub_th+direction+sector_bias)])
			pointx = point1.deflect(Hy, sub_dist*sind(sub_th+direction+sector_bias) / goto.globe.earth_radius)
			pointx = pointx.deflect(Hx, sub_dist*cosd(sub_th+direction+sector_bias) / goto.globe.earth_radius)
			coordr.append(pointx)
            
		nodes_coord.append(coordr)


	return hull_coord,nodes_coord

def read_terrain_grid(filepath=Path("terrain_grid.bin")):
	"""
	Reads the terrain_grid.bin file, unpacks the RcmFlightPath_t structure,
	and extracts the valid waypoint data into a list.
	"""

	summary_map = dict()

	with open(filepath, 'rb') as f:
		full_data = f.read()

		# Unpack the header section
		header_bytes = full_data[0:SIZE_RCM_GRID_HEADER]
		latitude, longitude,direction,offset_x,dist_min,dist_max,sector_aperture,sector_bias,corridor_width = struct.unpack(
			RCM_GRID_HEADER_FORMAT, header_bytes
			)



		print(f"--- Terrain Grid Config ---")
		print(f"  latitude: {latitude}")
		print(f"  longitude: {longitude}")
		print(f"  direction: {direction}")
		print(f"  offset_x: {offset_x}")
		print(f"  dist_min: {dist_min}")
		print(f"  dist_max: {dist_max}")
		print(f"  sector_aperture: {sector_aperture}")
		print(f"  sector_bias: {sector_bias}")	
		print(f"  corridor_width: {corridor_width}")	
		print(f"--------------------------")

		# Calculate the starting offset for the elevation array
		elevation_array_start_offset = SIZE_RCM_GRID_HEADER
		elevation = []
		for i in range(51):
			current_elevation_offset = elevation_array_start_offset + (i * SIZE_RCM_GRID_ELEV)
			elevation_bytes = full_data[current_elevation_offset : current_elevation_offset + SIZE_RCM_GRID_ELEV]
			elevx = struct.unpack(RCM_GRID_ELEV_FORMAT, elevation_bytes)[0]
			elevation.append(elevx)
			#print(f" ->  {elevx}")

		summary_map = {
			'latitude' : latitude,
			'longitude' : longitude,
			'direction' : direction,
			'offset_x' : offset_x,
			'dist_min' : dist_min,
			'dist_max' : dist_max,
			'sector_aperture' : sector_aperture,
			'sector_bias' : sector_bias,
			'corridor_width' : corridor_width,
			'elevation' : elevation,
		}
		filepath.with_suffix('.info.json').save(summary_map, verbose=True)

		terrain_grid_config= (latitude, longitude,direction,offset_x,dist_min,dist_max,sector_aperture,sector_bias,corridor_width)


	return terrain_grid_config,elevation

try:
	print("use input file")
	binary_file_path = Path(sys.argv[1])
except:
	binary_file_path = Path("terrain_grid.bin")

json_file_path = os.path.splitext(os.path.basename(binary_file_path))[0]+".json"
terrain_grid_config, elevation = read_terrain_grid(binary_file_path)

latitude, longitude,direction,offset_x,dist_min,dist_max,sector_aperture,sector_bias,corridor_width = terrain_grid_config

if dist_min < dist_max:
	hull_coord, nodes_coord = get_terrain_hull(latitude, longitude,direction,offset_x,dist_min,dist_max,sector_aperture,sector_bias,corridor_width)
	p0,p1,p3,p4,p4b,p3b = hull_coord


	"""
	Gzx = Hz.deflect(Hx, 3_000_000.0 / goto.globe.earth_radius)

	with GlobePlotMpl("test_grid") as plt :
	#with GlobePloGps(json_file_path) as plt :
		plt.add_point(Hx, "Hx")
		plt.add_point(Hy, "Hy")
		plt.add_point(Hz, "Hz")
		plt.add_point(Gzx, "Gzx", 'r')
		plt.add_line(Hz, Gzx, 'g')
	"""

	with GlobePlotGps(Path(json_file_path)) as gpl :
		gpl.add_point(p0, "Hz:{},{},{}".format(latitude,longitude,direction))
		obj = SegmentLine(p0, p1)
		gpl.add_segment(obj)
		obj = SegmentLine(p1, p3)
		gpl.add_segment(obj)
		obj = SegmentLine(p3, p4)
		gpl.add_segment(obj)
		obj = SegmentLine(p1, p3b)
		gpl.add_segment(obj)
		obj = SegmentLine(p3b, p4b)
		gpl.add_segment(obj)

		#gpl.point_map[f"P{index}"] = Cx
		#obj = SegmentArc(p4, p4b, center=p1, turnway=-1)
		#gpl.add_segment(obj)

		#plot sectors
		for i in range(NB_ROW_MAX):
			for j in range(NB_COL_MAX):
				gpl.add_segment(SegmentLine(nodes_coord[i][j], nodes_coord[i+1][j]))
				gpl.add_segment(SegmentLine(nodes_coord[i+1][j], nodes_coord[i+1][j+1]))
				gpl.add_segment(SegmentLine(nodes_coord[i+1][j+1], nodes_coord[i][j+1]))
				gpl.add_segment(SegmentLine(nodes_coord[i][j+1], nodes_coord[i][j]))			

	with GlobePlotGps(Path("elev_"+json_file_path)) as gpl :
		#plot elev
		for i in range(NB_ROW_MAX):
			for j in range(NB_COL_MAX):
				sector_id = NB_ROW_MAX * (j) + ((NB_ROW_MAX-1) - i)
				gpl.add_point(nodes_coord[i+1][j],f"P{sector_id}:{elevation[sector_id]}")
				#gpl.point_map[f"P{index}"] = Cx
else:
	print("Invalid terrain grid conf")