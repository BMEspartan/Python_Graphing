# Python Graphing Examples

A small collection of Python scripts that demonstrate different data visualization techniques using `matplotlib` (and a bit of `NumPy` and `SciPy`).

## Files

- `time_series_plot.py`  
  Generates a noisy time series, applies a moving average, highlights a region of interest, and annotates the peak.

- `scatter_regression.py`  
  Creates synthetic linear data, fits a regression line with `numpy.polyfit`, plots residuals, and computes R².

- `bar_error_bars.py`  
  Simulates group data and visualizes group means with error bars and value labels.

- `multi_panel_dashboard.py`  
  Builds a 2×2 dashboard-style figure: histogram, KDE, boxplot, and scatter plot of the same dataset.

## Usage

```bash
pip install numpy matplotlib scipy

python time_series_plot.py
python scatter_regression.py
python bar_error_bars.py
python multi_panel_dashboard.py
