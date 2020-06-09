# Import required libraries
import pathlib
import os
from random import randint
import dash
import math
from datetime import datetime as dt
import re
import pandas as pd
import numpy as np

import flask
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
#Graficos
import plotly.graph_objects as go
import plotly.express as px

# Multi-dropdown options
from controls import REGIONES, ENFERMEDADES


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
app.title = 'Info COVID-19 Chile'

#####################################               GET DATA            ##########################################################################################################
#### Datos regional/comunal
url  = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto1/Covid-19_T.csv'
df_region = pd.read_csv(url)
df_reg = df_region.loc[0:3,:]
df_t =df_region.loc[3:,:]

#### Datos nacional
url_nacional = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto5/TotalesNacionales_T.csv'
df_nacional = pd.read_csv(url_nacional)
df_nacional['Fecha']= pd.to_datetime(df_nacional['Fecha'])
df_nacional = df_nacional.set_index('Fecha')


#Haremos los diccionarios de codigos regon y codigos comuna
#Dicc Region
dic_regiones = df_reg.T
dic_regiones.columns= dic_regiones.iloc[0]
dic_regiones = dic_regiones.drop(dic_regiones.index[0])
dic_regiones = dic_regiones.drop(['Comuna', 'Codigo comuna', 'Poblacion'], axis=1)
dic_regiones = dic_regiones.reset_index()
dic_regiones = dic_regiones.rename(columns={'index':'Regiones'})
dic_regiones = dic_regiones.drop_duplicates(subset=['Codigo region'])
dic_regiones = dic_regiones.set_index('Codigo region')
dic_regiones = dic_regiones.to_dict()
dic_regiones = list(dic_regiones.values())
dic_regiones = dic_regiones[0]

## DICC
opciones_regiones = [
    {"label": str(REGIONES[regiones]), "value": str(regiones)}
    for regiones in REGIONES
]


#Dicc Comunas
dic_com = df_reg.T
dic_com.columns= dic_com.iloc[0]
dic_com = dic_com.drop(dic_com.index[0])
dic_com = dic_com.reset_index()
dic_com = dic_com.drop(['index', 'Codigo region', 'Poblacion'], axis=1)
dic_com = dic_com.set_index('Codigo comuna')
dic_com = dic_com.to_dict()
dic_com = list(dic_com.values())
dic_com = dic_com[0]

#### Formar Diccionario Region -> Comuna
df_Region_comuna = df_reg.T
df_Region_comuna = df_Region_comuna.reset_index()
df_Region_comuna.columns= df_Region_comuna.iloc[0]
df_Region_comuna = df_Region_comuna.drop(['Codigo region', 'Codigo comuna', 'Poblacion'], axis=1)
df_Region_comuna['Region'] = df_Region_comuna['Region'].map(lambda x: x.rstrip('.1234567890'))
df_Region_comuna = df_Region_comuna.set_index('Comuna')
df_Region_comuna = df_Region_comuna.drop(df_Region_comuna.index[0:1])
mapeo_com_reg = df_Region_comuna.to_dict()
mapeo_com_reg  = list(mapeo_com_reg.values())
mapeo_com_reg  = mapeo_com_reg[0]

### DICCIONARIO {REGION: [COMUNAS]}
df_Region_comuna = df_reg.T
df_Region_comuna = df_Region_comuna.reset_index()
df_Region_comuna.columns= df_Region_comuna.iloc[0]
df_Region_comuna = df_Region_comuna.drop(['Codigo region', 'Codigo comuna', 'Poblacion'], axis=1)
df_Region_comuna['Region'] = df_Region_comuna['Region'].map(lambda x: x.rstrip('.1234567890'))

df_Region_comuna = df_Region_comuna.drop(df_Region_comuna.index[0:1])

df_filtros =  df_Region_comuna.pivot(columns='Region')
df_filtros = df_filtros.apply(lambda x: pd.Series(x.dropna().values))
df_filtros.columns = df_filtros.columns.droplevel(0)
df_filtros = df_filtros.loc[~df_filtros.index.duplicated(keep='second')]

