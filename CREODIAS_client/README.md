# Cloudferro Client

Simple client for satellite data selection using CloudFerro infrastructure

## Examples

To prepare and download data
~~~
python3 client.py -f -s Sentinel2 -l LEVEL1C -r 50 -c 20 -p 19.399459879775495,50.981258660659165
~~~

To download prepared data
~~~
python3 client.py -d
~~~

To remove prepared data
~~~
python3 client.py -x
~~~

## Program arguments
|Short|Long         |Description                                          |Default                                 |
|-----|-------------|-----------------------------------------------------|----------------------------------------|
|-d   |--download   |Download data flag                                   |                                        |
|-f   |--find       |Preparing data flag                                  |                                        |
|-x   |--delete     |Delete data flag                                     |                                        |
|-s   |--satellite= |Collection name                                      |Sentinel2                               |
|-r   |--records=   |Max records to prepare, max 2000                     |10                                      |
|-c   |--cloud=     |Max cloud coverage [0-100]                           |50                                      |
|-l   |--proc_level=|Processing level of selected collection              |LEVEL2A                                 |
|-p   |--position=  |Position in format longitude,latitude                |19.399459879775495,50.981258660659165   |
|-t   |--start_date=|Start date in format yyyy-mm-dd                      |2014-08-01                              |
|-e   |--end_date=  |End date in format yyyy-mm-dd                        |Current date                            |
|-d   |--diff_days= |Diff in days counted since end date, optional, value>0|                                       |
|-z   |--resize=    |if value < 128, it divides current images width and height by the value, for greater values it resizes images to new size as follows: new_width=resize, new_height=resize| |
|-n   |--name=      |user string added to directory name                  |                                        |