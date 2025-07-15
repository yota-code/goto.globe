#!/usr/bin/env python3

import sys

import numpy as np
import matplotlib.pyplot as plt

from goto.globe.blip import Blip
from goto.globe.segment.turn import turn_3pt, turn_4pt
from goto.globe.plot import GlobePlotMpl

from cc_pathlib import Path

A = Blip(43.408233, 5.259825)
B = Blip(43.446844, 5.201197)
C = Blip(43.476095, 5.268565)

E, F, pE, pF, w = turn_3pt(A, B, C, 1000, Path("01.json"))