diccionario = df_filtros.to_dict('list')
diccionario_limpio = {k:[elem for elem in v if elem is not np.nan] for k,v in diccionario.items()}

#DICC
todas_opciones = diccionario_limpio

#Formar los fatos por Region/Comuna. Headers
#Agregar fila codigo comuna desde el df original
df_t.loc[-1]=df_reg.iloc[2]
df_t.index = df_t.index +1
df_t.sort_index(inplace=True)
#Limpiar y quitar filas
df_t = df_t.drop(labels=4, axis=0)
df_t = df_t.set_index('Region')
df_t = df_t[:-1]

#df_t.columns = df_t.iloc[0]
#df_t = df_t.drop(labels='Region', axis=0)
cols = []
for col in df_t.iloc[0]:
    cols.append(col)

#cols contiene los codigos de cada comuna

#df_tiempo contiene los casos diarios por comuna (headers = cod comuna)
df_tiempo =df_region.loc[3:,:]
df_tiempo.reset_index()
df_tiempo = df_tiempo[:-1]
df_tiempo = df_tiempo.drop(df_tiempo.index[0])
#df_tiempo = 
df_tiempo =df_tiempo.set_index('Region')
df_tiempo.columns = cols
df_tiempo = df_tiempo.apply(lambda x: pd.to_numeric(x), axis=0) #turn data to float
df_tiempo = df_tiempo.reset_index()
df_tiempo = df_tiempo.rename(columns={'Region':'Fecha'})



##############     Data Nacional   ########################
#### Datos nacional
url_nacional = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto5/TotalesNacionales_T.csv'
df_nacional = pd.read_csv(url_nacional)
df_nacional['Fecha']= pd.to_datetime(df_nacional['Fecha'])
df_nacional = df_nacional.set_index('Fecha')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
##############     Data Nacional   ########################
df_nacional['Casos nuevos sin sintomas'] = df_nacional['Casos nuevos sin sintomas'].fillna(0)
df_nacional = df_nacional.reset_index()


list_of_dates = df_nacional['Fecha'].tolist()


# Datos Comorbilidades
source = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto35/Comorbilidad.csv'
comorbo = pd.read_csv(source)

