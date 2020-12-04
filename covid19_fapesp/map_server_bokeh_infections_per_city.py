# Copyright (c) 2020 Danilo Panzeri Nogueira Carlotti

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from bokeh.plotting import figure, save
from bokeh.io import show, curdoc, output_notebook
from bokeh.models import (CDSView, ColorBar, ColumnDataSource,
                          CustomJS, CustomJSFilter, 
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider)
from bokeh.layouts import column, row, widgetbox
from bokeh.palettes import brewer
from bokeh.plotting import figure
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def remove_accents(texto):
	dicionario_acentos = {'Á':'A','Ã':'A','À':'A','á':'a','ã':'a','à':'a','É':'E','é':'e','Ê':'E','ê':'e','Í':'I','í':'i',
	'Ó':'O','ó':'o','Õ':'O','õ':'o','Ô':'O','ô':'o','Ú':'U','ú':'u','ç':'c','Ç':'Ç',';':'',',':'','/':'','\\':'','{':'','}':''
	,'(':'',')':'','-':'','_':''}
	texto = str(texto)
	for k,v in dicionario_acentos.items():
		texto = texto.replace(k,v)
	return texto

if __name__ == "__main__":    
    PATH_SHAPE_FILE = 'SP-MUN/35MUE250GC_SIR.shp'
    PATH_EXCEL_TOTAL = 'infecção_por_municípios.xlsx'
    gdf = gpd.read_file(PATH_SHAPE_FILE)
    gdf['NM_MUNICIP'] = gdf['NM_MUNICIP'].apply(lambda x: remove_accents(x))
    df_values_city = pd.read_excel(PATH_EXCEL_TOTAL)
    df_values_city['source'] = df_values_city['source'].apply(lambda x: x.upper())
    merged = gdf.merge(df_values_city, left_on='NM_MUNICIP',right_on='source',how='left')
    maximum_value = []
    for i in merged['values'].tolist():
        try:
            maximum_value.append(int(i))
        except:
            pass
    maximum_value.sort()
    geosource = GeoJSONDataSource(geojson = merged.to_json())
    palette = brewer['YlGnBu'][8]
    palette = palette[::-1] 
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = maximum_value[-1],  nan_color = '#d9d9d9')
    color_bar = ColorBar(color_mapper = color_mapper, 
                        label_standoff = 8,
                        width = 400, height = 30,
                        border_line_color = None,
                        location = (0,0), 
                        orientation = 'horizontal')
    p = figure(title = 'Infections per city in 2020', 
            plot_height = 650, plot_width = 850, 
            toolbar_location = 'below',
            tools = 'pan, wheel_zoom, box_zoom, reset, save', output_backend="webgl")
    p.axis.visible = False
    states = p.patches('xs','ys', source = geosource,
        fill_color = {'field' :'values',
                        'transform' : color_mapper},
        line_color = 'gray', 
        line_width = 0.25, 
        fill_alpha = 1)
    p.add_layout(color_bar, 'below')
    p.add_tools(HoverTool(renderers = [states],
                        tooltips = [('State','@NM_MUNICIP'),
                                ('Frequency', '@values')]))
    show(p)

    