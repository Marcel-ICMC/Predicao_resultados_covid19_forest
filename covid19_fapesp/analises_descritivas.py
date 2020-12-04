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

from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum
from connection_mysql import cursorConexao
from collections import Counter
from math import pi
import datetime
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PATH_FOLDER = 'analises/'
PATH_SHP_SP = 'SP-MUN/35MUE250GC_SIR.shp'

def pie_chart_bokeh(output_file_name, x, index_name, title):
    output_file(output_file_name)
    data = pd.Series(x).reset_index(name='value').rename(columns={'index':index_name})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    try:
        if len(data) < 20:
            data['color'] = Category20c[len(data)]
        else:
            data['color'] = Category20c[20]
    except:
        data['color'] = '#084594'
    p = figure(plot_height=1000, plot_width=1000, title=title, toolbar_location=None,
            tools="hover", tooltips="@{}: @value".format(index_name), x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field=index_name, source=data)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    show(p)

def cidades_por_paciente():
    cursor = cursorConexao()
    query = 'Select municipio.municipio, count(*) From covidFapesp.patient join municipio on municipio.id = patient.CD_MUNICIPIO Group By municipio.municipio'
    cursor.execute(query)
    top_20_list = []
    for mun, freq in cursor.fetchall():
        k  = str(mun).upper()
        top_20_list.append((freq,k))
    top_20_list.sort(reverse=True, key= lambda x:x[0])
    x = {}
    for freq,k in top_20_list[:20]:
        x[k] = freq
    pie_chart_bokeh("pie_chart_municipios.html", x, 'municipio', "Municípios dos pacientes") 
    cursor.close()  

def desfecho_por_paciente():
    cursor = cursorConexao()
    query = 'Select DE_DESFECHO, count(*) From covidFapesp.desfecho Group By DE_DESFECHO'
    cursor.execute(query)
    dados = cursor.fetchall()
    x = {}
    for de_desfecho, freq in dados:
        if len(de_desfecho) > 3:
            try:
                k  = de_desfecho.decode('latin1').encode('utf8').decode('utf-8')
            except:
                k  = de_desfecho
        else:
            k = 'Desconhecido'
        x[k] = freq
    cursor.close()
    pie_chart_bokeh("pie_chart_desfecho.html", x, 'desfecho', "Desfecho por tipos")
    
def exames_anormais():
    cursor = cursorConexao()
    query = 'SELECT exame_laboratorial.DE_EXAME, count(*) FROM exame_laboratorial INNER JOIN parse_exame_laboratorial on parse_exame_laboratorial.ID_EXAME=exame_laboratorial.ID where IS_ABNORMAL = "True" GROUP BY exame_laboratorial.DE_EXAME;'
    cursor.execute(query)
    dados = list(cursor.fetchall())
    dados.sort(key = lambda x:x[1], reverse=True)
    x = {exame:freq for exame,freq in dados[:15]}
    outros = 0
    for _,n in dados[15:]:
        outros += n
    x['Outros'] = outros
    pie_chart_bokeh("pie_chart_exames_anormais.html", x, 'exame', "Exames anormais - Top 15")
    cursor.close()

def sexo_pacientes():
    cursor = cursorConexao()
    cursor.execute('SELECT sexo.sexo FROM covidFapesp.patient join sexo on IC_SEXO = sexo.id')
    lista_sexos = []
    for sexo in cursor.fetchall():
        lista_sexos.append(sexo[0])
    cursor.close()
    counter_sexos = Counter(lista_sexos)
    labels = []
    sizes = []
    for l,v in counter_sexos.items():
        labels.append(l)
        sizes.append(v)
    explode = (0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Gráfico em pizza do sexo dos pacientes')
    plt.savefig('pie_chart_sexo_pacientes.png')

def histograma_idades():
    cursor = cursorConexao()
    cursor.execute('SELECT AA_NASCIMENTO FROM covidFapesp.patient;')
    lista_idades = []
    current_year = datetime.datetime.now().year
    for idade in cursor.fetchall():
        try:
            lista_idades.append(current_year-int(idade[0]))
        except:
            print('Erro ao calcular a idade do ano de nascimento ',idade[0])
    plt.hist(lista_idades,bins=[i for i in range(0,106,5)])
    plt.xlabel('Idade dos pacientes')
    plt.ylabel('Frequência')
    plt.title('Histograma de idade dos pacientes')
    plt.savefig('histograma_idade_pacientes.png')
    plt.clf()
    cursor.close()

def excel_municipios():
    cursor = cursorConexao()
    query = 'Select municipio.municipio, count(*) From covidFapesp.patient join municipio on municipio.id = patient.CD_MUNICIPIO Group By municipio.municipio'
    cursor.execute(query)
    dados = cursor.fetchall()
    x = {}
    for mun, freq in dados:
        if len(str(mun)) > 3:
            k  = str(mun).upper()
            x[k] = freq
    rows = []
    for k,v in x.items():
        rows.append({
            'source':k,
            'values':v
        })    
    df_municipios = pd.DataFrame(rows)
    df_municipios.to_excel('infecção_por_municípios.xlsx',index=False)
    cursor.close()

if __name__ == "__main__":
    pass
    # print('Excel de municípios')
    # excel_municipios()
    # print('Cidades por paciente')
    # cidades_por_paciente()
    # print('Desfecho por paciente')
    # desfecho_por_paciente()
    # print('Exames anormais')
    # exames_anormais()
    # print('Sexo dos pacientes')
    # sexo_pacientes()
    # print('Histograma de idades')
    # histograma_idades()