import toml

conf = toml.load('lidar-nn/conf.toml')

locals().update(conf)

BOUNDS = [*EAST_BOUNDS, *NORTH_BOUNDS, *ELEV_BOUNDS]
EAST_MIN, EAST_MAX, NORTH_MIN, NORTH_MAX, ELEV_MIN, ELEV_MAX = BOUNDS