################################################ Layout Components  #####################################################################

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src="https://upload.wikimedia.org/wikipedia/commons/0/02/Logotipo_del_Instituto_de_Salud_P%C3%BAblica_de_Chile.png",
                            id="img_ministerio",
                            style={
                                "height": "100px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Dashboard COVID-19",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Datos Chile 2020", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Info. Ministerio", id="learn-more-button"),
                            href="https://www.gob.cl/coronavirus/?gclid=EAIaIQobChMIp5XdmNje6QIVRAWRCh1_jAACEAAYASAAEgKqafD_BwE",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.B(
                            "Filtrar por fecha:",
                            className="control_label",
                        ),
                        dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=list_of_dates[0],
                        max_date_allowed=list_of_dates[-1],
                        initial_visible_month=list_of_dates[0],
                        start_date=list_of_dates[0],
                        end_date=list_of_dates[-1],
                        style={'margin-top':'5px'}
                        ),
                        html.Div(id='output-container-date-picker-range', className="control_label"),
                        html.Hr(),
                        html.B("Filtrar por Región:", className="control_label"),
                        dcc.RadioItems(
                            id="filtro-region",
                            options=[
                                {"label": "Todos ", "value": "todos"},
                                {"label": "Personalizado", "value": "personalizado"},
                            ],
                            #value="Metropolitana",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                            inputStyle={'margin-left':'10px', 'margin-right':'5px'}
                        ),
                        dcc.Dropdown(
                            id='seleccion_regiones',
                            options=[{'label':k, 'value': k} for k in todas_opciones.keys()],
                            multi=True,
                            value=list('Metropolitana'),
                            className="dcc_control",
                        ),
                        html.P('Mirar Grafico "Casos Regionales" abajo para ver datos filtrados.', className="subcontrol_label"),
                        html.Hr(),
                        html.B("Filtrar por Comuna: ", className="control_label"),
                        dcc.RadioItems(
                            id="filtro-comuna",
                            options=[
                                {"label": "Personalizado", "value": "personalizado"},
                            ],
                            value="Providencia",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                            inputStyle={'margin-left':'10px', 'margin-right':'5px'}
                        ),
                        dcc.Dropdown(
                            id='seleccion_comunas',
                            multi=True,
                            className="dcc_control",
                            value = list()
                        ),
                        html.P('Mirar Grafico "Casos Comunales" abajo para ver datos filtrados.', className="subcontrol_label"),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.Img(src="https://image.flaticon.com/icons/svg/2922/2922518.svg",style={
                                            "height": "25px",
                                            "width": "25px",
                                            'float':'left',
                                            'padding':'8px',
                                            'margin-right':'10px'
                                            }), html.H6(id="total-casos"), html.P("Casos")],
                                    id="casos",
                                    className="mini_container",
                                ),  
                                html.Div(
                                    [html.Img(src="https://image.flaticon.com/icons/svg/3022/3022870.svg",style={
                                            "height": "25px",
                                            "width": "25px",
                                            'float':'left',
                                            'padding':'8px',
                                            'margin-right':'10px'
                                            }),html.H6(id="total-activos"), html.P("Activos")],
                                    id="Activos",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.Img(src="https://image.flaticon.com/icons/svg/2913/2913465.svg",style={
                                            "height": "25px",
                                            "width": "25px",
                                            'float':'left',
                                            'padding':'8px',
                                            'margin-right':'10px'
                                            }),html.H6(id="casos-nuevos"), html.P("Nuevos")],
                                    id="Nuevos",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.Img(src="https://image.flaticon.com/icons/svg/2242/2242092.svg",style={
                                            "height": "25px",
                                            "width": "25px",
                                            'float':'left',
                                            'padding':'8px',
                                            'margin-right':'10px'
                                            }),html.H6(id="total-muertes"), html.P("Fallecidos")],
                                    id="Fallecidos",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id='grafico-nacional')],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id='grafico_regiones')],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id='grafico_nuevos')],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id='grafico_comunas')],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id='grafico_enfermedades')],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [ html.Div(html.A('Cifras Oficiales, Gobierno de Chile', href= 'https://github.com/MinCiencia/Datos-COVID19/'))],
            id="footer1",
            className="footer-display",
        ),
        html.Div(
            [
                    html.Div(html.A('Joaquin Ruiseñor', href= 'https://www.linkedin.com/in/joaquin-ruise%C3%B1or/'), style={'margin-right':'5px'}),
                    html.Div(html.Img(src="https://www.soydemarketing.com/wp-content/uploads/2015/12/linkedin-logo.png",style={
                                    "height": "25px",
                                    "width": "25px",
                                    }))],
            id="footer2",
            className="footer-display",
        ),
        html.Div(
            [
                    html.Div(html.A('jaruisenor/covid19dash', href= 'https://github.com/jaruisenor/COVID-19_App'), style={'margin-right':'5px'}),
                    html.Div(html.Img(src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",style={
                                    "height": "25px",
                                    "width": "25px",
                                    }))],
            id="footer3",
            className="footer-display"
            ),
        
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

################################################# fin App Layout ###################################################################################
# Helper functions
#Filtra el dataframe por fechas de inicio y termino
def filter_dataframe(df, start_date, end_date):
    filtro= (df['Fecha'] > start_date) & (df['Fecha'] <= end_date)
    df_filtrado = df.loc[filtro]
    return df_filtrado 

#Recibe una lista de regiones y entrega una lista de diccionarios en tuplas
def set_comunas_options(regiones_elegidas):
    filtro=[]
    lista_final=[]
    for i in regiones_elegidas:
        a= [{'label': str(j), 'value': str(j)} for j in diccionario_limpio[str(i)]]
        filtro.append(a)
        for sublista in filtro:
            for item in sublista:
                lista_final.append(item)
    return lista_final

