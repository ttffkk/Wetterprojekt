import os
import zipfile
import glob
import pandas as pd

class DWDDataProcessor:
    """Handles unzipping, filtering, and parsing of DWD data files."""
    def __init__(self, download_dir="data", extract_dir="data/unzipped"):
        self.download_dir = download_dir
        self.extract_dir = extract_dir

    def unzip_and_filter_files(self):
        """Unzips all .zip files, extracting only the data file, and then deletes the zip."""
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        zip_files = glob.glob(os.path.join(self.download_dir, "*.zip"))
        if not zip_files:
            print("No .zip files found to process.")
            return

        print(f"Found {len(zip_files)} zip files to process.")

        for zip_file_path in zip_files:
            file_name = os.path.basename(zip_file_path)
            print(f"Processing {file_name}...")
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    product_file = None
                    for file_in_zip in zip_ref.namelist():
                        if 'produkt_' in file_in_zip:
                            product_file = file_in_zip
                            break
                    
                    if product_file:
                        zip_ref.extract(product_file, self.extract_dir)
                        print(f"  - Extracted: {product_file}")
                    else:
                        print(f"  - Warning: No 'produkt_' file found in {file_name}")

                os.remove(zip_file_path)
                print(f"  - Deleted: {file_name}")

            except zipfile.BadZipFile:
                print(f"Error: Failed to unzip {file_name}. It might be a corrupted file.")
            except OSError as e:
                print(f"Error processing file {file_name}: {e}")

    def find_header_line(self, file_path):
        """Finds the line number of the header in a DWD data file."""
        with open(file_path, 'r', encoding='latin-1') as f:
            for i, line in enumerate(f):
                if 'STATIONS_ID' in line:
                    return i
        return None

    def parse_data_files(self):
        """Parses all data files in the extract directory and returns a single DataFrame."""
        data_files = glob.glob(os.path.join(self.extract_dir, "produkt_*.txt"))
        if not data_files:
            print("No data files found to parse.")
            return pd.DataFrame()

        all_data = []
        print(f"Found {len(data_files)} data files to parse.")

        for file_path in data_files:
            print(f"Parsing {os.path.basename(file_path)}...")
            try:
                header_line_index = self.find_header_line(file_path)
                if header_line_index is None:
                    print(f"  - Warning: Could not find header row in {os.path.basename(file_path)}. Skipping.")
                    continue

                df = pd.read_csv(
                    file_path, 
                    delimiter=';',
                    encoding='latin-1',
                    skiprows=header_line_index
                )

                df.columns = df.columns.str.strip()
                df.replace(-999, pd.NA, inplace=True)
                all_data.append(df)

            except Exception as e:
                print(f"  - Error parsing file {os.path.basename(file_path)}: {e}")

        if not all_data:
            print("No data could be parsed.")
            return pd.DataFrame()

        full_df = pd.concat(all_data, ignore_index=True)
        print("\nSuccessfully parsed and combined all data files.")
        return full_df

    def run(self):
        """Runs the complete data processing workflow."""
        print("\nStarting data processing...")
        self.unzip_and_filter_files()
        print("\nFile extraction and cleanup finished.")
        
        print("\nStarting data parsing...")
        parsed_data = self.parse_data_files()
        if not parsed_data.empty:
            print("\nData parsing finished successfully.")
        else:
            print("\nData parsing did not yield any data.")
        return parsed_data
