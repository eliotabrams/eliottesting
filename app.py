# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots


#https://towardsdatascience.com/a-gentle-invitation-to-interactive-visualization-with-dash-a200427ccce9
#https://dash.plot.ly/getting-started
# Deploy on https://www.heroku.com/students
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

fig = make_subplots(rows=1, cols=3)

app.layout = html.Div(children=[
    html.H2(children='Coronavirus'),

    html.Div(children=[
        html.Label('Case Fatality Rate'),
        dcc.Input(id="CFR", type="number", value=0.01, min=0, max=0.1, step=0.001),

        html.Label('Crisis CFR'),
        dcc.Input(id="CCFR", type="number", value=0.05, min=0, max=0.15, step=0.001),

        html.Label('Fraction Critical'),
        dcc.Input(id="criticalFraction", type="number", value=0.03, min=0, max=0.15, step=0.01),

        html.Label('Infection Period'),
        dcc.Input(id="infectionPeriod", type="number", value=14, min=5, max=20, step=1),

        html.Label('Testing Rate'),
        dcc.Input(id="testingRate", type="number", value=0.05, min=0, max=1, step=0.05),

        html.Label('Transmission'),
        dcc.Input(id="transmission", type="number", value=2, min=0, max=5, step=0.1),

        html.Label('Capacity Surge'),
        dcc.Input(id="capacity", type="number", value=1, min=0, max=2, step=0.1)
    ], style={'display':'flex', 'justify-content':'space-around', 'flex-wrap':'wrap'}),
    # https://css-tricks.com/snippets/css/a-guide-to-flexbox/

    html.Div(dcc.Graph(id = 'plot', figure = fig))

    ])


@app.callback(Output('plot', 'figure'),
            [Input('CFR', 'value'),
             Input('CCFR', 'value'),
             Input('criticalFraction', 'value'),
             Input('infectionPeriod', 'value'),
             Input('testingRate', 'value'),
             Input('transmission', 'value'),
             Input('capacity', 'value')])
def update_figure(CFR,CCFR,criticalFraction,infectionPeriod,testingRate,transmission,capacity):
    rho = transmission
    normalCaseFatalityRate = 1-(1-CFR*testingRate)**(1/infectionPeriod)
    crisisCaseFatalityRate = 1-(1-CCFR*1/(1+capacity/5)*testingRate)**(1/infectionPeriod)
    #(1-x)^infectionPeriod = 1-y 

    N = 327.2 * 1e6
    I, R, D, H = 10000, 0, 0, 0
    S = N - I - R
    notoverwhelmed = True

    Is, Rs, Ds, Hs, Ss, nIs, nHs, nDs, nRs = [], [], [], [], [], [], [], [], []

    for t in np.arange(0, 365):
        newInfections = min((I - H)*(rho/infectionPeriod * S/N), S) #Improve and add distancing
        newHospitalizations = newInfections*criticalFraction
        newDeaths = H*normalCaseFatalityRate*notoverwhelmed + H*crisisCaseFatalityRate*(not notoverwhelmed)
        newRecoveries = (I - newDeaths) * 1/infectionPeriod
        
        I = I + newInfections - newRecoveries - newDeaths
        R += newRecoveries
        D += newDeaths
        H = H + newHospitalizations - H*1/infectionPeriod - newDeaths
        S = N - I - R - D

        if H > 200000*(1+capacity):
            notoverwhelmed = False

        Is.append(I)
        Rs.append(R)
        Ds.append(D)
        Hs.append(H)
        Ss.append(S)
        nIs.append(newInfections)
        nHs.append(newHospitalizations)
        nDs.append(newDeaths)
        nRs.append(newRecoveries)


    fig = make_subplots(rows=1, cols=3, specs=[[{"secondary_y": False},{"secondary_y": False},{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=np.arange(365), y=Is, name="Infections"), row=1, col=1)
    fig.add_trace(go.Scatter(x=np.arange(365), y=np.array(Is)*testingRate, name="Cases"), row=1, col=2)
    fig.add_trace(go.Scatter(x=np.arange(365), y=Hs, name="Hospitalizations"), row=1, col=2)
    fig.add_shape(type="line",x0=0, y0=200000, x1=365, y1=200000, line=dict(color="Gray",dash="dashdot"), row=1, col=2)
    fig.add_shape(type="line",x0=0, y0=200000*(1+capacity), x1=365, y1=200000*(1+capacity), line=dict(color="Gray",dash="dashdot"), row=1, col=2)
    fig.add_trace(go.Scatter(x=np.arange(365), y=Ds, name="Deaths"), row=1, col=3)
    fig.add_trace(go.Scatter(x=np.arange(365), y=nDs, name="New Deaths"), secondary_y=True, row=1, col=3)
    # fig.add_trace(go.Scatter(x=np.arange(365), y=np.array(nIs)*testingRate, name="New Cases"), row=1, col=3)
    # fig.add_trace(go.Scatter(x=np.arange(365), y=nHs, name="New Hospitalizations"), row=1, col=3)
    # fig.add_trace(go.Scatter(x=np.arange(365), y=nDs, name="New Deaths"), row=1, col=3)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


