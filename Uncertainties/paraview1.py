"""
Slip Distribution VTK File Generator
Javiera Álvarez, 2024

This script converts slip distribution data from CSV format to VTK format
for 3D visualization in ParaView. It processes earthquake slip models by:

1. Loading slip distribution data (longitude, latitude, slip)
2. Converting to point cloud format
3. Creating PyVista grid structure
4. Exporting to VTK format for ParaView visualization

Dependencies:
   - pandas: data handling
   - pyvista: VTK file generation
   - numpy: numerical operations
"""

#%%
import pandas as pd
import pyvista as pv
import numpy as np

# Load slip distribution model from CSV
csv_file = '/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/filtrados72/slip_845_aumentado_filtered.csv'
slip_data = pd.read_csv(csv_file, delimiter=",", header=None)

# Extract spatial coordinates and slip values
lon = slip_data.iloc[:, 0].values  # Longitude values
lat = slip_data.iloc[:, 1].values  # Latitude values
slip = slip_data.iloc[:, 2].values  # Slip magnitudes

# Generate point cloud from spatial and slip data
points = np.column_stack((lon, lat, slip))

# Create PyVista grid structure
grid = pv.PolyData(points)

# Add slip values as grid property
grid['slip'] = slip

# Export to VTK format
vtk_output_file = 'slip_model_845_filtered_final.vtk'
grid.save(vtk_output_file)

print(f'VTK file saved as {vtk_output_file}. Ready for ParaView visualization.')
# %%
