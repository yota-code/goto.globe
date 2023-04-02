import numpy as np
from scipy.interpolate import RectBivariateSpline as Spline
import pygeodesy as geo
from pygeodesy.ellipsoidalVincenty import LatLon

class Geoid12B(): #NAD 83 Ellipsoid
    # https://www.ngs.noaa.gov/GEOID/GEOID12B/GEOID12B_CONUS.shtml
    # Download a Geoid Grid in little endian binary format ('g2012bu5.bin')
    def __init__(self, leBinFile):
        glamn, glomn, dla, dlo = np.fromfile(leBinFile,'<f8',4)
        glomn = -360 + glomn
        nla, nlo, ikind = np.fromfile(leBinFile,'<i4',11)[8:]
        lats = np.arange(glamn, glamn+dla*nla-.001,dla)
        longs = np.arange(glomn, glomn+dlo*nlo-.001,dlo)
        grid = np.fromfile(leBinFile,'<f4')[11:].reshape(nla,nlo)
        self.interp = Spline(lats, longs, grid)
    def height(self, longitude, latitude):
        return self.interp.ev(latitude, longitude)

class EGM96(): #WGS 84 Ellipsoid
    # http://earth-info.nga.mil/GandG/wgs84/gravitymod/egm96/binary/binarygeoid.html
    # Download WW15MGH.DAC
    def __init__(self,binFile):
        egm = np.fromfile(binFile,'>i2').reshape(721,1440)/100
        longs = np.arange(0,360,0.25)
        lats = np.arange(-90,90.1,0.25)
        self.interp = Spline(lats, longs, egm)
    def height(self, longitude, latitude):
        latitude *= -1
        #longitude[longitude < 0] += 360
        if longitude < 0:
            longitude += 360
        return self.interp.ev(latitude,longitude)
        
if __name__ == '__main__' :
	wgs = geo.datum.Datums.WGS84
	# example: convert WGS 84/EGM 96 location/elevation to NAD 83/NAVD 88
	egm = EGM96('WW15MGH.DAC')
	
	x, y = np.mgrid[:1001, :1001]
	z = np.zeros((1001, 1001))
	for i, lon in enumerate(np.linspace(5.0, 6.0, 1001)) :
		for j, lat in enumerate(np.linspace(43.0, 44.0, 1001)) :
			z[i, j] = egm.height(lon, lat)
			# print(i, j, z[i,j])
			
	print(x.shape, y.shape, z.shape)
			
	import matplotlib.pyplot as plt
	
	fig = plt.figure('3D surface')
	ax = fig.add_subplot(111, projection='3d')
	
	ax.plot_wireframe(5.0 + x / 1000.0, 43.0 + y / 1000.0, z)
	plt.show()
