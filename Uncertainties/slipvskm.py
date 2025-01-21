"""
Slip Pattern Analysis for Historical Seismic Events (1730, 1906, 1985)
Javiera Álvarez, 2024

This script analyzes and visualizes slip patterns along a constant latitude (~33°S) 
for three major historical earthquakes in Chile. It performs:

1. Data processing of slip distribution models
2. Distance calculations from trench using geodesic methods
3. Individual slip pattern visualization with key coastal locations
4. Comparative analysis of normalized and absolute slip values

Key Features:
- Filters data points near -33° latitude
- Calculates distances from trench using geodesic measurements
- Displays coastal city locations as vertical markers
- Generates both normalized and absolute slip comparisons

Dependencies:
   - pandas: data handling
   - numpy: numerical operations
   - matplotlib: visualization
   - geopy: geodesic distance calculations
"""

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic

# Load slip distribution models for each event
df_1730 = pd.read_csv('/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/filtrados72/slip_845_aumentado_filtered.csv', header=None, names=['Lon', 'Lat', 'Slip'])
df_1906 = pd.read_csv('/Users/javieraalvarezvargas/Desktop/modelos/1906/filtrados70_2/slip_367_filtered.csv', header=None, names=['Lon', 'Lat', 'Slip'])
df_1985 = pd.read_csv('/Users/javieraalvarezvargas/Desktop/modelos/1985/slip_1985_2/filtrado2/slip_1239_filtered.csv', header=None, names=['Lon', 'Lat', 'Slip'])

# Define coastal location coordinates for each event
deform_1730 = [
    (-71.6281, -33.6358, "Santo Domingo"),
    (-71.4145, -33.4448, "Estero Yali"),
    (-71.6272, -33.0393, "Valparaíso")
]

deform_1906 = [
    (-71.550, -33.921, "Viña del Mar"), (-71.675, -33.364, "Algarrobo"),
    (-71.604, -33.548, "Cartagena"), (-71.875, -33.963, "Matanzas")
]

deform_1985 = [
    (-71.627250, -33.039320, "Valparaíso"), (-71.607610, -33.553840, "Cartagena"),
    (-71.686000, -33.183300, "Quintay"), (-71.692800, -33.391100, "Algarrobo"),
    (-71.873300, -33.960700, "Matanzas")
]

# Data processing function for slip distribution analysis
def process_slip_data(df, label, deform_points=None):
    # Filter points near -33° latitude with tolerance
    lat_target = -33
    df_filtered = df[np.isclose(df['Lat'], lat_target, atol=0.05)].sort_values(by='Lon')
    
    # Set reference point for distance calculations
    reference_point = df_filtered.iloc[0]
    ref_lat = reference_point['Lat']
    ref_lon = reference_point['Lon']
    
    # Calculate distances from reference point
    df_filtered['Distance_km'] = df_filtered.apply(lambda row: geodesic((ref_lat, ref_lon), (row['Lat'], row['Lon'])).kilometers, axis=1)
    return df_filtered

# Visualization function for individual events
def plot_slip_pattern(df_filtered, label, color, deform_points, xlim, ylim):
    plt.figure(figsize=(10, 6))
    plt.plot(df_filtered['Distance_km'], df_filtered['Slip'], label=f'Slip Pattern {label}', color=color, linewidth=2.5)
    
    # Add location markers if provided
    if deform_points:
        for lon, lat, city_name in deform_points:
            deform_distance = geodesic((df_filtered.iloc[0]['Lat'], df_filtered.iloc[0]['Lon']), (lat, lon)).kilometers
            plt.axvline(x=deform_distance, color='gray', linestyle='--', linewidth=1)
            plt.text(deform_distance, 0.5, city_name, rotation=90, verticalalignment='bottom', 
                     horizontalalignment='center', fontsize=10, color='black')
            
    plt.xlabel('Distance from Trench, starting point at -33° Lat (km)')
    plt.ylabel('Slip (m)')
    plt.title(f'Slip Pattern for {label} Along Distance from Starting Point')
    plt.grid(True)
    plt.xlim(*xlim)
    plt.ylim(*ylim)
    plt.legend()
    plt.savefig(f'slip_pattern_{label}.png', dpi=300, bbox_inches='tight')

    plt.show()

# Process and plot individual events

df_1730_filtered = process_slip_data(df_1730, "1730")
plot_slip_pattern(df_1730_filtered, "1730", color='tab:red', deform_points=deform_1730, xlim=(0, 190), ylim=(0, 25))

df_1906_filtered = process_slip_data(df_1906, "1906")
plot_slip_pattern(df_1906_filtered, "1906", color='tab:orange', deform_points=deform_1906, xlim=(0, 200), ylim=(0, 4))

df_1985_filtered = process_slip_data(df_1985, "1985")
plot_slip_pattern(df_1985_filtered, "1985", color='tab:green', deform_points=deform_1985, xlim=(0, 200), ylim=(0, 4))

# Calculate maximum slip values and normalize
max_slip_1730 = df_1730_filtered['Slip'].max()
max_slip_1906 = df_1906_filtered['Slip'].max()
max_slip_1985 = df_1985_filtered['Slip'].max()

# Create normalized slip columns
df_1730_filtered['Normalized_Slip'] = df_1730_filtered['Slip'] / max_slip_1730
df_1906_filtered['Normalized_Slip'] = df_1906_filtered['Slip'] / max_slip_1906
df_1985_filtered['Normalized_Slip'] = df_1985_filtered['Slip'] / max_slip_1985

# Generate comparative plots
# Absolute slip comparison
plt.figure(figsize=(10, 6))
plt.plot(df_1730_filtered['Distance_km'], df_1730_filtered['Slip'], color='tab:red',linewidth=2.5, label='Slip Pattern 1730')
plt.plot(df_1906_filtered['Distance_km'], df_1906_filtered['Slip'], color='tab:orange', linewidth=2.5, label='Slip Pattern 1906')
plt.plot(df_1985_filtered['Distance_km'], df_1985_filtered['Slip'], color='tab:green', linewidth=2.5, label='Slip Pattern 1985')
plt.xlabel('Distance from Trench, starting point at -33° Lat (km)')
plt.ylabel('Slip (m)')
plt.xlim(0, 180)
plt.ylim(0, 25)
plt.title('Comparison of Slip Patterns (1730, 1906, and 1985)')
plt.grid(True)
plt.legend()
plt.savefig('events_comparison_total.png', dpi=300, bbox_inches='tight')
plt.show()

# Normalized slip comparison
plt.figure(figsize=(10, 6))
plt.plot(df_1730_filtered['Distance_km'], df_1730_filtered['Normalized_Slip'], color='tab:red', linestyle='--', linewidth=2.5, label='Normalized Slip Pattern 1730')
plt.plot(df_1906_filtered['Distance_km'], df_1906_filtered['Normalized_Slip'], color='tab:orange', linestyle='--', linewidth=2.5, label='Normalized Slip Pattern 1906')
plt.plot(df_1985_filtered['Distance_km'], df_1985_filtered['Normalized_Slip'], color='tab:green', linestyle='--', linewidth=2.5, label='Normalized Slip Pattern 1985')
plt.xlabel('Distance from Trench, starting point at -33° Lat (km)')
plt.ylabel('Normalized Slip (relative to max)')
plt.xlim(0, 200)
plt.ylim(0, 1.1)  # Límite hasta 1.1 para que se vea mejor
plt.title('Comparison of Normalized Slip Patterns (1730, 1906, and 1985)')
plt.grid(True)
plt.legend()
plt.savefig('events_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
