// /lux_resonans/static/js/simulation.js
document.addEventListener('DOMContentLoaded', function () {
    const simulationTypeSelect = document.getElementById('simulationType');
    const wavelengthInput = document.getElementById('wavelength');
    const wavelengthUnitSelect = document.getElementById('wavelengthUnit');
    const wavelengthSlider = document.getElementById('wavelengthSlider');
    const wavelengthDisplay = document.getElementById('wavelengthDisplay');
    const colorPreview = document.getElementById('colorPreview');

    const slitWidthInput = document.getElementById('slitWidth');
    const slitWidthUnitSelect = document.getElementById('slitWidthUnit');

    const slitSeparationInput = document.getElementById('slitSeparation');
    const slitSeparationUnitSelect = document.getElementById('slitSeparationUnit');
    const doubleSlitParamsDiv = document.getElementById('doubleSlitParams');

    const screenDistanceInput = document.getElementById('screenDistance');
    const screenDistanceUnitSelect = document.getElementById('screenDistanceUnit');

    const runButton = document.getElementById('runSimulation');
    const errorMessageP = document.getElementById('errorMessage');

    let intensityChart = null; // To hold the chart instance

    // --- Utility to convert wavelength (nm) to an approximate RGB color string ---
    // (Simplified version for frontend preview, backend has a more detailed one)
    function wavelengthToCssColor(nm) {
        if (nm >= 380 && nm < 440) { return `rgb(${-(nm - 440) * 255 / 60}, 0, 255)`; } // Violet
        else if (nm >= 440 && nm < 490) { return `rgb(0, ${(nm - 440) * 255 / 50}, 255)`; } // Blue
        else if (nm >= 490 && nm < 510) { return `rgb(0, 255, ${-(nm - 510) * 255 / 20})`; } // Cyan
        else if (nm >= 510 && nm < 580) { return `rgb(${(nm - 510) * 255 / 70}, 255, 0)`; } // Green
        else if (nm >= 580 && nm < 645) { return `rgb(255, ${-(nm - 645) * 255 / 65}, 0)`; } // Yellow/Orange
        else if (nm >= 645 && nm <= 750) { return `rgb(255, 0, 0)`; } // Red
        else { return `rgb(200, 200, 200)`; } // Default for out of range
    }

    // --- Event Listeners ---
    simulationTypeSelect.addEventListener('change', toggleDoubleSlitParams);
    runButton.addEventListener('click', runSimulation);

    wavelengthInput.addEventListener('input', updateWavelengthSliderAndPreview);
    wavelengthSlider.addEventListener('input', updateWavelengthInputAndPreview);
    wavelengthUnitSelect.addEventListener('change', updateWavelengthSliderAndPreview);


    function updateWavelengthSliderAndPreview() {
        let value = parseFloat(wavelengthInput.value) || 550;
        const unit = wavelengthUnitSelect.value;

        if (unit === 'µm') { // Convert to nm for slider and preview
            value *= 1000;
        }
        // Clamp slider value to its min/max if input is out of typical visible range
        value = Math.max(parseFloat(wavelengthSlider.min), Math.min(parseFloat(wavelengthSlider.max), value));

        wavelengthSlider.value = value; // Slider is always in nm
        wavelengthDisplay.textContent = `${value.toFixed(0)} nm`;
        colorPreview.style.backgroundColor = wavelengthToCssColor(value);

        if (wavelengthUnitSelect.value === 'µm' && wavelengthInput.value != (value / 1000).toFixed(3)) {
            // if input was originally nm, and we switched unit to µm, update input field
            // wavelengthInput.value = (value / 1000).toFixed(3); //This causes issues if user is typing
        } else if (wavelengthUnitSelect.value === 'nm' && wavelengthInput.value != value.toFixed(0)) {
            // wavelengthInput.value = value.toFixed(0);
        }
    }

    function updateWavelengthInputAndPreview() {
        const sliderValue = parseFloat(wavelengthSlider.value);
        wavelengthDisplay.textContent = `${sliderValue.toFixed(0)} nm`;
        colorPreview.style.backgroundColor = wavelengthToCssColor(sliderValue);

        if (wavelengthUnitSelect.value === 'nm') {
            wavelengthInput.value = sliderValue.toFixed(0);
        } else if (wavelengthUnitSelect.value === 'µm') {
            wavelengthInput.value = (sliderValue / 1000).toFixed(3);
        }
    }


    function toggleDoubleSlitParams() {
        if (simulationTypeSelect.value === 'double_slit') {
            doubleSlitParamsDiv.style.display = 'block';
        } else {
            doubleSlitParamsDiv.style.display = 'none';
        }
    }

    async function runSimulation() {
        errorMessageP.textContent = ''; // Clear previous errors
        const params = {
            simulationType: simulationTypeSelect.value,
            wavelength: parseFloat(wavelengthInput.value),
            wavelengthUnit: wavelengthUnitSelect.value,
            slitWidth: parseFloat(slitWidthInput.value),
            slitWidthUnit: slitWidthUnitSelect.value,
            slitSeparation: parseFloat(slitSeparationInput.value),
            slitSeparationUnit: slitSeparationUnitSelect.value,
            screenDistance: parseFloat(screenDistanceInput.value),
            screenDistanceUnit: screenDistanceUnitSelect.value,
        };

        // Basic frontend validation
        if (isNaN(params.wavelength) || isNaN(params.slitWidth) || isNaN(params.screenDistance) ||
            (params.simulationType === 'double_slit' && isNaN(params.slitSeparation))) {
            errorMessageP.textContent = 'Error: All numerical fields must be filled correctly.';
            return;
        }
        if (params.wavelength <= 0 || params.slitWidth <= 0 || params.screenDistance <= 0 ||
            (params.simulationType === 'double_slit' && params.slitSeparation <= 0)) {
            errorMessageP.textContent = 'Error: Physical dimensions (wavelength, widths, distances) must be positive.';
            return;
        }


        try {
            const response = await fetch('/calculate_pattern', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            updateChart(data.screen_positions_mm, data.intensity, data.plot_color);

        } catch (error) {
            console.error('Simulation Error:', error);
            errorMessageP.textContent = `Error: ${error.message}`;
            // Optionally clear chart or show error state in chart area
            if (intensityChart) {
                intensityChart.destroy();
                intensityChart = null;
            }
        }
    }

    // /lux_resonans/static/js/simulation.js (inside the updateChart function)
    function updateChart(screenPositions, intensityData, plotColor) {
        const ctx = document.getElementById('intensityPatternChart').getContext('2d');

        if (intensityChart) {
            intensityChart.destroy();
        }

        intensityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: screenPositions,
                datasets: [{
                    label: 'Relative Light Intensity',
                    data: intensityData,
                    borderColor: plotColor || 'rgba(0, 123, 255, 1)',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // <<< IMPORTANT: Set this to false
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Position on Screen (mm from center)'
                        },
                        ticks: {
                            callback: function (value, index, values) {
                                if (screenPositions.length > 50 && index % Math.floor(screenPositions.length / 20) !== 0 && index !== 0 && index !== screenPositions.length - 1) {
                                    return null;
                                }
                                // Access the label directly from the data for precision
                                const labelValue = this.getLabelForValue(screenPositions[index]);
                                return labelValue !== undefined ? parseFloat(labelValue).toFixed(1) : '';
                            },
                            maxRotation: 0,
                            minRotation: 0
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Relative Intensity (Arbitrary Units)'
                        },
                        min: 0,
                        max: 1.05
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(4);
                                }
                                return label;
                            },
                            title: function (context) {
                                if (context.length > 0 && context[0].parsed.x !== undefined) {
                                    // Use the actual x value from the dataset for the tooltip title
                                    const originalXValue = screenPositions[context[0].dataIndex];
                                    return `Position: ${parseFloat(originalXValue).toFixed(2)} mm`;
                                }
                                return '';
                            }
                        }
                    },
                    legend: {
                        display: true
                    }
                }
            }
        });
    }
    // Initial setup
    toggleDoubleSlitParams();
    updateWavelengthSliderAndPreview(); // Initialize slider and color preview
    runSimulation(); // Run simulation with default values on page load
});