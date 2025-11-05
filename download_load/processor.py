import os
import zipfile
import glob
import pandas as pd
from geopy.distance import geodesic

class DataProcessor:
    """Handles unzipping, filtering, and parsing of data files."""
    def __init__(self, download_dir, extract_dir, file_encoding, na_value):
        self.download_dir = download_dir
        self.extract_dir = extract_dir
        self.file_encoding = file_encoding
        self.na_value = na_value

    def process_file(self, zip_file_path, file_pattern_to_extract, header_keyword, delimiter):
        """Processes a single zip file: unzips, parses, and renames to CSV."""
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

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
                    extracted_file_path = zip_ref.extract(product_file, self.extract_dir)
                    print(f"  - Extracted: {product_file}")
                else:
                    print(f"  - Warning: No file matching '{file_pattern_to_extract}' found in {file_name}")
                    return None

            header_line_index = self._find_header_line(extracted_file_path, header_keyword)
            if header_line_index is None:
                print(f"  - Warning: Could not find header row in {os.path.basename(extracted_file_path)}. Skipping.")
                return None

            df = pd.read_csv(
                extracted_file_path,
                delimiter=delimiter,
                encoding=self.file_encoding,
                skiprows=header_line_index
            )

            df.columns = df.columns.str.strip()
            df.replace(self.na_value, pd.NA, inplace=True)

            if extracted_file_path.endswith('.txt'):
                new_file_path = os.path.splitext(extracted_file_path)[0] + ".csv"
                # Write the dataframe to a new csv file
                df.to_csv(new_file_path, index=False, sep=delimiter)
                print(f"  - Renamed to {os.path.basename(new_file_path)}")
                os.remove(extracted_file_path)
                return new_file_path
            else:
                # if it is already a csv, we just overwrite it with the cleaned data
                df.to_csv(extracted_file_path, index=False, sep=delimiter)
                return extracted_file_path

        except zipfile.BadZipFile:
            print(f"Error: Failed to unzip {file_name}. It might be a corrupted file.")
            return None
        except OSError as e:
            print(f"Error processing file {file_name}: {e}")
            return None
        except Exception as e:
            print(f"  - Error parsing file {os.path.basename(zip_file_path)}: {e}")
            return None

    def _find_header_line(self, file_path, header_keyword):
        """Finds the line number of the header in a data file."""
        with open(file_path, 'r', encoding=self.file_encoding) as f:
            for i, line in enumerate(f):
                if header_keyword in line:
                    return i
        return None

    @staticmethod
    def calculate_distance(coord1, coord2):
        """Calculates the distance between two coordinates in kilometers."""
        return geodesic(coord1, coord2).kilometers
