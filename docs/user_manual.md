# Vocal Geometry App: User Manual (Phase 2)

Welcome to the Vocal Geometry App. This manual explains how to navigate the updated interactive application.

## Getting Started
Launch the app. Use the sidebar to read about the validation status and educational disclaimers. 

## Tab 1: Interactive Muscle Explorer
This is the unified main interface where you can change inputs and see outputs in real time.
* **Left Column (Controls)**: Select Biological Sex. Use the **Quick Presets** to jump to standard configurations (e.g., Neutral, CT-dominant). Adjust the normalized activation ($0.0$ to $1.0$) of the Cricothyroid (CT), Thyroarytenoid (TA), and Lateral Cricoarytenoid (LCA) muscles using sliders. Read the physiological tendencies box.
* **Right Column (Results & 3D)**: 
  * The **3D Visualization** is an anatomically inspired parametric surface. It represents the left and right vocal folds. The dark red core represents the *Body* layer, and the orange medial layer represents the *Cover*. The teal dashed line is the Nodal Point. The gap closes as LCA increases (pedagogical visualization of adduction). 
  * Below the 3D plot, compact tables display the calculated Geometry and Mechanics values.

## Tab 2: Compare States
Compare two distinct muscle activation profiles side-by-side using the strict mathematical engine.
* Use the "Use current Explorer state as State A/B" buttons to easily copy your settings from Tab 1.
* The bar charts visually compare the geometry between State A and State B.
* The Delta chart shows the percentage change (increase or decrease).
* The data table provides exact numerical differences and percentage shifts.

## Tab 3: Activation Maps
Explore the entire parameter space by sweeping two muscles while keeping one fixed.
* **Basic Mode (Default)**: Select an Output Variable, a Sex, the Muscle Plane (e.g., aCT vs aTA), and fix the third muscle. By default, it shows a 2D Heatmap.
* **Advanced Mode**: Expand the settings to change Grid Resolution or switch the Plot Type to Contour or 3D Surface.
* **Export**: Click the "Download Map Data as CSV" button to export the raw computed grid for external analysis.

## Tab 4: Learning Mode
Contains pedagogical FAQs, references to the foundational manuscripts, and a mini-quiz.

## Tab 5: Validation & Documentation
Review the mathematical equations, limitations, and check the automated test status.
