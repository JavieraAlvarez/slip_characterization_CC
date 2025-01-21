# Megathrust Earthquake Characterization in Central Chile

This repository contains the code and data for analyzing historical earthquakes along the central Chile Gap
using the Stochastic Logic Tree Approach. The project focuses on exploring historical earthquakes and characterizing
seismic events from 1730, 1906, and 1985.

## Project Structure

The project is organized into three main folders:

### 1. LT-Stochastic/
Contains codes for implementing the Logic Tree (LT) stochastic approach, including:
- `run_comcot.sh` - Shell script for running COMCOT simulations
- `fault_creater_dom_lay.py` - Fault creation module
- `comcotctl_format.py` - COMCOT control file formatter
- `tsunami_model.py` - Tsunami modeling implementation
- `modfallas.py` - Fault modification utilities
- `modokada.py` and `modokada.pyc` - Okada model implementation
- `modrestricciones.py` - Constraint implementation
- Additional auxiliary functions in `aux_functions/`

### 2. constrain/
Implementation of constraint processes, including:
- `restringe_modelo_coincidencia.py` - Model coincidence constraints
- `restringe_modelo_interpolongitud.py` - Interpolation constraints
- `restringe_modelo_rapido.py` - Rapid model constraints
- `restringe_tsunami_baja_resolucion.py` - Tsunami resolution constraints
- `transforma_deformacion_2xyz.py` - Deformation transformation
- `transforma_slip_grilla2xyz.py` - Slip grid transformation
- `transformaepsapng.sh` - EPS to PNG conversion

### 3. uncertainties/
Contains codes for uncertainty analysis:
- `depthslabslip.py` - Depth analysis for slip
- `slipvskm.py` - Slip vs. distance analysis
- `incertidumbres1730.ipynb` - Jupyter notebook for 1730 event analysis
- `incertidumbres1906.ipynb` - Jupyter notebook for 1906 event analysis
- `subfallas.py` - Subfault analysis
- `paraview1.py` - Visualization utilities
- Additional configuration files and shell scripts

## Installation

```bash
# Clone the repository
git clone [repository-url]

# Install required dependencies
pip install -r requirements.txt
```

## Usage

Each module can be run independently depending on the analysis needed:

1. For stochastic model generation:
```bash
cd LT-Stochastic
python fault_creater_dom_lay.py
```

2. For constraint application:
```bash
cd constrain
python restringe_modelo_rapido.py
```

3. For uncertainty analysis:
```bash
cd uncertainties
jupyter notebook incertidumbres1730.ipynb
```

## Methodology

The project implements a Logic Tree approach for analyzing historical earthquakes, combining:
- Stochastic slip distribution generation
- Historical data constraints
- Uncertainty quantification
- Tsunami modeling validation

## Data Sources

- Historical earthquake records from central Chile (32°-34°S)
- Vertical displacement and tsunami inundation data
- Historical documentation from 1730, 1906, and 1985 events

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Authors

- Javiera Álvarez
- Ignacia Calisto
- Additional contributors listed in the manuscript

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