#recibe una lista de diccionarios con las tuplas {region : comuna} y debe entregar una lista de ccomunas
def extraer_comunas(regiones_elegidas):
    lista = []
    for dicc in regiones_elegidas:
        region = dicc['value']
        lista.append(region)
    return lista

#Transforma el df inicial RAW y lo transforma en un dataframe de casos por region
def transformar_casos_region(df):
    df_casos_region = df.drop([1,2,3,0])
    df_casos_region = df_casos_region[:-1]

    #cambiamos nombre fecha
    nombre_fecha = df_casos_region.columns.tolist()
    nombre_fecha[nombre_fecha.index('Region')] = 'Fecha'
    df_casos_region.columns = nombre_fecha

    #Eliminamos lo caracteres en los headers
    lista_headers= df_casos_region.columns.tolist()
    lista_limpia = []
    for col in lista_headers:
        col = col.rstrip('.1234567890')
        lista_limpia.append(col)
    df_casos_region.columns = lista_limpia

    #convertimos a numero
    df_casos_region = df_casos_region.set_index('Fecha')
    df_casos_region= df_casos_region.apply(lambda x: pd.to_numeric(x), axis=1)
    df_casos_region = df_casos_region.reset_index()
    #df_casos_region['Fecha'] = pd.to_datetime(df_casos_region['Fecha'])
    #Agrupamos por region
    df_casos_region= df_casos_region.groupby(df_casos_region.columns, axis=1).sum()
    return df_casos_region

#Transforma el df inicial RAW y lo transforma en un dataframe de casos por COMUNA
def transformar_casos_comuna(df):
    df_casos_comuna = df.drop([2,3,0])
    df_casos_comuna = df_casos_comuna[:-1]

    #Cambiar encabezado
    header = df_casos_comuna.iloc[0]
    df_casos_comuna = df_casos_comuna[1:]
    df_casos_comuna.columns = header

    #cambiamos nombre fecha
    nombre_fecha = df_casos_comuna.columns.tolist()
    nombre_fecha[nombre_fecha.index('Comuna')] = 'Fecha'
    df_casos_comuna.columns = nombre_fecha

    #convertimos a numero
    df_casos_comuna = df_casos_comuna.set_index('Fecha')
    df_casos_comuna= df_casos_comuna.apply(lambda x: pd.to_numeric(x), axis=1)
    df_casos_comuna = df_casos_comuna.reset_index()
    #df_casos_comuna['Fecha'] = pd.to_datetime(df_casos_comuna['Fecha'])
    
    return df_casos_comuna

#Filtra un dataframe por una lista
def filtrar_regiones_elegidas(df, regiones_elegidas):
    final = df[df.columns.intersection(regiones_elegidas)]
    final['Fecha'] = df['Fecha']
    return final

#Filtra un dataframe por una lista
def filtrar_comunas_elegidas(df, comunas_elegidas):
    final = df[df.columns.intersection(comunas_elegidas)]
    final['Fecha'] = df['Fecha']
    return final
    
#Trae la ultima columna de un df al primer lugar
def shift_cols(df):
    cols= list(df.columns)
    cols=[cols[-1]] + cols[:-1]
    df = df[cols]
    return df

#Retorna nombre en siglas de enfermedades
def retornar_siglas(df, diccionario):
    siglas=diccionario.keys()
    nombres_enf=df.iloc[:,0]
    lista_enf=nombres_enf.to_list()
    lista_siglas=[]
    for i in lista_enf:
        for sigla,nombre in diccionario.items():
            if i==nombre:
                lista_siglas.append(sigla)
    return lista_siglas

#############################################################################################################

