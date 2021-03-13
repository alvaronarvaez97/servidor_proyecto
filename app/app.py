import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import os
import csv
import analitica_descriptiva

def save(data):
    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(data)

file_name = "data/data_base.csv"
headers = ["","Date","sensor","value"]
if not os.path.isfile(file_name):
    save(headers)

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

def get_options():
    dict_list = []
    dict_list.append({"label": "Temperatura", "value": "Temperatura"})

    dict_list.append({"label": "Maximo", "value": "Maximo"})
    dict_list.append({"label": "Minimo", "value": "Minimo"})

    dict_list.append({"label": "Mediana", "value": "Mediana"})
    dict_list.append({"label": "Promedio", "value": "Promedio"})

    dict_list.append({"label": "Desviacion", "value": "Desviacion"})
    dict_list.append({"label": "Tendencia", "value": "Tendencia"})
    
    return dict_list


app.layout = html.Div(
    children=[
        html.Div(className="row",
                 children=[
                    html.Div(className="four columns div-user-controls",
                             children=[
                                 html.H2("DASH - Series de Tiempo"),
                                 html.P("Visualizador de sieries de tiempo con Plotly - Dash."),
                                 html.P("Selecciones una o más series en la lista."),
                                 html.Div(
                                     className="div-for-dropdown",
                                     children=[
                                         dcc.Dropdown(id="sensorselctor", options=get_options(),
                                                      multi=True, value=["Temperatura"],
                                                      style={"backgroundColor": "#1E1E1E"},
                                                      className="sensorselctor"
                                                      ),
                                     ],
                                     style={"color": "#1E1E1E"})
                                ]
                             ),
                    html.Div(className="eight columns div-for-charts bg-grey",
                             children=[
                                 dcc.Graph(id="timeseries", config={"displayModeBar": False}, animate=True)
                             ])
                              ])
        ]

)


# Callback for timeseries price
@app.callback(Output("timeseries", "figure"),
              [Input("sensorselctor", "value")])
def update_graph(selected_dropdown_value):
    # renenovar datos
    df = analitica_descriptiva.update(file_name)
    df.index = pd.to_datetime(df["Date"], format="%d/%m/%y %H:%M:%S")
    trace1 = []
    df_sub = df
    for stock in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub["sensor"] == stock].index,
                                 y=df_sub[df_sub["sensor"] == stock]["value"],
                                 mode="lines",
                                 opacity=0.7,
                                 name=stock,
                                 textposition="bottom center"))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {"data": data,
              "layout": go.Layout(
                  # Colores de salida
                  colorway=["#22C2D3", "#FF0043", "#00FF3C", "#5E0DAC", "#375CB1", "#FF7400", "#420690", "#f5a7f2"],
                  template="plotly_dark",
                  paper_bgcolor="rgba(0, 0, 0, 0)",
                  plot_bgcolor="rgba(0, 0, 0, 0)",
                  margin={"b": 15},
                  hovermode="x",
                  autosize=True,
                  title={"text": "Visualización", "font": {"color": "white"}, "x": 0.5},
                  xaxis={"range": [df_sub.index.min(), df_sub.index.max()]},
              ),

              }

    return figure


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
