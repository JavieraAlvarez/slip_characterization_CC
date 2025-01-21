"""
Slab2.0 Depth Analysis for Historical Seismic Events
Javiera Álvarez 2024

This script analyzes the spatial distribution of slip in relation to slab depth
for three historical seismic events (1730, 1906, and 1985). It performs the
following operations:

1. Loads Slab2.0 depth data and slip distribution models
2. Interpolates depth values at slip centroid locations
3. Generates 3D visualizations showing relationship between:
   - Spatial location (longitude, latitude)
   - Interpolated depth
   - Slip magnitude

Dependencies:
    - numpy: numerical operations
    - scipy: interpolation functions
    - pandas: data handling
    - matplotlib: 3D visualization
"""
#%%
import numpy as np
from scipy.interpolate import griddata
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load Slab2.0 depth data and adjust longitude to match slip coordinates
datos_xyz = np.loadtxt('/Users/javieraalvarezvargas/Downloads/sam_slab2_dep_02.23.18.xyz', delimiter=',')
lon_xyz = datos_xyz[:, 0] - 360  # Ajuste de longitud
lat_xyz = datos_xyz[:, 1]
depth_xyz = datos_xyz[:, 2]


# Load slip distribution models for each event
slip_1730df = pd.read_csv('/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/filtrados72/slip_845_aumentado_filtered.csv', header=None)
slip_1906df = pd.read_csv('/Users/javieraalvarezvargas/Desktop/modelos/1906/filtrados70_2/slip_367_filtered.csv', header=None)
slip_1985df = pd.read_csv('/Users/javieraalvarezvargas/Desktop/modelos/1985/slip_1985_2/filtrado2/slip_1239_filtered.csv', header=None)

lon_1730slip = slip_1730df[0].values  # Lon
lat_1730slip = slip_1730df[1].values  # Lat

lon_1906slip = slip_1906df[0].values  # 
lat_1906slip = slip_1906df[1].values  # 

lon_1985slip = slip_1985df[0].values  # 
lat_1985slip = slip_1985df[1].values  # 

# Interpolate depth values at slip centroids for each event
depth_interpolada = griddata(
    (lon_xyz, lat_xyz), depth_xyz, (lon_1730slip, lat_1730slip), method='linear'
)

depth_interpolada2 = griddata(
    (lon_xyz, lat_xyz), depth_xyz, (lon_1906slip, lat_1906slip), method='linear'
)

depth_interpolada3 = griddata(
    (lon_xyz, lat_xyz), depth_xyz, (lon_1985slip, lat_1985slip), method='linear'
)
# Display interpolated depth results
print("Profundidades interpoladas en los puntos de Slip:", depth_interpolada)

# Extract slip values for each event
slip_values_1730= slip_1730df[2].values  # Slip values
slip_values_1906= slip_1906df[2].values  
slip_values_1985= slip_1985df[2].values  


# Visualization for 1730 event
fig1 = plt.figure(figsize=(12, 8))
ax = fig1.add_subplot(111, projection='3d')

scatter = ax.scatter(lon_1730slip, lat_1730slip, depth_interpolada,  # - depth
                     c=slip_values_1730, cmap='jet', marker='o', alpha=0.7)

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Depth (km)')
ax.set_title('1730 Event in terms of Depth')
cbar = plt.colorbar(scatter, ax=ax, label='Slip (m)')
#plt.savefig('event_1730_depth.png', dpi=600, bbox_inches='tight')

plt.show()


# Visualization for 1906 event
fig2 = plt.figure(figsize=(12, 8))
ax = fig2.add_subplot(111, projection='3d')
scatter = ax.scatter(lon_1906slip, lat_1906slip, depth_interpolada2,  
                     c=slip_values_1906, cmap='jet', marker='o', alpha=0.7)

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Depth (km)')
ax.set_title('1906 Event in terms of Depth')

cbar = plt.colorbar(scatter, ax=ax, label='Slip (m)')
#plt.savefig('event_1906_depth.png', dpi=1000, bbox_inches='tight')

plt.show()


# Visualization for 1985 event
fig3 = plt.figure(figsize=(12, 8))
ax = fig3.add_subplot(111, projection='3d')
scatter = ax.scatter(lon_1985slip, lat_1985slip, depth_interpolada3,  
                     c=slip_values_1985, cmap='jet', marker='o', alpha=0.7)

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Depth (km)')
ax.set_title('1985 Event in terms of Depth')
# colobar
cbar = plt.colorbar(scatter, ax=ax, label='Slip (m)')
#plt.savefig('event_1985_depth.png', dpi=600, bbox_inches='tight')

plt.show()


# %%
