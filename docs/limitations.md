# Application Limitations and Disclaimers

The **Vocal Geometry App** is designed specifically as a pedagogical and conceptual visualization tool. It simplifies highly complex biological phenomena into a small number of mathematical rules. Users must be aware of the following fundamental limitations:

## 1. Not a Clinical Tool
> **WARNING:** This application does not reconstruct patient-specific vocal fold geometry and is not intended for clinical diagnosis, surgery planning, or therapeutic prescription. The app does NOT estimate real vocal fold geometry from acoustic signals or imaging.

## 2. Low-Dimensional Approximation
Real vocal folds are continuous 3D viscoelastic tissues. This application relies on a "low-dimensional" body-cover model, which reduces the vocal fold to two or three discrete masses connected by springs. 
* **Geometry Visualization:** The 3D visualization is an *anatomically inspired educational schematic*. It represents the mathematical lengths and thicknesses derived from the model output, but it is **NOT** a patient-specific anatomical reconstruction. The organic shape and glottal gap modulations are purely pedagogical visual aids.
* **Volume:** The assumption of volume conservation during elongation is an approximation.

## 3. Lack of Aerodynamics, Acoustics, & Diagnosis
This tool computes **static** geometries and resting mechanical parameters resulting from muscle activation. It **does not** simulate:
* Glottal airflow.
* Vocal fold collision or tissue vibration.
* The acoustic output (voice).
* Therefore, the app **cannot directly predict fundamental frequency ($F_0$), vocal quality, dysphonia, or the presence of pathology.** It only visualizes the intermediate geometric and mechanical variables that precede acoustic modeling.

## 4. Simplified Muscular Architecture
The model relies on three primary intrinsic muscles (CT, TA, LCA) using normalized activation values ($0.0$ to $1.0$). Real phonation involves complex, synergistic activation of many muscles (e.g., PCA, IA) and intricate geometric changes in the cartilages (e.g., arytenoid rotation/gliding) which are highly abstracted here.

## Summary
Use this tool to build intuition about the basic rules of vocal fold biomechanics: how the CT stretches the folds, how the TA thickens the body, and how the LCA contributes to adduction and geometric adjustment. Do not use it to promise changes in real vocal output or to diagnose medical conditions.
