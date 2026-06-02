# Vocal Geometry App

A scientific, interactive web application simulating the geometry, mechanics, and pedagogical phonation kinematics of the human vocal folds. The app implements the low-dimensional body-cover model (Titze & Story, 2002) to visualize how muscle activations (CT, TA, LCA) alter laryngeal structures.

## Features
- **Strict Anatomico-Mechanical 3D Representation:** Faithfully maps the Body (TA core) and Cover (Upper/Lower masses separated by Nodal Point Zn) to a functional 3D mesh.
- **Pedagogical Phonation Animation:** Simulates the mucosal wave and glottal gap dynamics with asymmetric open/close phases.
- **Glottal Cycle Analysis:** Outputs derived $A_g(t)$ (Glottal Area) and a sigmoidal $C(t)$ (EGG-like relative contact function), alongside contact proxy $A_c(t)$.
- **Compare Geometries:** Analyze shifts in morphological parameters and glottal performance between different muscle states using both static overlay and dynamic separate views.

## Installation

```bash
git clone <repository_url>
cd vocal_geometry_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

Launch the Streamlit interface:
```bash
python -m streamlit run app.py
```

## Validation

The underlying mathematical engine is strictly validated against the original manuscript Tables 5 and 6 from Titze (2002). To run the test suite and reproduce the tables:

```bash
# Run unit tests
pytest

# Reproduce tables
python validation/reproduce_table_5.py
python validation/reproduce_table_6.py

# Run all validations
python validation/run_all_validation.py
```

---
*Educational use only. Not intended for clinical diagnosis.*
*Developed by Calvache, 2026*