#CALLBACKS
# Date -> String below
### Callbacks
@app.callback(
    Output('output-container-date-picker-range', 'children'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'Seleccion: '
    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%b %d,  %Y')
        string_prefix = string_prefix + '' + start_date_string + ' | '
    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%b %d,  %Y')
        string_prefix = string_prefix + '' + end_date_string
    if len(string_prefix) == len('Seleccionado: '):
        return 'Selecciona un rango de fechas'
    else:
        return string_prefix

## Radio -> Dropdown (Region)
@app.callback(
    Output("seleccion_regiones", "value"), [Input("filtro-region", "value")]
)
def display_region(selector):
    if selector == "todos":
        return list(todas_opciones.keys())
    elif selector == "personalizado":
        return []
    else:
        return ['Metropolitana', 'Valparaíso']


## Dropdown Region -> Dropdown Comuna
@app.callback(
    Output('seleccion_comunas', 'options'),
    [Input('seleccion_regiones', 'value')])
def set_comunas_options(regiones_elegidas):
    filtro=[]
    lista_final=[]
    for i in regiones_elegidas:
        a= [{'label': str(j), 'value': str(j)} for j in diccionario_limpio[str(i)]]
        filtro.append(a)
        for sublista in filtro:
            for item in sublista:
                lista_final.append(item)
    return lista_final


## Radio -> Dropdown (Comuna)
@app.callback(
    Output("seleccion_comunas", "value"), 
    [Input("filtro-comuna", "value"), Input('seleccion_comunas', 'options')]
)
def display_region(selector, lista_regiones):
    if selector == "personalizado":
        return []
    else:
        return ['Santiago', 'Providencia']



#Total Casos
@app.callback(
    Output("total-casos", "children"),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]
)
def update_total_casos(start_date, end_date):
    dff = filter_dataframe(df_nacional, start_date, end_date)
    df = dff['Casos totales']
    lista_no_vacia=[]
    for i in df:
        if i >= 0:
            lista_no_vacia.append(i)
    non_empty=lista_no_vacia[-1]
    comma = '{:,.0f}'.format(non_empty)
    return comma

#Activos
@app.callback(
    Output("total-activos", "children"),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]
)
def update_total_casos(start_date, end_date):
    dff = filter_dataframe(df_nacional, start_date, end_date)
    df = dff['Casos activos']
    lista_no_vacia=[]
    for i in df:
        if i >= 0:
            lista_no_vacia.append(i)
    non_empty=lista_no_vacia[-1]
    comma = '{:,.0f}'.format(non_empty)
    return comma

#Recuperados
@app.callback(
    Output("casos-nuevos", "children"),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]
)
def update_total_casos(start_date, end_date):

    dff = filter_dataframe(df_nacional, start_date, end_date)
    rec = list(dff['Casos nuevos totales'])
    if dff['Casos nuevos totales'].iloc[-1] is not None:
        return dff['Casos nuevos totales'].iloc[-1]
    else:
        df = dff['Casos nuevos totales']
        df = df.fillna(method='ffill', inplace=True)
        return df.iloc[-1]

#total Muertes
@app.callback(
    Output("total-muertes", "children"),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]
)
def update_total_casos(start_date, end_date):

    dff = filter_dataframe(df_nacional, start_date, end_date)
    df = dff['Fallecidos']
    lista_no_vacia=[]
    for i in df:
        if i >= 0:
            lista_no_vacia.append(i)
    non_empty=lista_no_vacia[-1]
    comma = '{:,.0f}'.format(non_empty)
    return comma



#Date --> Grafico nacional
@app.callback(
    Output('grafico-nacional', 'figure'), 
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')] 
)
def render_graph(start_date, end_date): 
    df_filtrado = filter_dataframe(df_nacional, start_date, end_date)
   
    x = df_filtrado['Fecha']
    y= df_filtrado['Casos totales']
    

    data = [
        dict(
            type="scatter",
            mode="none",
            fill='tozeroy',
            name="Total",
            x=x,
            y=y,
            line=dict(shape="spline", smoothing="2", color="#1527C2"),
        ),
        dict(
            type="scatter",
            mode="none",
            fill='tozeroy',
            name="Activos",
            x=x,
            y=df_filtrado['Casos activos'],
            line=dict(shape="spline", smoothing="2", color="#F8FB10"),
        ),
        dict(
            type="scatter",
            mode="none",
            fill='tozeroy',
            name="Muertes",
            x=x,
            y=df_filtrado['Fallecidos'],
            line=dict(shape="spline", smoothing="2", color="#FF0707"),
        ),
    ]

    layout = go.Layout(
        paper_bgcolor='#f9f9f9',
        plot_bgcolor= '#f9f9f9',
        xaxis = dict(type='date', tickformat = '%d/%m/%Y', dtick=86400000.0 * 15 ,range=[min(x), max(x)]),
        #yaxis = dict(range=[min(y), max(y)]),
        font = dict(color = 'black'),
        title= 'Casos Nacionales',
        legend=dict(
            orientation='h',
            xanchor='center',
            yanchor='top',
            y=1.15,
            x=0.5
        )
        )


    return {'data': data, 'layout': layout}

