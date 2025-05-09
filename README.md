# Lux Resonans: A Deep Dive into Simulated Light Wave Phenomena

**Lux Resonans** is an interactive web application meticulously crafted to simulate and elucidate the fundamental principles of light wave optics, specifically **single-slit diffraction** and **double-slit interference (incorporating single-slit diffraction effects)**. This document details the underlying physics, the computational engine, and the software architecture that powers the simulation.

## I. The Physical Phenomena Modeled

The simulation visualizes the intensity distribution of light on a distant screen after passing through one or two narrow slits. This is primarily based on Huygens' principle and the principle of superposition, modeled under the Fraunhofer (far-field) diffraction regime.

### A. Single-Slit Diffraction

When a monochromatic plane wave of light encounters a single narrow slit, it diffracts, meaning it spreads out. The resulting pattern on a distant screen is not a simple sharp shadow but a characteristic diffraction pattern consisting of a bright central maximum, flanked by alternating dark minima and progressively fainter secondary maxima.

**1. Conceptual Basis:**
According to Huygens' principle, every point across the width of the slit can be considered as a source of secondary spherical wavelets. These wavelets interfere with each other.
*   **Central Maximum:** At the center of the pattern (directly opposite the slit), all wavelets arrive in phase (or with path differences that are multiples of the wavelength, but primarily in phase for the direct path), leading to constructive interference and high intensity.
*   **Minima (Dark Fringes):** Consider a point on the screen such that the path difference between a wavelet from one edge of the slit and a wavelet from the center of the slit is λ/2. For every wavelet in the top half of the slit, there's a corresponding wavelet in the bottom half that is λ/2 out of phase, leading to complete destructive interference. This occurs when:
    `a sin(θ) = mλ`
    where:
    *   `a` is the width of the slit.
    *   `θ` is the angle of diffraction relative to the normal to the slit.
    *   `λ` is the wavelength of light.
    *   `m = ±1, ±2, ±3, ...` is the order of the minimum (m=0 is the central maximum).

**2. Mathematical Formulation for Intensity:**
The relative intensity `I(θ)` of the diffraction pattern at an angle `θ` is given by:
`I(θ) = I₀ * (sin(β)/β)²`
where:
*   `I₀` is the intensity at the central maximum (θ=0).
*   `β = (π * a * sin(θ)) / λ`
The term `(sin(β)/β)²` is known as the "sinc squared" function. As `β` approaches 0 (i.e., `θ` approaches 0), the limit of `sin(β)/β` is 1, so `I(0) = I₀`.

### B. Double-Slit Interference (Young's Experiment)

When monochromatic light passes through two closely spaced, narrow slits, the waves emerging from each slit interfere.

**1. Conceptual Basis:**
Each slit acts as a coherent source of light (assuming the incident light is coherent and the slits are narrow enough).
*   **Constructive Interference (Bright Fringes):** Occurs at points on the screen where the path difference from the two slits is an integer multiple of the wavelength.
    `d sin(θ) = mλ`
    where `d` is the distance between the centers of the two slits, and `m = 0, ±1, ±2, ...` is the order of the bright fringe.
*   **Destructive Interference (Dark Fringes):** Occurs where the path difference is a half-integer multiple of the wavelength.
    `d sin(θ) = (m + 1/2)λ`

**2. Mathematical Formulation for Interference (Ideal Point Sources):**
If the slits were ideal point sources, the intensity would vary as:
`I_interference(θ) = I_max * cos²(α)`
where:
*   `α = (π * d * sin(θ)) / λ`

### C. Combined Double-Slit Pattern: Interference Modulated by Diffraction

In reality, each of the two slits has a finite width `a`. Therefore, the light from each slit creates its own single-slit diffraction pattern. These two diffraction patterns then interfere. The result is that the double-slit interference pattern is "modulated" by the single-slit diffraction envelope.

**1. Conceptual Basis:**
The observed pattern is the product of the interference effect from the two slits and the diffraction effect from the width of each individual slit. The `cos²(α)` term describes the rapidly varying interference fringes, while the `(sin(β)/β)²` term describes the slower-varying diffraction envelope that dictates the overall brightness of these fringes.
*   **Missing Orders:** If a position on the screen corresponds to an interference maximum (`d sin(θ) = m_i λ`) but also to a diffraction minimum from the individual slits (`a sin(θ) = m_d λ`), then that interference maximum will be "missing" or have zero intensity. This happens when `d/a` is an integer.

**2. Mathematical Formulation for Intensity:**
The relative intensity `I(θ)` for the combined pattern is:
`I(θ) = I₀ * (sin(β)/β)² * cos²(α)`
where:
*   `β = (π * a * sin(θ)) / λ` (diffraction term)
*   `α = (π * d * sin(θ)) / λ` (interference term)
*   `I₀` is the maximum intensity at the center of the pattern.

## II. Simulation Engine & Code Implementation (`physics_engine.py`)

The core physics calculations are encapsulated in `physics_engine.py`. This module uses NumPy for efficient vectorized calculations.

