import pandas as pd
import numpy as np
import os

# ----------------------------------------------------------------------
# File paths for input and output
# ----------------------------------------------------------------------

# The raw CSV file we got from Camelot extraction
CAMELOT_OUTPUT_FILE = 'processed_cutoff_data_new1.csv'

# The final cleaned file that will be used for calculations
FINAL_PROCESSED_FILE = 'final_zscore_data_new_01.csv' 

# ----------------------------------------------------------------------

def clean_course_name(name):
    
    #Break the combined 'Course\n(Uni)' string into two separate columns
    
    if isinstance(name, str) and '\n' in name:
        # Split only once to get the course and uni names
        parts = name.split('\n', 1) 
        course = parts[0].strip()
        # Clean up brackets from uni name
        university = parts[1].strip().replace('(', '').replace(')', '')
        return pd.Series([course, university])
    
    # If there's no newline, just return the course name
    return pd.Series([name, ''])

def process_table_block(df_block):  
    
    # Clean and organize each course table
    
    # Set the first column to 'District'
    df_block.rename(columns={df_block.columns[0]: 'District'}, inplace=True)
    
    # Remove empty rows
    df_block.dropna(subset=['District'], inplace=True)
    
    # Change the table layout to organize courses and Z-scores
    id_vars = ['District']
    value_vars = df_block.columns[1:].tolist() # All columns starting from the second one
    
    df_long = pd.melt(
        df_block, 
        id_vars=id_vars, 
        value_vars=value_vars,
        var_name='Course_University', 
        value_name='Z_Score_Str'
    )
    
    # Clean the Z-Score and change it to a number
    df_long['Z_Score'] = pd.to_numeric(
        df_long['Z_Score_Str'].replace({'NQC': np.nan, '-': np.nan, 'NQC ': np.nan}), 
        errors='coerce' # Change invalid Z-scores (like 'NQC') to empty values
    )
    
    # Drop the temporary string column
    df_long.drop(columns=['Z_Score_Str'], inplace=True)
    
    # Divide the Course_University column into two
    df_long[['Course', 'University']] = df_long['Course_University'].apply(clean_course_name)
    
    # Drop the original Course_University column
    df_long.drop(columns=['Course_University'], inplace=True)
    
    # Keep only the columns we need and remove any empty rows
    final_columns = ['Course', 'University', 'District', 'Z_Score']
    df_final = df_long[final_columns].copy()
    
    # Remove any rows with missing Z-score values(NQC or other missing values)
    df_final.dropna(subset=['Z_Score'], inplace=True)

    return df_final


def process_camelot_output_revised(csv_file_path):
    
    #Reads the CSV file, finds the data tables, and organizes them into a clear list with District, Course, and Z-Score
    try:
        # Read the CSV file raw, without setting any column names
        df_full = pd.read_csv(csv_file_path, header=None)
    except FileNotFoundError:
        print(f"Error: Input file '{csv_file_path}' not found.")
        return None
    
    print(f"Successfully loaded full data from '{csv_file_path}'. Starting multi-block processing...")
    
    # Identify the start of each course section by looking for title rows
    # These rows (like MEDICINE) act as markers before the data begins
    
    header_indices = df_full[df_full.iloc[:, 1].apply(lambda x: isinstance(x, str) and '\n' in x)].index.tolist()
    
    # Include the last row of the file as the final limit
    header_indices.append(len(df_full)) 

    all_processed_data = []

    # Go through each course section one by one
    for i in range(len(header_indices) - 1):
        start_row = header_indices[i]
        end_row = header_indices[i+1]
        
        # Use the first row as the table header
        # The data starts from start_row + 1
        
        # extract the actual data starting from the next row
        # .iloc[start_row] selects the row to be the column names

        df_block = df_full.iloc[start_row + 1 : end_row].copy()
        df_block.columns = df_full.iloc[start_row]
        
        # Reset row numbers to start from 0 for this new section
        df_block.reset_index(drop=True, inplace=True)
        
        # Clean and organize this section, then add it to our final list
        processed_block = process_table_block(df_block)
        all_processed_data.append(processed_block)

    # Merge all cleaned course sections into one single table
    if not all_processed_data:
        print("Warning: No data blocks were successfully identified or processed.")
        return None

    df_final_combined = pd.concat(all_processed_data, ignore_index=True)
    
    # 7. Remove Duplicates
    # Remove rows that have the same (Course, University, District) combination
    df_final_combined.drop_duplicates(
        subset=['Course', 'University', 'District'], 
        keep='first', 
        inplace=True
    )
    
    # Save the final DataFrame
    df_final_combined.to_csv(FINAL_PROCESSED_FILE, index=False)
    
    print("\n---------------------------------------------------------")
    print(f"✅ Data Processing Successful! Clean data saved to '{FINAL_PROCESSED_FILE}'.")
    print(f"Total processed cutoff entries: {len(df_final_combined)}")
    print("---------------------------------------------------------")
    print("\nFirst 10 rows of the Final Processed Data (Long Format):")
    print(df_final_combined.head(10))
    
    print(f"\n*Next Step: Implement the Weighted Scoring Algorithm using the '{FINAL_PROCESSED_FILE}' file.*")
    
    return df_final_combined

if __name__ == "__main__":
    process_camelot_output_revised(CAMELOT_OUTPUT_FILE)