#!/usr/bin/env python

import pandas as pd
import xarray as xr

inflow = [0.0, 79.2, 212.5, 320.5, 381.9, 400.0,
          386.1, 352.3, 308.4, 261.7, 216.5, 175.6,
          140.1, 110.2, 85.7, 65.9, 50.3, 38.1, 28.6,
          21.4, 15.9, 11.7, 8.6, 6.3, 4.6, 3.4, 2.4,
          1.8, 1.3, 0.9, 0.7, 0.5, 0.3, 0.2, 0.2,
          0.1, 0.1, 0.1, 0.0, 0.0, 0.0]

times = pd.date_range('2000-01-01 00:00', periods=len(inflow), freq='1800S')

ds = xr.Dataset({'inflow': (['time'], inflow)},
                coords={'time': times})

ds.inflow.encoding['_FillValue'] = None
ds.inflow.encoding['dtype']      = 'float32'
ds.inflow.attrs['units']         = 'm3/s'

ds.to_netcdf('inflow.ch9sturm.nc')
