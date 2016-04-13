# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 13:22:59 2016

Cellular Automata: Regolith Formation
Using CellLab

@author: Katherine
"""

import time
import matplotlib
import numpy as np
from landlab import RasterModelGrid
from landlab.ca.celllab_cts import Transition, CAPlotter
from landlab.ca.raster_cts import RasterCTS
from fracture_grid import make_frac_grid

def setup_transition_list():
    """
    Creates and returns a list of Transition() objects to represent state
    transitions for an unbiased random walk.

    Parameters
    ----------
    (none)

    Returns
    -------
    xn_list : list of Transition objects
            List of objects that encode information about the link-state transitions.

    Notes
    -----
    State 0 represents fluid and state 1 represents a particle (such as a
    sediment grain, tea leaf, or solute molecule).

    The states and transitions are as follows:

    Pair state      Transition to       Process             Rate (cells/s)
    ==========      =============       =======             ==============
    0 (0-0)         (none)              -                   -
    1 (1-0)         2 (1-1)             left/down motion    10.0
    2 (0-1)         1 (1-1)             right/up motion     10.0
    3 (1-1)         (none)              -                   -

    """

    # Create an empty transition list
    xn_list = []

    # Append two transitions to the list.
    # Note that the arguments to the Transition() object constructor are:
    #  - Tuple representing starting pair state
    #    (left/bottom cell, right/top cell, orientation)
    #  - Tuple representing new pair state
    #    (left/bottom cell, right/top cell, orientation)
    #  - Transition rate (cells per time step, in this case 1 sec)
    #  - Name for transition
    xn_list.append( Transition((1,0,0), (1,1,0), 1., 'saprolite formation') )
    xn_list.append( Transition((0,1,0), (1,1,0), 1., 'saprolite formation') )
    return xn_list
        
        

# INITIALIZE
# User-defined parameters
nr = 300  # number of rows in grid
nc = 300  # number of columns in grid
plot_interval = 0.5   # time interval for plotting, sec
run_duration = 20.0   # duration of run, sec
report_interval = 10.0  # report interval, in real-time seconds

# Remember the clock time, and calculate when we next want to report
# progress.
current_real_time = time.time()
next_report = current_real_time + report_interval

# Create grid
mg = RasterModelGrid(nr, nc, 1.0)

# Make the boundaries be walls
mg.set_closed_boundaries_at_grid_edges(True, True, True, True)

#Create a node-state dictionary
ns_dict = { 0 : 'rock', 1 : 'saprolite' }

#Create the transition list
xn_list = setup_transition_list()

# Create the node-state array and attach it to the grid
node_state_grid = mg.add_zeros('node', 'node_state_map', dtype=int)
 
# Initialize the node-state array: here, the initial condition is a set of fracture lines.
node_state_grid.shape=((mg.number_of_node_rows,mg.number_of_node_columns))
node_state_grid=make_frac_grid(10, numrows=nr, numcols=nc, model_grid=node_state_grid)

# For visual display purposes, set all boundary nodes to fluid
node_state_grid[mg.closed_boundary_nodes] = 0

# Create the CA model
ca = RasterCTS(mg, ns_dict, xn_list, node_state_grid)

# Set up colors for plotting
grain = '#5F594D'
fluid = '#D0E4F2'
clist = [fluid,grain]
my_cmap = matplotlib.colors.ListedColormap(clist)

# Create a CAPlotter object for handling screen display
ca_plotter = CAPlotter(ca, cmap=my_cmap)

# Plot the initial grid
ca_plotter.update_plot()

# RUN
current_time = 0.0
while current_time < run_duration:

# Once in a while, print out simulation real time to let the user
# know that the sim is running ok
    current_real_time = time.time()
    if current_real_time >= next_report:
        print('Current simulation time '+str(current_time)+'  \
                   ('+str(int(100*current_time/run_duration))+'%)')
        next_report = current_real_time + report_interval

# Run the model forward in time until the next output step
    ca.run(current_time+plot_interval, ca.node_state, plot_each_transition=False)
    current_time += plot_interval

# Plot the current grid
    ca_plotter.update_plot()
    
ca_plotter.finalize()


