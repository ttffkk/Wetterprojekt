import os
import zipfile
import glob
import pandas as pd

class DataProcessor:
    """Handles unzipping, filtering, and parsing of data files."""
    def __init__(self, download_dir, extract_dir, file_encoding, na_value):
        self.download_dir = download_dir
        self.extract_dir = extract_dir
        self.file_encoding = file_encoding
        self.na_value = na_value

    def unzip_and_filter_files(self, file_pattern_to_extract, zip_glob):
        """Unzips all .zip files, extracting only files matching the pattern, and then deletes the zip."""
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        zip_files = glob.glob(os.path.join(self.download_dir, zip_glob))
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
                        if file_pattern_to_extract in file_in_zip:
                            product_file = file_in_zip
                            break
                    
                    if product_file:
                        zip_ref.extract(product_file, self.extract_dir)
                        print(f"  - Extracted: {product_file}")
                    else:
                        print(f"  - Warning: No file matching '{file_pattern_to_extract}' found in {file_name}")

                os.remove(zip_file_path)
                print(f"  - Deleted: {file_name}")

            except zipfile.BadZipFile:
                print(f"Error: Failed to unzip {file_name}. It might be a corrupted file.")
            except OSError as e:
                print(f"Error processing file {file_name}: {e}")

    def find_header_line(self, file_path, header_keyword):
        """Finds the line number of the header in a data file."""
        with open(file_path, 'r', encoding=self.file_encoding) as f:
            for i, line in enumerate(f):
                if header_keyword in line:
                    return i
        return None

    def parse_data_files(self, file_glob, header_keyword, delimiter):
        """Parses all data files in the extract directory and returns a single DataFrame."""
        data_files = glob.glob(os.path.join(self.extract_dir, file_glob))
        if not data_files:
            print("No data files found to parse.")
            return pd.DataFrame()

        all_data = []
        print(f"Found {len(data_files)} data files to parse.")

        for file_path in data_files:
            print(f"Parsing {os.path.basename(file_path)}...")
            try:
                header_line_index = self.find_header_line(file_path, header_keyword)
                if header_line_index is None:
                    print(f"  - Warning: Could not find header row in {os.path.basename(file_path)}. Skipping.")
                    continue

                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding=self.file_encoding,
                    skiprows=header_line_index
                )

                df.columns = df.columns.str.strip()
                df.replace(self.na_value, pd.NA, inplace=True)
                all_data.append(df)

                if file_path.endswith('.txt'):
                    new_file_path = os.path.splitext(file_path)[0] + ".csv"
                    os.rename(file_path, new_file_path)
                    print(f"  - Renamed to {os.path.basename(new_file_path)}")

            except Exception as e:
                print(f"  - Error parsing file {os.path.basename(file_path)}: {e}")

        if not all_data:
            print("No data could be parsed.")
            return pd.DataFrame()

        full_df = pd.concat(all_data, ignore_index=True)
        print("\nSuccessfully parsed and combined all data files.")
        return full_df

    def run(self, file_pattern_to_extract, file_glob, header_keyword, delimiter, zip_glob):
        """Runs the complete data processing workflow."""
        print("\nStarting data processing...")
        self.unzip_and_filter_files(file_pattern_to_extract, zip_glob)
        print("\nFile extraction and cleanup finished.")
        
        print("\nStarting data parsing...")
        parsed_data = self.parse_data_files(file_glob, header_keyword, delimiter)
        if not parsed_data.empty:
            print("\nData parsing finished successfully.")
        else:
            print("\nData parsing did not yield any data.")
        return parsed_data
