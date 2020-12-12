import datetime

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

true = html.Span(id = "true", className = "icon", children = "✔️")
false = html.Span(id = "false", className = "icon", children = "❌")

app.layout = html.Div(
    id = "container",
    children = [
        html.Div(
            id = 'banner',
            children = [
                html.H1("ARiMR - rozpoznawanie rzepaku 🌾")
            ]
        ),
        html.Div(
            id = "div_1",
            children = [
                html.H2("1. Na podstawie zdjęcia"),
                dcc.Upload(
                    id='upload-image',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '50%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                html.Div(id="output-image-text"),
                html.Div(id='output-image-upload'),
                html.Button('Oceń', id='button_photo'),
                html.Div(id='ocena_photo', className = 'ocena'),
            ]
        ),
        html.Div(
            id = "div_2",
            children = [
                html.H2("2. Podaj numer działki"),
                dcc.Input(id='numer_dzialki', value='', type='text',placeholder="Numer działki"),
                html.Br(),
                html.Br(),
                html.Button('Oceń ', id='button_number'),
                html.Div(id='ocena_id', className = 'ocena')
        ])]
)


def parse_contents(contents):
    return html.Div([
        html.Img(src=contents,style={'height':'auto', 'width':'auto'})
    ])


@app.callback(Output('output-image-upload', 'children'),
              Output('output-image-text', "children"),
              Input('upload-image', 'contents'))
def update_output(photo):
    if photo is not None:
        photo = photo[0]
        children = [parse_contents(photo)]
        return children, html.H3("Wgrane zdjęcie:")



@app.callback(Output('ocena_photo', 'children'),
              Input('button_photo', 'n_clicks')
              )
def update_output_based_on_photo(baton_clicks):
    if baton_clicks!=None:
        is_rzepak = False
        if is_rzepak:
            return [true, html.P(className='ocena_text', children = 'To jest rzepak!')]
        else:
            return [false, html.P(className='ocena_text', children='To nie jest rzepak!')]


@app.callback(Output('ocena_id', 'children'),
              Input('button_number', 'n_clicks'),
              Input('numer_dzialki', 'value'))
def update_output_based_on_id(baton_clicks, numer_dzialki):
    if baton_clicks!=None:
        is_rzepak = True
        if is_rzepak:
            return [true, html.P(className='ocena_text', children = 'Na działce znajduje się rzepak!')]
        else:
            return [false, html.P(className='ocena_text', children='Na działce nie ma rzepaku!')]

if __name__ == '__main__':
    app.run_server(debug=True)