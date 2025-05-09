# /lux_resonans/physics_engine.py
import numpy as np

# Constants
DEFAULT_SCREEN_WIDTH_M = 0.1  # Virtual screen width in meters (e.g., 10 cm)
NUM_SCREEN_POINTS = 500     # Number of points to calculate intensity on the screen

def calculate_single_slit_intensity(wavelength_m, slit_width_m, screen_distance_m):
    """
    Calculates the intensity pattern for single-slit diffraction.

    Args:
        wavelength_m (float): Wavelength of light in meters.
        slit_width_m (float): Width of the slit in meters.
        screen_distance_m (float): Distance from slit to screen in meters.

    Returns:
        tuple: (screen_positions_m, relative_intensity)
               screen_positions_m: np.array of positions on the screen in meters.
               relative_intensity: np.array of corresponding relative light intensity.
    """
    if slit_width_m <= 0 or wavelength_m <= 0 or screen_distance_m <= 0:
        # Return empty arrays or raise an error for invalid inputs
        return np.array([]), np.array([])

    # Screen positions from -SCREEN_WIDTH_M/2 to +SCREEN_WIDTH_M/2
    y = np.linspace(-DEFAULT_SCREEN_WIDTH_M / 2, DEFAULT_SCREEN_WIDTH_M / 2, NUM_SCREEN_POINTS)
    
    # Angle theta for each point on the screen (small angle approximation: sin(theta) approx y/L)
    # For more accuracy, use theta = np.arctan(y / screen_distance_m)
    # but for typical setups y/L is small.
    # sin_theta = y / screen_distance_m
    # To avoid issues if screen_distance_m is very small relative to y, let's use a safe approach for beta
    
    # Parameter beta = (pi * a * sin(theta)) / lambda
    # Using sin_theta directly for clarity in the formula
    # Ensure we handle the case where slit_width_m is zero to avoid division by zero if not caught earlier
    
    beta = (np.pi * slit_width_m * y) / (wavelength_m * screen_distance_m) # Using small angle sin(theta) ~ y/L

    # Intensity I = I0 * (sin(beta)/beta)^2
    # Handle beta = 0 case (limit is 1)
    intensity = (np.sin(beta) / beta)**2
    intensity[beta == 0] = 1.0  # L'Hopital's rule for sin(x)/x as x -> 0

    return y, intensity


def calculate_double_slit_intensity(wavelength_m, slit_width_m, slit_separation_m, screen_distance_m):
    """
    Calculates the intensity pattern for double-slit interference.

    Args:
        wavelength_m (float): Wavelength of light in meters.
        slit_width_m (float): Width of each slit in meters.
        slit_separation_m (float): Distance between the centers of the two slits in meters.
        screen_distance_m (float): Distance from slits to screen in meters.

    Returns:
        tuple: (screen_positions_m, relative_intensity)
    """
    if slit_width_m <= 0 or slit_separation_m <=0 or wavelength_m <= 0 or screen_distance_m <= 0:
        return np.array([]), np.array([])

    y = np.linspace(-DEFAULT_SCREEN_WIDTH_M / 2, DEFAULT_SCREEN_WIDTH_M / 2, NUM_SCREEN_POINTS)
    
    # Diffraction term (from each single slit)
    # beta = (pi * a * sin(theta)) / lambda
    beta = (np.pi * slit_width_m * y) / (wavelength_m * screen_distance_m) # sin(theta) ~ y/L
    
    diffraction_effect = (np.sin(beta) / beta)**2
    diffraction_effect[beta == 0] = 1.0

    # Interference term
    # alpha = (pi * d * sin(theta)) / lambda
    alpha = (np.pi * slit_separation_m * y) / (wavelength_m * screen_distance_m) # sin(theta) ~ y/L
    
    interference_effect = np.cos(alpha)**2

    # Total intensity I = I0 * (diffraction_effect) * (interference_effect)
    intensity = diffraction_effect * interference_effect
    
    return y, intensity

def wavelength_to_rgb(wavelength_nm):
    """
    Converts a wavelength in nm to an approximate RGB color string.
    This is a simplified conversion.
    """
    gamma = 0.8
    intensity_max = 255
    factor = 0.0
    r, g, b = 0, 0, 0

    if 380 <= wavelength_nm <= 439:
        r = -(wavelength_nm - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wavelength_nm <= 489:
        r = 0.0
        g = (wavelength_nm - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wavelength_nm <= 509:
        r = 0.0
        g = 1.0
        b = -(wavelength_nm - 510) / (510 - 490)
    elif 510 <= wavelength_nm <= 579:
        r = (wavelength_nm - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wavelength_nm <= 644:
        r = 1.0
        g = -(wavelength_nm - 645) / (645 - 580)
        b = 0.0
    elif 645 <= wavelength_nm <= 780:
        r = 1.0
        g = 0.0
        b = 0.0
    else: # Outside visible spectrum (approx)
        r = 0.0
        g = 0.0
        b = 0.0

    # Intensity factor adjustment
    if 380 <= wavelength_nm <= 419:
        factor = 0.3 + 0.7 * (wavelength_nm - 380) / (420 - 380)
    elif 420 <= wavelength_nm <= 700:
        factor = 1.0
    elif 701 <= wavelength_nm <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength_nm) / (780 - 700)
    else:
        factor = 0.0

    if r > 0: r = int(intensity_max * (r * factor)**gamma)
    if g > 0: g = int(intensity_max * (g * factor)**gamma)
    if b > 0: b = int(intensity_max * (b * factor)**gamma)
    
    return f"rgb({r},{g},{b})"