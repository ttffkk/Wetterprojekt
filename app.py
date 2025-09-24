from data_importer import DWDDataImporter

if __name__ == '__main__':
    # Create an instance of the importer
    importer = DWDDataImporter()

    # Run the import process, downloading and unzipping the first 5 files for demonstration
    importer.run_import(limit=5)

    print("\nProcess finished. The data is available in the 'data' and 'data/unzipped' directories.")
