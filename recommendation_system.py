import pandas as pd
import numpy as np
import os

# ----------------------------------------------------------------------
# CONFIGURATION AND TUNABLE WEIGHTS (Parameters you can change easily)
# ----------------------------------------------------------------------
# ⚠️ NEW: List of all Z-Score data files (for 3 years)
ZSCORE_DATA_FILES = [
    'final_zscore_data_new_03.csv',  # 2022-2023 
    'final_zscore_data_new_02.csv',  # 2023-2024 
    'final_zscore_data_new_01.csv' # 2024-2025
]
RECOMMENDATION_COUNT = 10 

# 1. Z-SCORE MARGIN WEIGHTS
MAX_ZSCORE_MARGIN_CAP = 0.2 

# 2. PREFERENCE BOOST SCORES
PRIMARY_BOOST_VALUE = 1.0 
SECONDARY_BOOST_VALUE = 0.5 
BASE_BOOST_VALUE = 0.1 

# 3. OVERALL WEIGHTS (Must sum to 1.0)
WEIGHT_MARGIN = 0.5 
WEIGHT_PREFERENCE = 0.5 

# ⚠️ NEW: Stream-to-Course-Keyword Mapping for Eligibility Filtering
#  ['Science', 'Technology', 'Arts', 'Commerce', 'Mathamatics']
STREAM_COURSE_MAP = {
    'Science': ['Medicine', 'Dental', 'Veterinary', 'Science', 'Bio', 'Health', 'Nursing', 'Pharmacy'],
    'Technology': ['Technology', 'Engineering', 'Architecture', 'Design', 'Surveying'],
    'Arts': ['Arts', 'Law', 'Languages', 'Sociology', 'Archaeology', 'Social'],
    'Commerce': ['Management', 'Accounting', 'Business', 'Finance', 'Commerce'],
    'Mathamatics': ['Engineering', 'IT', 'Computer', 'Statistics', 'Quantity Surveying', 'Applied Science'] 
    # Note: 'Mathamatics' stream is often broadly categorized into Physical Science courses.
}

# ----------------------------------------------------------------------


def load_data(file_paths):
    """
    Loads Z-Score data from multiple years, consolidates it, and 
    calculates the average Z-Score cutoff for each course.
    """
    all_years_df = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Error: Data file '{file_path}' not found. Please ensure all data files are present.")
            return None
        
        df = pd.read_csv(file_path)
        all_years_df.append(df)
    
    # Combine all data into a single DataFrame
    combined_df = pd.concat(all_years_df, ignore_index=True)
    
    # ⚠️ FIX STEP 1: Keep ONLY the required columns before grouping
    required_cols = ['Course', 'University', 'District', 'Z_Score']
    
    for col in required_cols:
        if col not in combined_df.columns:
            print(f"Warning: Column '{col}' not found in one of the data files. Cannot proceed.")
            return None # Error if critical columns are missing
    
    combined_df = combined_df[required_cols].copy() 
    
    # Key columns for identifying a unique cutoff entry
    group_keys = ['Course', 'University', 'District']
    
    # Calculate the average Z_Score 
    combined_df['Avg_Z_Score'] = combined_df.groupby(group_keys)['Z_Score'].transform('mean')
    
    # Keep only one row per unique entry
    final_avg_df = combined_df.drop_duplicates(subset=group_keys, keep='first').copy()
    
    # ⚠️ FIX STEP 2: Drop the original 'Z_Score' column before renaming 'Avg_Z_Score'
    if 'Z_Score' in final_avg_df.columns:
        final_avg_df.drop(columns=['Z_Score'], inplace=True)
        
    # Rename the calculated average column
    final_avg_df.rename(columns={'Avg_Z_Score': 'Z_Score'}, inplace=True)
    
    # Keep only the necessary columns
    return final_avg_df[['Course', 'University', 'District', 'Z_Score']].copy()
    

