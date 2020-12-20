import base64
import datetime
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
from dash.dependencies import Input, Output, State
from flask import Flask, url_for
from tensorflow.keras.preprocessing import image

from functions.from_id_pipeline_no_imports import (converter, cord_reader,
                                                   get_photo_from_id)
from functions.model_functions import predict_with_loaded_model

UPLOAD_DIRECTORY = "/save_images"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

true = html.Span(id="true", className="icon", children="✔️")
false = html.Span(id="false", className="icon", children="❌")


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

@server.route("/imgs/<path:path>")
def images(path):
    fullpath = "./imgs/" + path
    resp = flask.make_response(open(fullpath).read())
    resp.content_type = "image/jpg"
    return resp

def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


app.layout = html.Div(
    id="container",
    children=[
        html.Div(id="banner", children=[html.H1("ARiMR - rozpoznawanie rzepaku 🌾")]),
        html.Div(
            id="div_1",
            children=[
                html.H2("1. Na podstawie zdjęcia"),
                dcc.Upload(
                    id="upload-image",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "50%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    # Allow multiple files to be uploaded
                    multiple=True,
                ),
                html.Div(id="output-image-text"),
                html.Div(id="output-image-upload"),
                html.Br(),
                html.Button("Oceń", id="button_photo"),
                dcc.Loading(
                    id="loading-1",
                    children=[html.Div(id="ocena_photo", className="ocena")],
                    type="circle",
                ),
            ],
        ),
        html.Div(
            id="div_2",
            children=[
                html.H2("2. Podaj numer działki"),
                dcc.Input(
                    id="numer_dzialki",
                    value="",
                    type="text",
                    placeholder="Numer działki",
                ),
                html.Br(),
                html.Br(),
                html.Div(
                    id="wrapper_iframe_photo",
                    children=[
                        html.Iframe(
                            id="iframe_map",
                            style={
                                "width": "300px",
                                "height": "300px",
                            },
                            hidden=True,
                        ),
                        html.Img(id = "cuted_image")
                    ],
                ),
                html.Br(),
                html.Button("Oceń", id="button_number"),
                dcc.Loading(
                    id="loading-2",
                    children=[html.Div(id="ocena_id", className="ocena")],
                    type="circle",
                ),
            ],
        ),
    ],
)


def add_image_from_photo_content(first_photo_content):
    return html.Div([html.Img(src=first_photo_content, style={"height": "auto", "width": "auto"})])


@app.callback(
    Output("output-image-upload", "children"),
    Output("output-image-text", "children"),
    Input("upload-image", "contents"),
)
def update_output(photo_content):
    if photo_content is not None:
        first_photo_content = photo_content[0]
        html_image = [add_image_from_photo_content(first_photo_content)]
        save_file("example_photo.png", first_photo_content)
        return html_image, html.H3("Wgrane zdjęcie:")
    else:
        return None, None


@app.callback(
    Output("iframe_map", "src"),
    Output("iframe_map", "hidden"),
    Input("button_number", "n_clicks"),
    State("numer_dzialki", "value"),
)
def update_iframe(button_clicks, id_dzialki):
    if button_clicks is not None:

        dict_coordinates = cord_reader([id_dzialki])
        str_coordinates = dict_coordinates[id_dzialki][0]
        splitted_str_coordinates = str_coordinates.split(" ")

        x_puwg_coord = splitted_str_coordinates[1]
        y_puwg_coord = splitted_str_coordinates[0]

        x, y = converter(x_puwg_coord, y_puwg_coord)
        x = str(float(x))
        y = str(float(y))

        src = "https://maps.google.com/maps?q= " + y + ", " + x + "&z=15&output=embed"
        return src, False
    else:
        return None, True


@app.callback(Output("ocena_photo", "children"), Input("button_photo", "n_clicks"))
def update_output_based_on_photo(button_clicks):
    if button_clicks is not None:
        files = uploaded_files()
        is_rzepak = predict_with_loaded_model(
            photo_path=os.path.join(UPLOAD_DIRECTORY, files[0]), model_path="trained_NN"
        )
        if is_rzepak == 0:
            is_rzepak = True
        else:
            is_rzepak = False
        if is_rzepak:
            return [true, html.P(className="ocena_text", children="To jest rzepak!")]
        else:
            return [
                false,
                html.P(className="ocena_text", children="To nie jest rzepak!"),
            ]
    else:
        return [None, None]

def save_file_from_bytes(name, photo_in_bytes):
    """Decode and store an image from byes."""
    data = photo_in_bytes.split(b";base64,")
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data[0]))

@app.callback(
    Output("ocena_id", "children"),
    Output("cuted_image", "src"),
    Input("button_number", "n_clicks"),
    Input("numer_dzialki", "value"),
)
def update_output_based_on_id(button_clicks, numer_dzialki):
    if button_clicks is not None:
        get_photo_from_id(numer_dzialki)
        encoded_image = base64.b64encode(open("./cuted_photo.jpg", 'rb').read())
        print(open("./cuted_photo.jpg", 'rb').read())
        save_file_from_bytes("cuted_photo_gui.jpg", open("./cuted_photo.jpg", 'rb').read())
        print(uploaded_files())
        is_rzepak = predict_with_loaded_model(
            photo_path="./cuted_photo.jpg", model_path="trained_NN"
        )
        if is_rzepak == 0:
            is_rzepak = True
        else:
            is_rzepak = False
        if is_rzepak:
            return [
                true,
                html.P(className="ocena_text", children="Na działce znajduje się rzepak!"),
            ], html.Img(src='data:image/jpg;base64,{}'.format(encoded_image))
        else:
            return [
                false,
                html.P(className="ocena_text", children="Na działce nie ma rzepaku!"),
            ], html.Img(src='data:image/jpg;base64,{}'.format(encoded_image))
    else:
        return None, None


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=5000, debug=True)
