#!/home/skycoder/Desktop/dataducks/back-end/mickey/bin/python

import sys
# import osgeo_utils.rgb2pct as a convenience to use as a script
from osgeo_utils.rgb2pct import *  # noqa
from osgeo_utils.rgb2pct import main
from osgeo.gdal import deprecation_warn


deprecation_warn('rgb2pct')
sys.exit(main(sys.argv))
