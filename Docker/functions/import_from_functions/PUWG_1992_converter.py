import pyproj

def converter(x_in,y_in):

    input_proj = pyproj.Proj(init='epsg:2180')
    output_proj = pyproj.Proj(init="epsg:4326")

    x_out, y_out = pyproj.transform(input_proj, output_proj, y_in, x_in)
    return (x_out, y_out)

