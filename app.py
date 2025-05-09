# /lux_resonans/app.py
from flask import Flask, render_template, request, jsonify
import numpy as np
from physics_engine import (
    calculate_single_slit_intensity,
    calculate_double_slit_intensity,
    wavelength_to_rgb
)

app = Flask(__name__)

# Unit conversion factors to meters
UNIT_CONVERSIONS = {
    "nm": 1e-9,  # nanometers to meters
    "µm": 1e-6,  # micrometers to meters
    "mm": 1e-3,  # millimeters to meters
    "m": 1.0     # meters
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/theory')
def theory():
    return render_template('theory.html')

@app.route('/experiment')
def experiment_info(): # Renamed to avoid conflict with potential variable names
    return render_template('experiment.html')

@app.route('/calculate_pattern', methods=['POST'])
def calculate_pattern():
    try:
        data = request.get_json()

        sim_type = data.get('simulationType', 'double_slit')
        
        # Wavelength
        wavelength_val = float(data.get('wavelength', 550))
        wavelength_unit = data.get('wavelengthUnit', 'nm')
        wavelength_m = wavelength_val * UNIT_CONVERSIONS.get(wavelength_unit, 1e-9)

        # Slit width
        slit_width_val = float(data.get('slitWidth', 10))
        slit_width_unit = data.get('slitWidthUnit', 'µm')
        slit_width_m = slit_width_val * UNIT_CONVERSIONS.get(slit_width_unit, 1e-6)

        # Slit separation (only for double slit)
        slit_separation_val = float(data.get('slitSeparation', 50))
        slit_separation_unit = data.get('slitSeparationUnit', 'µm')
        slit_separation_m = slit_separation_val * UNIT_CONVERSIONS.get(slit_separation_unit, 1e-6)
        
        # Screen distance
        screen_distance_val = float(data.get('screenDistance', 1))
        screen_distance_unit = data.get('screenDistanceUnit', 'm')
        screen_distance_m = screen_distance_val * UNIT_CONVERSIONS.get(screen_distance_unit, 1.0)

        # Validate positive values for physical dimensions
        if not all(v > 0 for v in [wavelength_m, slit_width_m, screen_distance_m]):
            return jsonify({"error": "Wavelength, slit width, and screen distance must be positive."}), 400
        if sim_type == 'double_slit' and slit_separation_m <= 0:
             return jsonify({"error": "Slit separation must be positive for double slit."}), 400
        if sim_type == 'double_slit' and slit_width_m >= slit_separation_m:
            return jsonify({"error": "Slit width must be less than slit separation."}), 400


        screen_positions = []
        intensity = []

        if sim_type == 'single_slit':
            screen_positions, intensity = calculate_single_slit_intensity(
                wavelength_m, slit_width_m, screen_distance_m
            )
        elif sim_type == 'double_slit':
            screen_positions, intensity = calculate_double_slit_intensity(
                wavelength_m, slit_width_m, slit_separation_m, screen_distance_m
            )
        else:
            return jsonify({"error": "Invalid simulation type"}), 400

        if screen_positions.size == 0: # Check if calculation failed due to bad params in engine
             return jsonify({"error": "Calculation failed, likely due to invalid parameters (e.g., zero values)."}), 400

        # Prepare data for JSON response
        # Convert numpy arrays to lists for JSON serialization
        # Convert screen positions to mm for more convenient display on graph axis
        response_data = {
            "screen_positions_mm": (screen_positions * 1000).tolist(), 
            "intensity": intensity.tolist(),
            "plot_color": wavelength_to_rgb(wavelength_val if wavelength_unit == 'nm' else wavelength_val * 1e9) # Ensure nm for color
        }
        return jsonify(response_data)

    except ValueError:
        return jsonify({"error": "Invalid input. Please ensure all values are numbers."}), 400
    except Exception as e:
        # Log the exception e for debugging
        print(f"An error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500

if __name__ == '__main__':
    app.run(debug=True)