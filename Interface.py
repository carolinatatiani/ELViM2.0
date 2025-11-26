'''
 # @ Created by: Carolina Tatiani
 #@ At: 2025, Sep, 18 15:07
 # @ Last Modification: 2025, Nov,16 22:52
 # @ By: Carolina Tatiani
 # @ E-mail: carolina.tatiani@unesp.br
 '''


from bokeh.models import Select
import numpy as np
import os

from bokeh.layouts import column, row
from bokeh.models import (
    Button,
    TextInput,
    LinearColorMapper,
    ColumnDataSource,
    TabPanel,
    Tabs,
    Slider,
    ColorBar
)
import bokeh.palettes as bp
from bokeh.plotting import figure, curdoc

TOOLS = "hover,pan,wheel_zoom,zoom_in,zoom_out,reset,tap,save,box_select,poly_select,lasso_select,fullscreen,help"

# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------

color_options = ["Select color file:"]
color_array = [f for f in os.listdir(
    '.') if f.endswith('.txt') or f.endswith('.dat')]
color_array.sort()
color_options.extend(color_array)

dataset_options = ["Select projection file:"]
projection_array = [f for f in os.listdir('.') if f.endswith('.out')]
projection_array.sort()
dataset_options.extend(projection_array)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

# ColumnDataSource starts empty
source = ColumnDataSource(
    data=dict(
        x=[],
        y=[],
        alpha=[],
        colors_norm=[]
    )
)

current_palette = bp.Viridis256
mapper = LinearColorMapper(palette=current_palette, low=0, high=1)


def SetColors(colors_array):
    """Normalize colors and update source with colors_norm."""
    if len(colors_array) == 0 or len(source.data["x"]) == 0:
        return

    color_min = np.min(colors_array)
    color_max = np.max(colors_array)

    # avoid division by zero
    if color_max == color_min:
        colors_norm = np.zeros_like(colors_array)
    else:
        colors_norm = (colors_array - color_min) / (color_max - color_min)

    source.data.update(colors_norm=colors_norm)


def execute_command(cmd):
    ret = os.system(cmd)
    if ret == 0:
        print("Command executed successfully.")
    else:
        print("Error executing command.")


def save_selection_callback():
    idx = source.selected.indices

    if not idx:
        print("No points selected.")
        return

    x_sel = np.array(source.data["x"])[idx]
    y_sel = np.array(source.data["y"])[idx]

    data = np.column_stack([x_sel, y_sel])

    fname = "Selection.npy"
    np.save(fname, data)

    print(f"Saved {len(idx)} selected points to {fname}.")

# -----------------------------------------------------------------------------
# Main ELViM projection plot
# -----------------------------------------------------------------------------


p = figure(height=600, title="ELViM Projection", toolbar_location="above",
           tools=TOOLS, sizing_mode="scale_width")

points = p.scatter(
    x='x', y='y', source=source, size=5,
    fill_color={'field': 'colors_norm', 'transform': mapper},
    fill_alpha='alpha',
    line_alpha='alpha'
)
color_bar = ColorBar(color_mapper=mapper, location=(0, 0), width=8)
p.add_layout(color_bar, 'right')

# -----------------------------------------------------------------------------
# SuAVE Tab
# -----------------------------------------------------------------------------

suave_cmd = TextInput(title="SuAVE command line:")
run_suave = Button(label="Run SuAVE")


def run_suave_callback():
    print("Running SuAVE...")
    execute_command(suave_cmd.value)


run_suave.on_click(run_suave_callback)

suave_layout = column(suave_cmd, run_suave)
suave_panel = TabPanel(child=suave_layout, title="SuAVE")

# -----------------------------------------------------------------------------
# ELViM Tab
# -----------------------------------------------------------------------------

elvim_cmd = TextInput(title="Elvim command line:")
run_elvim = Button(label="Run ELViM")

projection_select = Select(title="Select projection file:",
                           options=dataset_options,
                           value=dataset_options[0] if dataset_options else "")

color_select = Select(title="Color files available:",
                      options=color_options,
                      value=color_options[0] if color_options else "")


def run_elvim_callback():
    print("Running ELViM...")
    execute_command(elvim_cmd.value)


def apply_projection_callback():
    fname = projection_select.value
    data = np.loadtxt(fname)
    n = data.shape[0]
    source.data.update(
        x=data[:, 0],
        y=data[:, 1],
        alpha=np.ones(n),
        colors_norm=np.zeros(n),
    )


def apply_colors_callback():
    fname = color_select.value
    if not fname or fname.startswith("Select"):
        return

    colors = np.loadtxt(fname)

    # guarda internamente o último vetor
    if len(colors) != len(source.data['x']):
        print("Error: color vector does not match number of points.")
        return
    SetColors(colors)


run_elvim.on_click(run_elvim_callback)


elvim_layout = column(elvim_cmd, run_elvim, projection_select, color_select)
elvim_panel = TabPanel(child=elvim_layout, title="ELViM")

projection_select.on_change(
    'value', lambda attr, old, new: apply_projection_callback())
color_select.on_change('value', lambda attr, old, new: apply_colors_callback())

# -----------------------------------------------------------------------------
# Configurações Tab — sliders and palette select
# -----------------------------------------------------------------------------


point_size_slider = Slider(title="Point Size",
                           start=1, end=20, step=1, value=5)
alpha_slider = Slider(title="Transparency (alpha)",
                      start=0.0, end=1.0, step=0.01, value=1.0)
palette_select = Select(title="Color Palette:", options=[
                        "Viridis", "Inferno", "Magma", "Plasma", "Turbo"], value="Viridis")


save_selection_button = Button(
    label="Save Selected Points", button_type="success")

palette_map = {
    "Viridis": bp.Viridis256,
    "Inferno": bp.Inferno256,
    "Magma": bp.Magma256,
    "Plasma": bp.Plasma256,
    "Turbo": bp.Turbo256,
}


def update_point_size(attr, old, new):
    points.glyph.size = new


def update_alpha(attr, old, new):
    n = len(source.data['x'])
    if n == 0:
        return

    source.data['alpha'] = [new] * n
    points.glyph.fill_alpha = new
    points.glyph.line_alpha = new


def update_palette(attr, old, new):
    global current_palette
    current_palette = palette_map[new]
    mapper.palette = current_palette
    if "color_raw" in source.data:
        SetColors(source.data["color_raw"])


point_size_slider.on_change('value', update_point_size)
alpha_slider.on_change('value', update_alpha)
palette_select.on_change('value', update_palette)
save_selection_button.on_click(save_selection_callback)

config_layout = column(
    point_size_slider,
    alpha_slider,
    palette_select,
    save_selection_button
)

config_panel = TabPanel(child=config_layout, title="Plot Configurations")

# -----------------------------------------------------------------------------
# Tabs container
# -----------------------------------------------------------------------------

tabs = Tabs(tabs=[suave_panel, elvim_panel, config_panel])

# -----------------------------------------------------------------------------
# Final layout
# -----------------------------------------------------------------------------

# --- Layout revised to ensure plot appears correctly ---
# CHANGES:
# + Force tabs to have fixed width (250px)
# + Ensure plot expands to the rest of the screen
# + Use stretch_height only for tabs, stretch_both for plot
# + Wrap plot inside a container if needed

# Set fixed width for left-side tabs
# (prevents them from expanding horizontally and hiding the plot)
tabs.width = 450
p.width = 600
p.height = 600

tabs.sizing_mode = "stretch_height"
p.sizing_mode = "fixed"

layout = row(
    tabs,
    p,
    sizing_mode="stretch_both",
)

curdoc().add_root(layout)
