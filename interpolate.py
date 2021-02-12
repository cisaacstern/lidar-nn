import pathlib

import numpy as np
from scipy import interpolate

import config as c

class Interpolate():

    def __init__(self, filename, bounds):
        '''
        Parameters
        ==========
        filename : str
            files should be in .csv format and their names should begin
            with the date of data collection in YYYYMMDD format
        bounds : list or tuple of floats
            [east_min, east_max, north_min, north_max, elev_max, elev_min]
        '''
        self.filename = filename
        self.filepath = pathlib.Path.cwd() / 'lidar-nn' / 'data' / filename
        self.bounds = bounds
        self.xyz = self._import_xyz(filepath=self.filepath, bounds=bounds)

    @staticmethod
    def _import_xyz(filepath, bounds):
        '''
        See __init__() method for parameter types and information.
        '''
        xyz = np.genfromtxt(fname=filepath, delimiter=',', skip_header=1)
        
        Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]
        assert(not(np.any((Easting < bounds[0])
                            |(Easting > bounds[1])))), 'Easting out of range.'
        assert(not(np.any((Northing < bounds[2])
                            |(Northing > bounds[3])))), 'Northing out of range.'
        assert(not(np.any((Elevation < bounds[4])
                            |(Elevation > bounds[5])))), 'Elevation out of range.'

        return xyz

    def interpolate_grid(self, xyz, res):
            '''
            takes xyz pointcloud data, outputs nearest neighbor interpolation
            '''
            Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]

            xi = np.linspace(c.EAST_MIN, c.EAST_MAX, res)
            yi = np.linspace(c.NORTH_MIN, c.NORTH_MAX, res)

            return interpolate.griddata((Easting, Northing), Elevation, 
                                        (xi[None,:], yi[:,None]), method='nearest')