#Date --> Grafico Casos Nuevos
@app.callback(
    Output('grafico_nuevos', 'figure'), 
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]) 

def render_graph(start_date, end_date): 
    dff = filter_dataframe(df_nacional, start_date, end_date)
   
    x = dff['Fecha']
    y= dff['Casos nuevos totales']

    data= [
        dict(x=x,
            y=y,
            type="bar",
            mode="markers",
            name="Totales",
        ),
        dict(x=x,
            y=dff['Casos nuevos sin sintomas'],
            type="bar",
            mode="markers",
            name="Asintomaticos",
        ),

    ]

    layout_barra = go.Layout(
        paper_bgcolor='#f9f9f9',
        plot_bgcolor= '#f9f9f9',
        xaxis =  dict(type='date', tickformat ='%d/%m/%Y', dtick=86400000.0 * 30 ,range=[min(x), max(x)]),
        yaxis = dict(range=[min(y), max(y)]),
        font = dict(color = 'black'),
        title= 'Casos Nuevos por Día Chile',
        legend=dict(
                orientation='h',
                xanchor='center',
                yanchor='top',
                y=1.15,
                x=0.5
            )
        )

    figure = {'data': data, 'layout': layout_barra}

    return figure

# Date % Dropdown -> Grafico Casos en Region

@app.callback(
    Output('grafico_regiones', 'figure'), 
    [Input('seleccion_regiones', 'value')] 
)
def graph_regiones(regiones_elegidas):
    df = transformar_casos_region(df_region)
    dff= filtrar_regiones_elegidas(df, regiones_elegidas)
    #dff = shift_cols(dataframe)
    if len(regiones_elegidas)== 0:
        data = []
        layout = go.Layout(
            paper_bgcolor='#f9f9f9',
            plot_bgcolor= '#f9f9f9',
            xaxis =  dict(type='date', tickformat = '%d/%m/%Y', dtick=86400000.0 * 30 ,range=[min(x), max(x)]),
            #yaxis = dict(range=[min(y), max(y)]),
            font = dict(color = 'black'),
            title= 'Casos Regiones (Seleccionar una region)',
            legend=dict(
                orientation='h',
                xanchor='center',
                yanchor='top',
                #y=1.15,
                #x=0.5
            )
            )
        return {'data': data, 'layout': layout}
    elif  len(regiones_elegidas) !=  0:
        #primero armamos el dataframe que pasaremos
        #ejex.index = np.arange(1, len(ejex)+1)
        #x = dff.index
        #y= dff['Atacama']
        lista_columnas = dff.columns.to_list()
        vacia=[]
        data=[]
        for col in lista_columnas[:-1]:
            l = dff[str(col)].to_list()
            n= str(col)
            vacia.append((n,l))
        for j in vacia:
            d= dict(
                    type="line",
                    name=str(j[0]),
                    x=dff['Fecha'],
                    y=j[1],
                    fill='tozeroy',
                    #line=dict(shape="spline", smoothing="2", color="#1527C2"),
                )
            data.append(d)

        layout = dict(
            title='Casos Regionales',
            font = dict(color = 'black'),
            xaxis= dict(type='date', tickformat = '%d/%m/%Y', dtick=86400000.0 * 30 ),
            paper_bgcolor='#f9f9f9',
            plot_bgcolor= '#f9f9f9',
            )
        
        
        return {'data': data, 'layout': layout}

