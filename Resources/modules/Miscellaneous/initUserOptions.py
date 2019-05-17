from os.path import expanduser

def initOptions():
    with open("resources/temp/user_options.txt", 'w') as writefile:
        writefile.write("""
[GENERAL]
application_datetime=today

[PLOTTING]
filled_plots=False
line_width=2
color_cycler_theme=default
use_twin_axes=False

[STATISTICS]

[DATASETS TAB]
current_map_location=
current_map_layers=

[FILE OPS]
file_name={0}\\untitled.fcst

[DATA TAB]
por_start=
current_plotted_columns=
current_plot_bounds=""".format(expanduser("~")))