**A. Input Parameters & Representation:**
The engine accepts the following physical parameters, which are typically provided in mixed units from the frontend and converted to meters (`_m` suffix) by the Flask backend before being passed to the engine:
*   `wavelength_m`: Wavelength of light (meters).
*   `slit_width_m`: Width of a single slit, or each slit in a double-slit setup (meters).
*   `slit_separation_m`: Distance between the centers of the two slits (meters, for double-slit only).
*   `screen_distance_m`: Distance from the slits to the virtual screen (meters).

**B. Screen Model & Angular Displacement:**
*   **Screen Discretization:** The virtual screen is modeled as a 1D array of points.
    ```python
    DEFAULT_SCREEN_WIDTH_M = 0.1  # e.g., 10 cm
    NUM_SCREEN_POINTS = 500
    y = np.linspace(-DEFAULT_SCREEN_WIDTH_M / 2, DEFAULT_SCREEN_WIDTH_M / 2, NUM_SCREEN_POINTS)
    ```
    `y` represents the positions on the screen relative to the center.
*   **Angular Calculation:** For Fraunhofer diffraction, the angle `θ` to a point `y` on the screen is related by `tan(θ) = y / L`. For small angles (where `L >> y`), the **small angle approximation** `sin(θ) ≈ tan(θ) ≈ y / L` is often used. The current implementation uses `sin(θ) ≈ y / L` directly within the `β` and `α` calculations:
    *   For `β`: `(np.pi * slit_width_m * y) / (wavelength_m * screen_distance_m)`
    *   For `α`: `(np.pi * slit_separation_m * y) / (wavelength_m * screen_distance_m)`
    This avoids calculating `sin(arctan(y/L))` for each point, simplifying computation while being accurate for typical experimental setups simulated.

**C. Intensity Calculation Logic:**

1.  **`calculate_single_slit_intensity(wavelength_m, slit_width_m, screen_distance_m)`:**
    *   Calculates `y` (screen positions) as described above.
    *   Calculates `β` for all points on the screen using vectorized NumPy operations:
        ```python
        beta = (np.pi * slit_width_m * y) / (wavelength_m * screen_distance_m)
        ```
    *   Calculates the relative intensity `(sin(β)/β)²`:
        ```python
        intensity = (np.sin(beta) / beta)**2
        ```
    *   **Singularity Handling:** The `sin(β)/β` term is undefined when `β = 0`. However, by L'Hôpital's rule, the limit as `β → 0` is 1. This is handled by:
        ```python
        intensity[beta == 0] = 1.0
        ```
        This uses NumPy's boolean indexing to set the intensity to 1 where `beta` is zero.
    *   Returns `y` (screen positions in meters) and the calculated `intensity` array.

2.  **`calculate_double_slit_intensity(wavelength_m, slit_width_m, slit_separation_m, screen_distance_m)`:**
    *   Calculates `y` screen positions.
    *   Calculates the diffraction term `β` and `diffraction_effect = (sin(β)/β)²` (including singularity handling) as in the single-slit case.
    *   Calculates the interference term `α`:
        ```python
        alpha = (np.pi * slit_separation_m * y) / (wavelength_m * screen_distance_m)
        ```
    *   Calculates `interference_effect = np.cos(alpha)**2`.
    *   The total relative intensity is the product of these two effects:
        ```python
        intensity = diffraction_effect * interference_effect
        ```
    *   Returns `y` (screen positions in meters) and the calculated `intensity` array.

**D. Wavelength to RGB Conversion (`wavelength_to_rgb(wavelength_nm)`):**
*   This function provides an approximate conversion of a given wavelength in nanometers (nm) to an RGB color string (`"rgb(r,g,b)"`) for visualizing the light color and the plot line.
*   The algorithm is a set of piecewise linear interpolations across different segments of the visible spectrum (approximating CIE color matching functions).
*   It includes an intensity factor and a gamma correction (`gamma = 0.8`) to adjust perceived brightness and color. This is a common, though simplified, method for such conversions.

**E. Assumptions & Limitations in the Physics Model:**
*   **Fraunhofer (Far-Field) Diffraction:** The simulation assumes the screen is far enough from the slits for plane waves to be a good approximation for the wavelets arriving at any point on the screen.
*   **Scalar Diffraction Theory:** Light is treated as a scalar wave, ignoring its vector (polarization) nature. This is generally valid for unpolarized light and when apertures are much larger than the wavelength.
*   **Infinitely Long Slits:** The model is for slits that are effectively infinitely long in one dimension, so diffraction effects are only considered in the dimension perpendicular to the slit length.
*   **Monochromatic and Coherent Light:** The incident light is assumed to be perfectly monochromatic (single wavelength) and spatially coherent across the slit(s).
*   **Thin Slits:** The thickness of the material in which the slits are made is neglected.

## III. Web Application Architecture (Flask Backend - `app.py`)

The Flask application (`app.py`) serves as the backend, handling user requests, processing parameters, and invoking the physics engine.

