"""
time_series_plot.py

Demonstrates basic time-series plotting in matplotlib:
- Noisy signal
- Moving average smoothing
- Shaded region highlighting
- Custom labels and annotations
"""

import numpy as np
import matplotlib.pyplot as plt


def generate_time_series(n_points: int = 500, noise_scale: float = 0.4):
    """Generate a noisy sine-wave time series."""
    t = np.linspace(0, 10, n_points)
    signal = np.sin(2 * np.pi * 0.5 * t)  # base sine wave
    noise = np.random.normal(scale=noise_scale, size=n_points)
    y = signal + noise
    return t, y


def moving_average(x: np.ndarray, window_size: int = 25):
    """Simple moving average using convolution."""
    if window_size < 1:
        raise ValueError("window_size must be >= 1")
    window = np.ones(window_size) / window_size
    return np.convolve(x, window, mode="same")


def main():
    # 1. Generate synthetic data
    t, y = generate_time_series()

    # 2. Smooth the data
    y_smooth = moving_average(y, window_size=25)

    # 3. Create the plot
    plt.figure(figsize=(10, 5))

    # Raw noisy data
    plt.plot(t, y, label="Noisy signal", alpha=0.5, linewidth=1)

    # Smoothed data
    plt.plot(t, y_smooth, label="Moving average (window=25)", linewidth=2)

    # Highlight a region of interest
    highlight_start, highlight_end = 3, 6
    plt.axvspan(highlight_start, highlight_end, alpha=0.1, hatch="////",
                label="Region of interest")

    # Annotate the maximum of the smoothed curve
    idx_max = np.argmax(y_smooth)
    t_max, y_max = t[idx_max], y_smooth[idx_max]
    plt.scatter(t_max, y_max, zorder=3)
    plt.annotate(
        f"Peak ~ {y_max:.2f}",
        xy=(t_max, y_max),
        xytext=(t_max + 0.3, y_max + 0.5),
        arrowprops=dict(arrowstyle="->", linewidth=1),
    )

    # Labels, title, legend, grid
    plt.title("Noisy Time Series with Moving Average Smoothing")
    plt.xlabel("Time [s]")
    plt.ylabel("Signal amplitude")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    plt.legend()

    plt.tight_layout()
    plt.savefig("time_series_plot.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
