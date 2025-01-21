"""
PyGMT-based Slip Distribution Filtering and Visualization
Javiera Álvarez, 2024

This script processes and visualizes slip distribution data for seismic events,
applying spatial filters and creating detailed topographic maps. Key features:

1. Slip tapering along longitude
2. Distance-based filtering from trench location
3. Topographic visualization with PyGMT
4. Automated processing of multiple slip distribution models

Functions:
- Slip tapering with cosine function
- Trench-distance filtering using KD-tree
- Topographic map generation with slip overlay

Dependencies:
   - pygmt: GMT-based plotting
   - numpy: numerical operations
   - pandas: data handling
   - scipy: spatial calculations
"""

#%%
import pygmt
import numpy as np
import pandas as pd
import os
from scipy.spatial import cKDTree

def apply_taper(lon, slip, taper_start_lon=-71):
   """
   Applies cosine taper to slip values starting from specified longitude.
   
   Parameters:
       lon: array-like, longitude values
       slip: array-like, slip values
       taper_start_lon: float, longitude where taper begins
   
   Returns:
       array-like: tapered slip values
   """
   slip_tapered = np.copy(slip)
   taper_mask = lon > taper_start_lon
   taper_factor = 0.5 * (1 + np.cos(np.pi * (lon[taper_mask] - taper_start_lon) / (lon.max() - taper_start_lon)))
   slip_tapered[taper_mask] *= taper_factor
   return slip_tapered

def filter_by_distance_to_trench(lon, lat, trench_lon, trench_lat, max_distance_km=50):
   """
   Filters slip points within maximum distance from trench.
   
   Parameters:
       lon, lat: array-like, coordinates of slip points
       trench_lon, trench_lat: array-like, trench coordinates
       max_distance_km: float, maximum allowed distance from trench
   
   Returns:
       array-like: boolean mask for points within distance threshold
   """
   trench_tree = cKDTree(np.column_stack([trench_lon, trench_lat]))
   distances, _ = trench_tree.query(np.column_stack([lon, lat]))
   return distances <= max_distance_km

# Directory setup and file paths
csv_dir = "/Users/javieraalvarezvargas/Desktop/modelos/1730/csv_final"
output_dir = "/Users/javieraalvarezvargas/Desktop/modelos/1730/filtrados"

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
   os.makedirs(output_dir)

# Configure map parameters
region = [-76, -69, -38, -27]  # Geographic bounds
projection = "M7c"  # Mercator projection
paleta = "gray"  # Grayscale topography

# Process topography data
pygmt.grdcut(grid="@earth_relief_01m", region=region, outgrid="topo.grd")
pygmt.grdgradient(grid="topo.grd", outgrid="int.grd", azimuth=45, normalize="t0.3")
pygmt.grdfilter(grid="topo.grd", outgrid="topo_smooth.grd", filter="g10", distance="1")

# Load trench data
trench_file = "trench-chile"
trench_data = pd.read_csv(trench_file, delim_whitespace=True, header=None)
trench_lon = trench_data.iloc[:, 0].values
trench_lat = trench_data.iloc[:, 1].values

# Process each slip distribution file
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

for csv_file in csv_files:
   # Load slip data
   csv_file_path = os.path.join(csv_dir, csv_file)
   slip_data = pd.read_csv(csv_file_path)
   lon = slip_data.iloc[:, 0].values
   lat = slip_data.iloc[:, 1].values
   slip = slip_data.iloc[:, 2].values

   # Apply spatial filtering
   slip_tapered = apply_taper(lon, slip, taper_start_lon=-72)
   mask = filter_by_distance_to_trench(lon, lat, trench_lon, trench_lat, max_distance_km=50)
   
   # Extract filtered data
   lon_filtered = lon[mask]
   lat_filtered = lat[mask]
   slip_filtered = slip_tapered[mask]

   # Save filtered data
   filtered_csv_file = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}_filtered.csv")
   filtered_data = pd.DataFrame({
       'Longitude': lon_filtered,
       'Latitude': lat_filtered,
       'Slip': slip_filtered
   })
   filtered_data.to_csv(filtered_csv_file, index=False)
   print(f"Filtered CSV saved: {filtered_csv_file}")

   # Create visualization
   fig = pygmt.Figure()
   
   # Base map configuration
   fig.basemap(region=region, projection=projection, frame=["af"])
   fig.grdimage(grid="topo_smooth.grd", shading="int.grd", cmap=paleta)
   fig.coast(region=region, projection=projection, shorelines="0.3p,black", 
            water="gray", resolution="h")
   
   # Plot trench line
   fig.plot(data=trench_file, style="f0.5i/0.1i+r+t+o1", pen="1.0p,black", color="white")
   
   # Configure and plot slip distribution
   pygmt.makecpt(cmap="hot", series=[slip_filtered.min(), 25], reverse=True, continuous=True)
   fig.plot(x=lon_filtered, y=lat_filtered, style="s0.3c", color=slip_filtered, 
           cmap=True, pen="black")
   
   # Add colorbar
   fig.colorbar(position="JBC+o0c/1c", frame=["x+lSlip (m)"])
   
   # Save and display figure
   output_file = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}_tapered_filtered.png")
   fig.savefig(output_file)
   print(f"Figure saved: {output_file}")
   fig.show()



# %%
