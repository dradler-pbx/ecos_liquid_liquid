import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go

import pandas as pd
import numpy as np

axis_template = {
    "showbackground": True,
    "backgroundcolor": "#ffffff",
    "gridcolor": "rgb(255, 255, 255)",
    "zerolinecolor": "rgb(255, 255, 255)",
}

plot_layout = {
    "title": "",
    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    "font": {"size": 12, "color": "white"},
    "showlegend": False,
    "plot_bgcolor": "#ffffff",
    "paper_bgcolor": "#ffffff",
    "scene": {
        "xaxis": axis_template,
        "yaxis": axis_template,
        "zaxis": axis_template,
        "aspectratio": {"x": 1, "y": 1.2, "z": 1},
        "camera": {"eye": {"x": 1.25, "y": 1.25, "z": 1.25}},
        "annotations": [],
    },
}

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True

df = pd.read_pickle(r'C:\Users\dominik\Python\projects\OperationalEnvelope_Postprocessing\data.pkl')
filename = 'operation_envelope_pickle'

parameters = df.columns.to_list()
parameters.remove('T_hotside_in')
parameters.remove('T_coldside_in')
parameters.remove('cpr_speed')

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('PBX', style={'font': 'bold 35px Poppins', 'color': 'white', 'display': 'inline'}),
            html.Label('Colibri', style={'font': '35px Poppins', 'color': 'white', 'display': 'inline'}),
            html.Label(filename, style={'font': '12px Poppins', 'color': 'white','display': 'inline', 'padding-left': '30px'}),],
            style={'background-color': '#ffffff', 'padding-left': '10px'}
        ),
        html.Div([
            html.Div([dcc.Graph(id='mainGraph', figure={'data.csv': [], 'layout': {'display': 'none'}}, style={'height': '100%', })
                      ], style={'width': '60%', 'height': '100%', 'float': 'left'}),
            html.Div([
                html.Div('test', id='Graph1', style={'height': '33.33%'}),
                html.Div('test', id='Graph2', style={'height': '33.33%'}),
                html.Div('test', id='Graph3', style={'height': '33.33%'})
            ],
                style={'width': '40%', 'float': 'left', 'background-color': '#ffffff'})
        ],
            style={'flex-grow': '1', 'display': 'flex', 'flew-flow': 'row'}
        )
    ], style={'display': 'flex', 'flex-flow': 'column', 'height': '100vh', 'flex-grow': '1'}),
    html.Div([
        html.Div([
            html.Label('x-Axis:', style={'color': 'white'}),
             dcc.Dropdown(
                 id='xaxis_dd',
                 options=[{'label': 'Hotside temperature', 'value': 'T_hotside_in'},
                          {'label': 'Coldside temperature', 'value': 'T_coldside_in'},
                          {'label': 'Compressor speed', 'value': 'cpr_speed'}],
                 value='T_coldside_in'
             )]),
        html.Div([
            html.Label('y-Axis:', style={'color': 'white'}),
                 dcc.Dropdown(
                     id='yaxis_dd',
                     options=[{'label': 'Hotside temperature', 'value': 'T_hotside_in'},
                              {'label': 'Coldside temperature', 'value': 'T_coldside_in'},
                              {'label': 'Compressor speed', 'value': 'cpr_speed'}],
                     value='cpr_speed'
                 )]),
        html.Div(id='third_parameter_name', children=[
            html.Label('Third parameter:', style={'color': 'white'}),
            dcc.Dropdown(
                id='third_parameter_checklist',
                options=[],
                value=[],
                multi=True
            )],
                 style={'margin-top': '20px'}
        ),
        html.Div(children=[
            html.Label('Parameters', style={'color': 'white'}),
            dcc.Dropdown(id='parameters',
                         options=parameters,
                         value=[],
                         multi=True)],
        style={'margin-top': '20px'})
    ], style={'width': '250px', 'background-color': '#ffffff', 'padding-left': '10px', 'padding-right': '10px', 'padding-top': '30px'})
], style={'display': 'flex', 'flex-flow': 'row', 'height': '100vh', 'width': '100vw'})




@app.callback(Output('mainGraph', 'figure'),
              [Input('xaxis_dd', 'value'),
               Input('yaxis_dd', 'value'),
               Input('third_parameter_checklist', 'value'),
               Input('parameters', 'value')])
def update_graph(xaxis, yaxis, third_para_check, parameters):
    # print(third_para_check, parameters)
    if third_para_check is not None and parameters is not None:
        data = []
        for third_para_name in df.columns[0:3]:
            if third_para_name not in [xaxis, yaxis]:
                break
        idx = 0

        for third_para in third_para_check:
            # print(third_para)
            dff = df[df[third_para_name] == third_para]
            for parameter in parameters:
                x_list = dff.drop_duplicates(subset=xaxis, keep='first')[xaxis].values
                y_list = dff.drop_duplicates(subset=yaxis, keep='first')[yaxis].values
                z_data = np.zeros([y_list.size, x_list.size])

                for i, x in enumerate(x_list):
                    z_data[:, i] = dff[dff[xaxis] == x_list[i]][parameter].values

                data.append(go.Surface(x=x_list, y=y_list, z=z_data, showscale=False, name=third_para))

        layout = {
            "title": "",
            "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
            "font": {"size": 12, "color": "#000000"},
            "showlegend": False,
            "plot_bgcolor": "#ffffff",
            "paper_bgcolor": "#ffffff",
            "scene": {
                "xaxis": {
                    "showbackground": True,
                    "backgroundcolor": "#ffffff",
                    "gridcolor": "#000000",
                    "zerolinecolor": "#000000",
                    "title": xaxis
                },
                "yaxis": {
                    "showbackground": True,
                    "backgroundcolor": "#ffffff",
                    "gridcolor": "#000000",
                    "zerolinecolor": "#000000",
                    "title": yaxis
                },
                "zaxis": {
                    "showbackground": True,
                    "backgroundcolor": "#ffffff",
                    "gridcolor": "#000000",
                    "zerolinecolor": "#000000",
                    "title": ''.join(parameters)
                },
                "aspectratio": {"x": 1, "y": 1.2, "z": 1},
                "camera": {"eye": {"x": 1.25, "y": 1.25, "z": 1.25}},
                "annotations": [],
            },
        }
        #     go.Layout(
        #     scene={
        #         'xaxis': {'title': xaxis}, 'yaxis': {'title': yaxis}, 'zaxis': {'title': ''.join(parameters)}
        #     }
        # )

        return go.Figure(data=data, layout=layout)
    else:
        return {'data.csv':[],'layout': {'display': 'none'}}

