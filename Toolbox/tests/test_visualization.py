import pandas as pd
from toolbox.visualization import plot_scatter

def test_plot_scatter_returns_figure(tmp_path):
    df = pd.DataFrame({"x": [1,2], "y": [3,4]})
    fig = plot_scatter(df, x="x", y="y")
    # Verify that the returned object has a savefig method
    assert hasattr(fig, "savefig")
    # Optionally, test saving to a temporary file
    out_file = tmp_path / "test_scatter.png"
    fig.savefig(str(out_file))
    assert out_file.exists()
