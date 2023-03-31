#!/usr/bin/env python3

import enum
import dataclasses
import struct

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
	corridor_height: float
	terrain_elevation: float
	geoid_elevation: float
	leg_attribute: RouteAttr
	stop_at: bool

	def __getitem__(self, k) :
		return getattr(self, k)

	def __setitem__(self, k, v) :
		setattr(self, k, v)

	def to_binary(self) :
		waypoint_stt = struct.Struct('ddfbfifififfffii')
		print(dataclasses.astuple(self)[1:])
		return waypoint_stt.pack(* dataclasses.astuple(self)[1:])

	def to_tsv(self) :
		return '\t'.join(i.name if isinstance(i, enum.Enum) else str(i) for i in dataclasses.astuple(self))

	def to_lang_c(self) :
		return '\t\t{' + ', '.join(f'UPMV{i.__class__.__name__.upper()}_{i.name}' if isinstance(i, enum.Enum) else str(i) for i in dataclasses.astuple(self)[1:]) + '},'

