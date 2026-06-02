# Model Equations & Assumptions

This document summarizes the mathematical rules implemented in the Vocal Geometry App, based on the body-cover low-dimensional model (Titze & Story, 2002).

## A. Body-Cover Framework & Anatomy Mapping
The 3-mass model geometry is mapped to 3D space as follows:
- **$L$ (Length)**: Anterior-Posterior dimension (Y-axis).
- **$T$ (Thickness)**: Inferior-Superior vertical dimension (Z-axis).
- **$D_b, D_c$ (Depths)**: Medial-Lateral lateral depth (X-axis).
- **$Z_n$ (Nodal Point)**: Separates the upper/lower cover along the vertical Z-axis.

## B. Geometric Equations
All geometric changes are driven by longitudinal strain (elongation, $\epsilon$):
$$ \epsilon = G(R \cdot aCT - aTA) - H \cdot aLCA $$

Where $aCT, aTA, aLCA \in [0, 1]$ are muscle activations, and $G=0.2, R=3.0, H=0.2$.

- **Length**: $L = L_0 (1 + \epsilon)$
- **Thickness**: $T = T_0 / (1 + 0.8\epsilon)$
- **Body Depth**: $D_b = \frac{aTA \cdot D_{mus} + 0.5 \cdot D_{lig}}{1 + 0.2\epsilon}$
- **Cover Depth**: $D_c = \frac{D_{muc} + 0.5 \cdot D_{lig}}{1 + 0.2\epsilon}$
- **Nodal Point**: $Z_n = (1 + aTA)^{T/3}$

## C. Glottal Area & Contact Functions
These functions are pedagogical derivations from the time-varying animated medial gap $\text{gap}(y,z,t)$:

- **Glottal Area Function**:
  $$ A_g(t) = \int \max\left(\min_z(\text{gap}(y,z,t)),\,0\right)\; dy $$

- **EGG-like Contact Function** (logistic approach):
  $$ C(t) = \text{norm} \int \frac{1}{1 + \exp\left(\frac{\min_z(\text{gap}(y,z,t)) - \delta_\text{egg}}{s}\right)}\; dy $$

- **Contact Area Proxy** (threshold):
  $$ A_c(t) = \int \max\left(\delta_c - \min_z(\text{gap}(y,z,t)),\,0\right)\; dy $$

*Note: These curves are pedagogical proxies. They are not equivalent to high-speed imaging, electroglottography, finite-element contact pressure, or patient-specific phonation simulation.*

## D. References
- Story BH, Titze IR. Voice simulation with a body-cover model of the vocal folds. JASA. 1995;97:1249–1260.
- Titze IR, Story BH. Rules for controlling low-dimensional vocal fold models with muscle activation. JASA. 2002;112:1064–1076.
- Zhang Z. Mechanics of human voice production and control. JASA. 2016;140:2614–2635.
- Zhang Z. Effect of vocal fold stiffness on voice production in a three-dimensional body-cover phonation model. JASA. 2017;142:2311–2321.
- Zhang Z. Vocal fold contact pressure in a three-dimensional body-cover phonation model. JASA. 2019;146:256–265.
- Smith SL, Titze IR. Vocal fold contact patterns based on normal modes of vibration. Journal of Biomechanics. 2018;73:177–184.
- Miri AK. Mechanical characterization of vocal fold tissue: A review study. Journal of Voice. 2014;28:657–667.
- Vahabzadeh-Hagh AM, Zhang Z, Chhetri DK. Hirano’s cover-body model and its unique laryngeal postures revisited. Laryngoscope. 2018;128:1412–1418.
- Galindo GE et al. Modeling the pathophysiology of phonotraumatic vocal hyperfunction with a triangular glottal model. JSLHR. 2017;60:2452–2471.
- Alzamendi GA et al. Triangular body-cover model of the vocal folds with coordinated activation of the five intrinsic laryngeal muscles. JASA. 2022;151:17–30.
- Herbst CT. Electroglottography – An Update. Journal of Voice. 2020.
- Kankare E, et al. Electroglottographic contact quotient in different phonation types. Journal of Voice. 2012.

---
*Developed by Calvache, 2026*