#Dropdown -> Casos Comunas
@app.callback(
    Output('grafico_comunas', 'figure'), 
    [Input('seleccion_comunas', 'value')] 
)
def graph_regiones(comunas_elegidas):
    df = transformar_casos_comuna(df_region)
    dff= filtrar_comunas_elegidas(df, comunas_elegidas)
    #dff = shift_cols(dataframe)

    if len(comunas_elegidas)== 0:
        data = []
        layout = go.Layout(
            paper_bgcolor='#f9f9f9',
            plot_bgcolor= '#f9f9f9',
            xaxis = dict(type='date', tickformat = '%d/%m/%Y', dtick=86400000.0 * 30),
            #yaxis = dict(range=[min(y), max(y)]),
            font = dict(color = 'black'),
            title= 'Casos Comunas (seleccionar comuna)',
            legend=dict(
                orientation='h',
                xanchor='center',
                yanchor='top',
                #y=1.15,
                #x=0.5
            )
            )
        return {'data': data, 'layout': layout}
    elif  len(comunas_elegidas) !=  0:
        #primero armamos el dataframe que pasaremos
        #ejex.index = np.arange(1, len(ejex)+1)
        #x = dff.index
        #y= dff['Atacama']
        lista_columnas = dff.columns.to_list()
        vacia=[]
        data=[]
        for col in lista_columnas[:-1]:
            l = dff[str(col)].to_list()
            n= str(col)
            vacia.append((n,l))
        for j in vacia:
            d= dict(
                    type="line",
                    name=str(j[0]),
                    x=dff['Fecha'],
                    y=j[1],
                )
            data.append(d)

        layout = dict(
            title='Casos Comunas',
            font = dict(color = 'black'),
            xaxis = dict(type='date', tickformat = '%d/%m/%Y', dtick=86400000.0 * 30 ),
            paper_bgcolor='#f9f9f9',
            plot_bgcolor= '#f9f9f9',
            )
        
        
        return {'data': data, 'layout': layout}
    else:
        data = []
        layout = go.Layout(
            paper_bgcolor='#f9f9f9',
            plot_bgcolor= '#f9f9f9',
            xaxis = dict(type='date', tickformat = '%d/%m/%Y', dtick=86400000.0 * 30 ),
            #yaxis = dict(range=[min(y), max(y)]),
            font = dict(color = 'black'),
            title= 'Casos Comunas (seleccionar comuna)',
            legend=dict(
                orientation='h',
                xanchor='center',
                yanchor='top',
                #y=1.15,
                #x=0.5
            )
            )
        return {'data': data, 'layout': layout}

#Date --> Grafico Enfermedades
@app.callback(
    Output('grafico_enfermedades', 'figure'), 
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]) 

def enfermedades_graph(start_date, end_date): 
    df = comorbo
    lista_siglas = retornar_siglas(df, ENFERMEDADES)
    enfermedad = lista_siglas
    hospitalizacion = list(df['Hospitalización'])
    columnas = df.columns
    ultima = columnas[-1]
    nro_hosp = list(df[ultima])
    ultima_col = str(ultima)


    #insertar centro de grafico
    #enfermedad.insert(0,'Total')
    #hospitalizacion.insert(0,'')
    #nro_hosp.insert(0,60000)

    #fig = px.sunburst(data, names='character', parents='parent', value='value',)
    #fig =go.Figure(go.Sunburst(df, path=['Hospitalización','Comorbilidad'], values='2020-06-01'))
    fig = px.sunburst(df, path=['Hospitalización','Comorbilidad'], values=str(ultima), branchvalues='total',color='Comorbilidad', title='Comorbilidades Hospitalizados/No Hospitalizados',
            hover_data=['2020-06-01'])
    fig.update_layout(
        #margin = dict(t=30, l=30, r=30, b=30),
        paper_bgcolor='#f9f9f9',
        plot_bgcolor= '#f9f9f9',
            )

    fig.update_traces(hovertemplate=None) 
    fig.update_layout(title={
        'text': "Comorbilidades Hospitalizados/No Hospitalizados",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font = dict(color = 'black')
        )

    return fig


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
