# VocalFold Explorer

**Interactive body-cover model for vocal fold geometry, mechanics, and glottal-cycle visualization.**

**Live application:**  
https://vocalfold-explorer.streamlit.app/

**Archived software release:**  
https://doi.org/10.5281/zenodo.20518555

---

## Overview

**VocalFold Explorer** is an interactive educational web application that implements a low-dimensional body-cover model of the human vocal folds. The app allows users to explore how selected intrinsic laryngeal muscle activation parameters influence vocal fold geometry, mechanical properties, body-cover visualization, and pedagogical glottal-cycle outputs.

The application is designed for educational, research-training, and computational visualization purposes in voice science, vocology, speech-language pathology, and vocal fold biomechanics.

---

## Main Features

- **3D body-cover visualization** of the vocal folds.
- **Muscle activation exploration** through cricothyroid, thyroarytenoid, and lateral cricoarytenoid activation parameters.
- **Interactive geometry inspection** of length, thickness, body depth, cover depth, and nodal point.
- **Pedagogical glottal-cycle visualization** based on simulated medial gap dynamics.
- **Glottal Area Function** `Ag(t)`.
- **Contact Area Proxy** `Ac(t)`.
- **Contact Length** `Lc(t)`.
- **Approximate Contact Quotient** `CoQ`.
- **A/B comparison** of two activation states.
- **Activation heatmaps** for geometry, glottal-cycle outputs, mechanical proxies, and advanced model parameters.
- **Equations and references** integrated into the app.
- **Numerical verification scripts** for reproducing reference model tables.

---

## Important Scope Limitation

VocalFold Explorer is an **educational low-dimensional computational model**.

It is **not**:

- a clinical diagnostic tool;
- a patient-specific simulator;
- a finite element model;
- a high-speed videoendoscopy tool;
- an electroglottography system;
- an acoustic synthesizer;
- a predictor of F0, pitch, voice quality, pathology, or clinical status.

The glottal-cycle curves are displayed over **normalized pedagogical cycles**, not calibrated physical time. Therefore, the application does **not** estimate vocal frequency, acoustic output, or patient-specific phonatory behavior.

---

## Core Model-Derived Outputs

The app currently focuses on the following pedagogical outputs.

### Glottal Area Function

`Ag(t)` represents the estimated glottal opening area derived from the simulated medial gap:

```text
Ag(t) = ∫ max(gap(y,t), 0) dy
```

### Contact Length

`Lc(t)` estimates the anterior-posterior length over which the simulated medial gap reaches a contact threshold:

```text
Lc(t) = ∫ I(gap(y,t) ≤ δcontact) dy
```

### Contact Area Proxy

`Ac(t)` is a geometric proxy derived from contact length and an effective mucosal contact height:

```text
Ac(t) = Lc(t) · hcontact
```

It is not tissue contact pressure and should not be interpreted as a clinical contact measurement.

### Approximate Contact Quotient

`CoQ` represents the proportion of the normalized pedagogical cycle during which relevant simulated contact is present:

```text
CoQ = Tcontact / Tcycle
```

---

## Repository Structure

```text
vocalfold-explorer/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── CITATION.cff
├── .zenodo.json
├── .streamlit/
│   └── config.toml
├── vocal_geometry/
│   ├── model.py
│   ├── plotting.py
│   ├── constants.py
│   └── validation.py
├── validation/
│   ├── reproduce_table_5.py
│   ├── reproduce_table_6.py
│   └── run_all_validation.py
├── tests/
└── docs/
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/CarlosCalvache/vocalfold-explorer.git
cd vocalfold-explorer
```

Create and activate a virtual environment.

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Running the Application Locally

Launch the Streamlit app:

```bash
python -m streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

---

## Online Use

The app is publicly available at:

https://vocalfold-explorer.streamlit.app/

No local installation is required to use the online version.

---

## Numerical Verification

The implementation includes scripts to verify the numerical consistency of the model implementation with the reference body-cover model tables used in development.

Run the unit tests:

```bash
pytest
```

Reproduce reference tables:

```bash
python validation/reproduce_table_5.py
python validation/reproduce_table_6.py
```

Run all validation checks:

```bash
python validation/run_all_validation.py
```

Numerical verification should not be interpreted as clinical validation. It confirms consistency of the implemented computational model, not diagnostic or patient-specific accuracy.

---

## Deployment

The app is designed for deployment through **Streamlit Community Cloud**.

Deployment configuration:

```text
Repository: CarlosCalvache/vocalfold-explorer
Branch: main
Main file path: app.py
```

The Streamlit theme is configured in:

```text
.streamlit/config.toml
```

---

## Citation

If you use VocalFold Explorer in teaching, research, software development, or academic work, please cite the archived software release:

```text
Calvache, C. (2026). VocalFold Explorer (v1.0.2) [Software]. Zenodo. https://doi.org/10.5281/zenodo.20518555
```

Version DOI:

```text
https://doi.org/10.5281/zenodo.20518555
```

Concept DOI:

```text
https://doi.org/10.5281/zenodo.20518554
```

---

## Software Archive

- **GitHub repository:** https://github.com/CarlosCalvache/vocalfold-explorer
- **Live app:** https://vocalfold-explorer.streamlit.app/
- **Zenodo archived release:** https://doi.org/10.5281/zenodo.20518555
- **Concept DOI:** https://doi.org/10.5281/zenodo.20518554

---

## License

This project is released under the MIT License.

See the `LICENSE` file for details.

---

## Author

**Carlos Calvache**  
Vocology Center  
ORCID: https://orcid.org/0000-0002-5403-1852

---

## Disclaimer

VocalFold Explorer is provided for educational and research-training purposes only. It should not be used for clinical diagnosis, therapeutic decision-making, patient-specific prediction, or acoustic estimation.