def calculate_compatibility_score(student_z_score, district, primary_field, secondary_field, stream, df_cutoffs):
    """
    Calculates a compatibility score for all eligible courses based on 
    Z-Score margin (now using the average Z-Score) and student preferences.
    """
    if df_cutoffs is None:
        return pd.DataFrame()

    eligible_df = df_cutoffs.copy()
    
    # 1. Stream Eligibility Filtering (NEW LOGIC)
    
    stream_keywords = STREAM_COURSE_MAP.get(stream, [])
    
    if stream_keywords:
        # Create a regex pattern to search for any of the stream-relevant keywords
        pattern = '|'.join(stream_keywords)
        
        # Filter the DataFrame to include only courses matching the student's stream keywords
        stream_filter_mask = eligible_df['Course'].str.contains(pattern, case=False, na=False)
        eligible_df = eligible_df[stream_filter_mask].copy()
        
    if eligible_df.empty:
        # If no courses match the stream, return an empty DataFrame immediately
        print(f"No courses found matching the '{stream}' stream criteria.")
        return pd.DataFrame()

    # 2. Filter by District: Find the cutoff for the student's district (e.g., 'COLOMBO')
    district_cutoff_df = eligible_df[eligible_df['District'].str.upper() == district.upper()].copy()

    if district_cutoff_df.empty:
        print(f"Warning: No cutoff data found for district: {district} after Stream filtering.")
        return pd.DataFrame()

    merged_df = district_cutoff_df.copy()
    
    # 3. Z-Score Eligibility and Margin Calculation (Uses the 'Z_Score' which is now the Average)
    
    # Check if the student's Z-Score meets or exceeds the course cutoff
    merged_df['Is_Eligible'] = merged_df['Z_Score'] <= student_z_score
    
    # Calculate the Safety Margin 
    merged_df['Safety_Margin'] = student_z_score - merged_df['Z_Score']
    
    # Apply the CAP for the Margin Score calculation (only positive margins are used)
    merged_df['Capped_Margin'] = np.clip(merged_df['Safety_Margin'], 0, MAX_ZSCORE_MARGIN_CAP)
    
    # Normalize the Capped Margin (Scaled to 0 to 1)
    merged_df['Margin_Score'] = merged_df['Capped_Margin'] / MAX_ZSCORE_MARGIN_CAP
    
    # --- WEIGHTED SCORING ---
    
    # 4. Preference Boost Calculation
    merged_df['Preference_Boost'] = BASE_BOOST_VALUE # Give a base boost to all stream-eligible courses
    
    # Primary Field Match 
    if primary_field:
        primary_mask = merged_df['Course'].str.contains(primary_field, case=False, na=False)
        merged_df.loc[primary_mask, 'Preference_Boost'] = PRIMARY_BOOST_VALUE

    # Secondary Field Match 
    if secondary_field and secondary_field.lower() != primary_field.lower():
        secondary_mask = merged_df['Course'].str.contains(secondary_field, case=False, na=False)
        # Apply secondary boost only if it didn't get the primary boost
        merged_df.loc[~primary_mask & secondary_mask, 'Preference_Boost'] = SECONDARY_BOOST_VALUE
        
    # 5. Final Weighted Score Calculation
    # The final score is a weighted average of normalized margin and preference boost.
    merged_df['Compatibility_Score'] = (merged_df['Margin_Score'] * WEIGHT_MARGIN) + \
                                       (merged_df['Preference_Boost'] * WEIGHT_PREFERENCE)

    # 6. Final Filtering and Ranking
    
    # Filter only for eligible courses (where Z-Score meets or exceeds cutoff)
    recommended_df = merged_df[merged_df['Is_Eligible'] == True].copy()
    recommended_df = recommended_df.sort_values(by='Compatibility_Score', ascending=False)
    final_recommendations = recommended_df.head(RECOMMENDATION_COUNT)
    
    # Ensure Safety Margin displays the true margin (not the capped value)
    final_recommendations['Safety_Margin'] = final_recommendations['Safety_Margin'].round(4)
    
    output_columns = ['Course', 'University', 'Z_Score', 'District', 'Compatibility_Score', 'Safety_Margin']
    
    return final_recommendations[output_columns]

def run_recommendation_demo():
    """Runs a demonstration of the recommendation system."""
    
    # Load the cleaned data (using the list of files now)
    df_cutoffs = load_data(ZSCORE_DATA_FILES)
    if df_cutoffs is None:
        return

    print(f"\nData loaded successfully. Total cutoff entries (Averaged): {len(df_cutoffs)}")
    print("--------------------------------------------------------------------")
    
    # --- DEMO STUDENT INPUTS---
    
    STUDENT_INPUTS = {
        'Z_Score': 1.8500,
        'District': 'COLOMBO',
        'Primary_Field': 'Computer', 
        'Secondary_Field': 'Information', 
        'Stream': 'Mathamatics' # Mathamatics stream 
    }
    
    print(f"Analyzing recommendations for: Z-Score={STUDENT_INPUTS['Z_Score']}, District={STUDENT_INPUTS['District']}, Primary Preference='{STUDENT_INPUTS['Primary_Field']}', Stream='{STUDENT_INPUTS['Stream']}'")
    
    # Run the core recommendation function
    recommendations = calculate_compatibility_score(
        student_z_score=STUDENT_INPUTS['Z_Score'],
        district=STUDENT_INPUTS['District'],
        primary_field=STUDENT_INPUTS['Primary_Field'],
        secondary_field=STUDENT_INPUTS['Secondary_Field'],
        stream=STUDENT_INPUTS['Stream'],
        df_cutoffs=df_cutoffs
    )
    
    if recommendations.empty:
        print("\n😔 Sorry, no eligible courses found based on the inputs.")
    else:
        print("\n ✅ TOP RECOMMENDED COURSES (Ranked by Compatibility Score):")
        recommendations['Compatibility_Score'] = recommendations['Compatibility_Score'].round(3)
        print(recommendations.reset_index(drop=True))

if __name__ == "__main__":
    run_recommendation_demo()