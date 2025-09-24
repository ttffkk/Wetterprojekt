from dwd_downloader import DWDDownloader
from dwd_data_processor import DWDDataProcessor

if __name__ == '__main__':
    # 1. Download the data
    downloader = DWDDownloader()
    downloader.run(limit=5) # Using a limit for demonstration

    # 2. Process the downloaded data
    #processor = DWDDataProcessor()
    #processed_data = processor.run()

    # 3. Display a sample of the final data
    #if not processed_data.empty:
     #   print("\n--- Sample of Final Processed Data ---")
     #   print(processed_data.head())
      #  print("\n-------------------------------------")

    print("\nFull data import and processing workflow finished.")
