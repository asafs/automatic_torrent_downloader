
from SeriesUtils import *
from LocalFilesUtil import *


update_series_to_download()
series_to_download = get_series_to_download()
for serie in series_to_download:
    get_links_for_series(serie, to_download=True)


#TODO: Add move of file to NAS after finish download
#TODO: find subtitle
#TODO: Run with schedule
#TODO: GUI (Web UI?) to manage this
#TODO: add preffered quality for each searies
