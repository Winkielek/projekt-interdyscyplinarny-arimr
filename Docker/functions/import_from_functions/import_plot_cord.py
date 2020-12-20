import requests
from shapely import wkb

# A BTW WOLNE STRASZNIE DA SIĘ TO JAKOŚ PRZYŚPIESZYĆ UŻYWJAĆ SESIJ ALE TO TODO


def cord_reader(plot_ids_list):
    # Taking list contaings plots ID as strings
    # example ["260101_5.0037.569"]

    # Return dictionary with plots ID as key and
    # cords of plot as value

    # data check

    if not isinstance(plot_ids_list, list):
        raise Exception("List object is required")
    if not isinstance(plot_ids_list[0], str):
        raise Exception("List didnt contains only strings")

    list_of_cords = []

    for i in plot_ids_list:
        # ganerated with https://curl.trillworks.com/

        response1 = requests.get(
            "https://uldk.gugik.gov.pl/?request=GetParcelById&id=" + i
        )  # WKB

        hexlocation = response1.text[2 : len(response1.text) - 1]
        point = wkb.loads(hexlocation, hex=True)
        x_y = point.exterior.coords.xy

        cords = []
        for i in range(len(x_y[0])):
            cords.append(str(x_y[0][i]) + " " + str(x_y[1][i]))
        list_of_cords.append(cords)

    res = dict(zip(plot_ids_list, list_of_cords))

    return res


# c= cord_reader(["021804_5.0003.98"])
# from PUWG_1992_converter import   converter
# c=c.get("021804_5.0003.98")[0]

# x,y = converter(float(c.split(" ")[1]),float(c.split(" ")[0]))
# print(x,y)