**A. Key Routes:**
*   `@app.route('/')`: Serves the main simulation page (`index.html`).
*   `@app.route('/theory')`: Serves the theory explanation page (`theory.html`).
*   `@app.route('/experiment')`: Serves the experimental setup guide (`experiment.html`).
*   `@app.route('/calculate_pattern', methods=['POST'])`: The API endpoint for running the simulation.

**B. Simulation Request Handling (`/calculate_pattern`):**
1.  **Receiving Parameters:** Expects a JSON payload in the POST request containing user-defined parameters:
    ```json
    {
        "simulationType": "double_slit", // or "single_slit"
        "wavelength": 550,
        "wavelengthUnit": "nm",
        "slitWidth": 10,
        "slitWidthUnit": "µm",
        // ... other parameters
    }
    ```
2.  **Unit Conversion:** Converts all physical dimension inputs (wavelength, slit width, etc.) from their user-specified units (nm, µm, mm) to meters (the standard unit for the `physics_engine.py`) using a `UNIT_CONVERSIONS` dictionary.
    ```python
    UNIT_CONVERSIONS = {
        "nm": 1e-9, "µm": 1e-6, "mm": 1e-3, "m": 1.0
    }
    wavelength_m = wavelength_val * UNIT_CONVERSIONS.get(wavelength_unit, 1e-9)
    ```
3.  **Input Validation:** Performs basic validation:
    *   Ensures physical dimensions are positive.
    *   For double-slit, ensures slit width is less than slit separation.
    *   Handles potential `ValueError` if inputs are not valid numbers.
4.  **Invoking Physics Engine:** Calls the appropriate function from `physics_engine.py` based on `simulationType`.
5.  **Formatting Response:** The results from the physics engine (screen positions in meters, intensity array) are processed:
    *   Screen positions are converted to millimeters (`* 1000`) for more user-friendly display on the chart axes.
    *   NumPy arrays are converted to Python lists (`.tolist()`) for JSON serialization.
    *   An approximate RGB color for the plot line is determined using `wavelength_to_rgb`.
    The response is a JSON object:
    ```json
    {
        "screen_positions_mm": [...],
        "intensity": [...],
        "plot_color": "rgb(r,g,b)"
    }
    ```

## IV. Frontend Interaction & Visualization (`static/js/simulation.js`)

The client-side logic handles user interaction, parameter submission, and rendering the results using Chart.js.

**A. Parameter Management:**
*   Event listeners on input fields (`wavelengthInput`, `slitWidthInput`, etc.) and the wavelength slider (`wavelengthSlider`) capture user changes.
*   The `wavelengthSlider` and `wavelengthInput` are synchronized, and a `colorPreview` `div`'s background is updated in real-time to reflect the selected wavelength.
*   The visibility of slit separation controls is toggled based on the selected `simulationType`.

**B. API Communication:**
*   The `runSimulation()` function gathers all parameters from the HTML form elements.
*   It constructs a JSON object matching the backend's expected format.
*   An asynchronous `fetch` request (POST) is made to the `/calculate_pattern` endpoint with the JSON payload.

**C. Response Processing & Charting:**
1.  **Error Handling:** Checks if the `fetch` response is `ok`. If not, it attempts to parse an error message from the JSON response and displays it.
2.  **Data Extraction:** On a successful response, it parses the JSON data containing `screen_positions_mm`, `intensity`, and `plot_color`.
3.  **Chart.js Integration (`updateChart` function):**
    *   If an existing chart instance (`intensityChart`) exists, it's destroyed to prevent conflicts.
    *   A new Chart.js line chart is created on the `<canvas id="intensityPatternChart">`.
    *   **Data Mapping:**
        *   `labels`: `screen_positions_mm` (X-axis).
        *   `datasets[0].data`: `intensityData` (Y-axis).
        *   `datasets[0].borderColor`: `plot_color`.
    *   **Chart Options:**
        *   `responsive: true`, `maintainAspectRatio: false`: Allows the chart to adapt to its container's dimensions (height controlled via CSS on `.chart-container`).
        *   Axis titles (`Position on Screen (mm from center)`, `Relative Intensity`).
        *   Y-axis limits (`min: 0`, `max: 1.05`).
        *   Customized tooltips to show position and intensity with appropriate formatting.
        *   Tick formatting to reduce clutter on the X-axis for dense datasets.

## V. Educational Content Structure (`templates/`)

The `/theory` and `/experiment` routes serve static HTML pages (`theory.html`, `experiment.html`) generated using Flask's `render_template`. These pages contain:
*   **`theory.html`:** Textual explanations of the physics principles (Huygens', superposition, mathematical formulas for diffraction and interference) with appropriate headings and lists for clarity.
*   **`experiment.html`:** Practical guidance on setting up real-world experiments, including lists of apparatus, procedural steps, measurement advice, and safety precautions (especially regarding laser use). An illustrative diagram (e.g., from Wikimedia Commons) is embedded.

These templates extend a `layout.html` for consistent navigation and page structure.

---

This detailed overview provides insight into the scientific and technical underpinnings of the Lux Resonans simulation project.
