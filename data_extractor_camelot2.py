import camelot
import pandas as pd
import os


# BASIC INPUTS

PDF_FILE_PATH = '2023_2024_Z_Score.pdf' 
OUTPUT_CSV_FILE = 'processed_cutoff_data_new2.csv' 
PAGE_RANGE = '1-10' 
def extract_tables_with_camelot(pdf_path):
    """
    Extract tables from the PDF file using the Camelot library
    The 'lattice' method is used for tables with clear border
    """
    if not os.path.exists(pdf_path):
        print(f"Error: Input file '{pdf_path}' not found.")
        return None

    all_dataframes = []
    
    try:
        print(f"Starting table extraction from '{pdf_path}'...")
        
        # Use this for tables with clear border 
        # Try the 'stream' method if no tables are found
        
        tables = camelot.read_pdf(
            pdf_path, 
            flavor='lattice', 
            pages=PAGE_RANGE  # Extract all pages
        )

        if tables.n == 0:
            print("Warning: Camelot could not identify any tables using 'lattice'. Switching to 'stream' method and trying again.")
            tables = camelot.read_pdf(
                pdf_path, 
                flavor='stream', 
                pages=PAGE_RANGE
            )
        
        if tables.n == 0:
            print("\nError: Could not identify tables using either 'lattice' or 'stream' methods. The manual's structure may be too complex.")
            return None

        print(f"\nCamelot successfully identified {tables.n} tables.")

        # Convert all tables into Pandas DataFrames and join them
        for i, table in enumerate(tables):
            df = table.df
            # Delete empty rows
            df.dropna(how='all', inplace=True) 
            if not df.empty:
                all_dataframes.append(df)
                print(f"Table {i+1} - Rows: {len(df)}")
        
        # Join all data into one table
        if all_dataframes:
            final_df = pd.concat(all_dataframes, ignore_index=True)
            
            # Save the final DataFrame as a CSV
            final_df.to_csv(OUTPUT_CSV_FILE, index=False, header=True)
            print(f"\nAll table data successfully saved to '{OUTPUT_CSV_FILE}'.")
            print("Use this CSV file as the source for your Data Processing step (Step 3).")
            print("\nFirst few rows of the DataFrame:")
            print(final_df.head())
            return final_df
        
        return None

    except Exception as e:
        print(f"An error occurred during Camelot execution: {e}")
        return None

if __name__ == "__main__":
    extract_tables_with_camelot(PDF_FILE_PATH)