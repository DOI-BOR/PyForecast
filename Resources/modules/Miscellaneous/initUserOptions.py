from os.path import expanduser

def initOptions():
    with open("resources/temp/user_options.txt", 'w') as writefile:
        writefile.write("""
[GENERAL]
application_datetime=today
default_snow_time_window=2M
defualt_snow_time_period=1D
default_snow_function=first
default_streamflow_inflow_time_window=6M
default_streamflow_inflow_time_period=1M
default_streamflow_inflow_function=average
default_precipitation_time_window=
default_precipitation_time_period=
default_precipitation_function=accumulation
default_temperature_time_window=2M
default_temperature_time_period=1M
default_temperature_function=average
default_index_time_window=2M
default_index_time_period=1M
default_index_function=average

[PLOTTING]
filled_plots=False
line_width=2
color_cycler_theme=default
use_twin_axes=False

[STATISTICS]

[DATASETS TAB]
current_map_location=
current_map_layers=
reset_map=False

[FILE OPS]
file_name={0}\\untitled.fcst

[DATA TAB]
por_start=
current_plotted_columns=
current_plot_bounds=""".format(expanduser("~")))