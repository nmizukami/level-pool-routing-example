#!/usr/bin/env python

import sys
import argparse
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
import matplotlib.pyplot as plt

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Lake routing using Elevation-Storage-Discharge relationship')
    parser.add_argument('innc',
                        help='input inflow netcdf')
    parser.add_argument('inasc',
                        help='Elevation-Storage-Outflow relationship')

    args = parser.parse_args()

    return(args)


def read_elev_storage_outflow_data(asc_in):
    return  pd.read_csv(asc_in, delim_whitespace=True, header=0, names=['z','s','o'])


def read_inflow(nc_in):
    return xr.open_dataset(nc_in)


def do_routing(ds_inflow, df_data, init_z=0.5):
    '''
      Solve 2*S(t+1)/dt+O(t+1) = I(t+1)+ I(t) + 2*S(t)/dt-O(t)
      given relaionship between S vs 2*S/dt+O and O vs 2*S/dt+O
    '''

    times = ds_inflow.time.values.astype(datetime)
    dt = (times[1]-times[0])*1e-9

    inflow = np.squeeze(ds_inflow.inflow.values)

    SO2 = 2*df_data.s/dt + df_data.o

    ntstep = len(inflow)
    # initialize
    Z = np.full(ntstep, -999., dtype=float)
    S = np.full(ntstep, -999., dtype=float)
    O = np.full(ntstep, -999., dtype=float)

    # start time stepping...
    for tidx, time in enumerate(times):

        print('time step: %d'%tidx)
        if tidx == 0:
            # Initial States
            S[0] = linear_interp(init_z, df_data.z.values, df_data.s.values)
            O[0] = linear_interp(init_z, df_data.z.values, df_data.o.values)
        else:
            right = (inflow[tidx-1]
                    + inflow[tidx]
                    + 2*S[tidx-1]/dt - O[tidx-1] )

            O[tidx] = linear_interp(right, SO2.values, df_data.o.values)
            S[tidx] = linear_interp(right, SO2.values, df_data.s.values)

    df_out = pd.DataFrame(data={'time': ds_inflow.time.values, 'inflow': inflow, 'outflow': O, 'storage': S})

    return df_out


def linear_interp(x_in, x_array, y_array):
    ''' Linear interpolation '''

    if x_in > x_array[-1]:
        y_out = y_array[-1]
    else:
        for idx, xx in enumerate(x_array):
            if xx > x_in:
                y_out = ( y_array[idx-1] +
                        ( y_array[idx]-y_array[idx-1])/(x_array[idx]-x_array[idx-1])*(x_in - x_array[idx-1]) )
                break

    return y_out


def flow_plot(df):

    df.inflow.plot(label='inflow')
    df.outflow.plot(label='outflow')
    plt.legend()
    plt.xlabel('Time step')
    plt.ylabel('Q,m3/s')
    plt.show()


# main
if __name__ == '__main__':

  args = process_command_line()

  df_data = read_elev_storage_outflow_data(args.inasc)

  ds_inflow = read_inflow(args.innc)

  df_outflow = do_routing(ds_inflow, df_data)

  flow_plot(df_outflow)