@app.callback(Output('third_parameter_checklist', 'options'),
              [Input('xaxis_dd', 'value'),
               Input('yaxis_dd', 'value')])
def update_third_parameter_list(xaxis, yaxis):
    for third_para in df.columns[0:3]:
        if third_para not in [xaxis, yaxis]:
            break
    options_list = df.drop_duplicates(subset=third_para, keep='first')[third_para]
    unit = 'rpm' if third_para == 'n_CPR_target' else '°C'
    return [{'label': ''.join([str(option), unit]), 'value': option} for option in options_list]


@app.callback([Output('Graph1', 'children'),
               Output('Graph2', 'children'),
               Output('Graph3', 'children')],
              [Input('mainGraph', 'clickData')],
              [State('xaxis_dd', 'value'),
               State('yaxis_dd', 'value'),
               State('third_parameter_checklist', 'value'),
               State('parameters', 'value')])
def update_side_graphs(clickData, xaxis, yaxis, third_parameter_value, parameters):
    print(clickData)
    # find third parameter, it is the one, that is not xaxis nor yaxis ;)
    for third_para in df.columns[0:3]:
        if third_para not in [xaxis, yaxis]:
            break

    # if somebody clicked, let's start:
    if clickData is not None:
        data_x = []
        data_y = []
        data_z = []
        for parameter_value in third_parameter_value:
            for parameter in parameters:
                # filter the df by the click data.csv for the xaxis -> yaxis and third parameter constant
                dff_x = df[(df[yaxis] == clickData['points'][0]['y']) & (df[third_para] == parameter_value)]
                data_x.append(go.Scatter(x=dff_x[xaxis], y=dff_x[parameter], name=parameter_value))
                # [{
                #     'x': dff_x[xaxis],
                #     'y': dff_x[parameter],
                #     'name': parameter_value
                # } for parameter in parameters])
                # print(data_x)

                # same as for x
                dff_y = df[(df[xaxis] == clickData['points'][0]['x']) & (df[third_para] == parameter_value)]
                data_y.append(go.Scatter(x=dff_y[yaxis], y=dff_y[parameter], name=parameter_value))
                #     [{
                #     'x': dff_y[yaxis],
                #     'y': dff_y[parameter],
                #     'name': parameter_value
                # } for parameter in parameters])

            # same as for x, but only for one loop (3rd parameter value loop is not necessary)
            dff_z = df[(df[xaxis] == clickData['points'][0]['x']) & (df[yaxis] == clickData['points'][0]['y'])]
            data_z.append(go.Scatter(x=dff_z[third_para], y=dff_z[parameter], name=parameter))

            layout_x = go.Layout(title=''.join([yaxis,': ', str(clickData['points'][0]['y']),' | ', third_para,': ', str(third_parameter_value[0])]), xaxis={'title': xaxis, 'showgrid': False, 'zeroline': False}, yaxis={'title': parameters[0], 'showgrid': False, 'zeroline': False}, font={'size': 10, 'color': '#000000'}, margin={'l': 10, 'r': 10, 't': 30, 'b': 10}, paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
            layout_y = go.Layout(title=''.join([xaxis,':', str(clickData['points'][0]['x']),' | ', third_para,': ', str(third_parameter_value[0])]), xaxis={'title': yaxis, 'showgrid': False, 'zeroline': False}, yaxis={'title': parameters[0], 'showgrid': False, 'zeroline': False}, font={'size': 10, 'color': '#000000'}, margin={'l': 10, 'r': 10, 't': 30, 'b': 10}, paper_bgcolor="#ffffff", plot_bgcolor='#ffffff')
            layout_z = go.Layout(title=''.join([xaxis,': ', str(clickData['points'][0]['x']),' | ', yaxis,': ', str(clickData['points'][0]['y'])]), xaxis={'title': third_para, 'showgrid': False, 'zeroline': False}, yaxis={'title': parameters[0], 'showgrid': False, 'zeroline': False}, font={'size': 10, 'color': '#000000'}, margin={'l': 10, 'r': 10, 't': 30, 'b': 10}, paper_bgcolor="#ffffff", plot_bgcolor='#ffffff')

        return [dcc.Graph(figure=go.Figure(data=data_x, layout=layout_x), style={'height': '100%'}),
                dcc.Graph(figure=go.Figure(data=data_y, layout=layout_y), style={'height': '100%'}),
                dcc.Graph(figure=go.Figure(data=data_z, layout=layout_z), style={'height': '100%'})]
    else:
        return [' ']*3
    # return ['Please select a data.csv point']*3


if __name__ == '__main__':
    app.run_server(debug=True)
