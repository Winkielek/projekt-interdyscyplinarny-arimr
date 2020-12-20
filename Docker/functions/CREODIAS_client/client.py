import sys
import getopt
import datetime

from CloudferroRemoteClient import CloudferroRemoteClient

creodias = {"big": "45.130.30.32", "small": "45.130.31.37", "uni": "45.130.31.49"}


def main(argv):
    help_msg = (
        "client.py <parameters>\n"
        "parameters:\n"
        "-d, --download\t- Only download prepared directory\n"
        "-f, --find\t\t- Find, prepare, and download data\n"
        "-x, --delete\t- Delete one of prepared directories\n"
        "-s, --satellite=\t- Collection name, default Sentinel2\n"
        "-l, --proc_level=\t Processing level, default LEVEL1C\n"
        "-r, --records=\t\t- Max records to prepare, default 10, max 2000\n"
        "-c, --cloud=\t\t- Max cloud coverage [0-100], default 50\n"
        "-p, --position=\t\t- Position in format longitude,latitude, "
        "default 19.399459879775495,50.981258660659165\n"
        "-t, --start_date=\t- Start date in format yyyy-mm-dd, default 2014-08-01\n"
        "-e, --end_date=\t\t- End date in format yyyy-mm-dd, current date\n"
        "-i, --diff_days=\t- Diff in days counted since end date, optional >0\n"
        "-z, --resize=\t- divide image size by factor or select width and height to rescale all images\n"
        "eg. -z 2 will shrink width and height of all images by 2\n"
        "-n, --name=\t- string added to directory, empty by default\n"
        "-z (100, 100) will resize all images to 100 width and 100 height"
    )

    end_date_passed = False

    arguments = {
        "satellite": "Sentinel2",
        "proc_level": "LEVEL1C",
        "records": "10",
        "cloud": "50",
        "position": "19.399459879775495,50.981258660659165",
        "start_date": "2014-08-01T00:00:00",
        "end_date": datetime.datetime.now().isoformat().split(".")[0],
        "diff_days": "",
        "name": "_",
        "resize": "0",
    }

    flags = {"only_download": False, "full_prepare": False, "delete": False}

    try:
        opts, args = getopt.getopt(
            argv,
            "hdfxs:r:c:p:t:e:i:l:z:n:",
            [
                "help, download, find, delete, satellite=",
                "records=",
                "clouds=",
                "position=",
                "start_date=",
                "end_date=",
                "diff_days=",
                "proc_level=",
                "resize=",
                "name=",
            ],
        )
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(help_msg)
            sys.exit(2)
        elif opt in ("-d", "--download"):
            flags["only_download"] = True
            break
        elif opt in ("-x", "--delete"):
            flags["delete"] = True
            break
        elif opt in ("-f", "--find"):
            flags["full_prepare"] = True
        elif opt in ("-s", "--satellite"):
            arguments["satellite"] = arg
        elif opt in ("-r", "--records"):
            arguments["records"] = arg
        elif opt in ("-c", "--cloud"):
            arguments["cloud"] = arg
        elif opt in ("-p", "--position"):
            arguments["position"] = arg
        elif opt in ("-t", "--start_date"):
            arguments["start_date"] = arg
        elif opt in ("-e", "--end_date"):
            arguments["end_date"] = arg
            end_date_passed = True
        elif opt in ("-d", "--diff_date"):
            if end_date_passed:
                arguments["diff_date"] = arg
            else:
                print("ERROR: No end date passed")
                sys.exit(2)
        elif opt in ("-l", "--proc_level="):
            arguments["proc_level"] = arg
        elif opt in ("-n", "--name="):
            arguments["name"] = arg
        elif opt in ("-z", "--resize="):
            arguments["resize"] = arg

    acc = 0
    for item in flags:
        if flags[item]:
            acc += 1
    if acc == 0 or acc > 1:
        print(
            "Select prepare mode (-f, --find) or download mode (-d, --download) or delete mode (-x, --delete)"
        )
        exit(0)

    cloudferro_remote = CloudferroRemoteClient(
        creodias["uni"], "./functions/CREODIAS_client/keys/uni_key", ignore_check=True
    )

    if flags["only_download"]:
        cloudferro_remote.download_prepared()
    if flags["delete"]:
        cloudferro_remote.remove_data()
    if flags["full_prepare"]:
        cloudferro_remote.find_prepare_and_download(arguments)


if __name__ == "__main__":
    main(sys.argv[1:])
