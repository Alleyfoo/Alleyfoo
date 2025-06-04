"""
A simple end-to-end example script demonstrating Toolbox usage.
"""
import pandas as pd
from toolbox.utils import hello_world
from toolbox.visualization import plot_scatter
from toolbox.data_processing import load_csv

def main():
    print(hello_world())

    # If you have a CSV in data/, you can load and plot it
    try:
        df = load_csv("data/sample.csv")
    except FileNotFoundError:
        # Create a dummy DataFrame for demonstration
        df = pd.DataFrame({
            "x": [10, 20, 30, 40, 50],
            "y": [5, 4, 3, 2, 1]
        })

    fig = plot_scatter(df, x="x", y="y", title="Simple Analysis Scatter")
    fig.savefig("examples/output.png")
    print("Saved scatter to examples/output.png")

if __name__ == "__main__":
    main()
