from wetter.downloader import Downloader
from wetter.processor import DataProcessor

if __name__ == '__main__':
    # Configuration for the DWD data source
    DWD_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
    ZIP_PATTERN = r'href="(tageswerte_KL_.*?\.zip)"'
    PRODUCT_PATTERN_TO_EXTRACT = 'produkt_'
    DATA_FILE_GLOB = "produkt_*.txt"
    HEADER_KEYWORD = 'STATIONS_ID'
    DELIMITER = ';'

    # 1. Download the data
    downloader = Downloader(url=DWD_URL)
    downloader.run(pattern=ZIP_PATTERN, limit=5)  # Using a limit for demonstration

    # 2. Process the downloaded data
    processor = DataProcessor()
    processed_data = processor.run(
        file_pattern_to_extract=PRODUCT_PATTERN_TO_EXTRACT,
        file_glob=DATA_FILE_GLOB,
        header_keyword=HEADER_KEYWORD,
        delimiter=DELIMITER
    )



    print("\nFull data import and processing workflow finished.")
