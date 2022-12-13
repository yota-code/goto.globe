#!/usr/bin/env python3

import enum
import dataclasses

class RouteAltitude(enum.IntEnum) :
	UNSPECIFIED = 0 
	HEIGHT = 1 # relative to the ground
	BARO = 2 # actual baro measure (baro setting unknown)
	MSL = 3 # standard atmosphere (or geoid)
	WGS84 = 4 # pure GPS ellispoid

class RouteSpeed(enum.IntEnum) :
	UNSPECIFIED = 0
	GROUND = 1 # ground speed
	AIR = 2 # air speed

class RouteHeading(enum.IntEnum) :
	UNSPECIFIED = 0
	TRACK = 1
	HEADING = 2
	FIXED = 3

class RouteAttr(enum.IntEnum) :
	UNSPECIFIED = 0
	PARKING = 2
	TAXIWAY = 3
	GOAROUND = 4
	FLIGHT = 5
	DESCEND = 6

@dataclasses.dataclass
class RoutePiece() :

	verb: str
	latitude: float
	longitude: float
	leg_radius: float
	is_large_arc: bool
	altitude: float
	altitude_typ: RouteAltitude
	speed: float
	speed_typ: RouteSpeed
	heading: float
	heading_typ: RouteHeading
	corridor_width: float
	corridot_height: float
	terrain_elevation: float
	geoid_elevation: float
	leg_attribute: RouteAttr
	stop_at: bool

	def to_binary(self) :
		waypoint_stt = struct.Struct('ddfbfifififfffii')
		return waypoint_stt.pack(* dataclasses.astuple(self))

	def to_tsv(self) :
		return '\t'.join(i.name if isinstance(i, enum.Enum) else str(i) for i in dataclasses.astuple(self))

