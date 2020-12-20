import os


def download_data(
    latitude,
    longitude,
    date_from,
    date_to,
    folder_name,
    cloud_value: int,
    records_per_image: str = 1,
):
    os.system(
        "python ./CREODIAS_client/client.py -f -s Sentinel2 -l LEVEL1C -r 1 -c "
        + str(cloud_value)
        + " -p "
        + str(longitude)
        + ","
        + str(latitude)
        + " -t "
        + date_from
        + " -e "
        + date_to
        + " -n "
        + folder_name
    )
    return
