import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(layout="wide")

# Importing your recommendation_system file and the file list
# We import ZSCORE_DATA_FILES to pass the list of 3-year files to load_data
from recommendation_system import load_data, calculate_compatibility_score, ZSCORE_DATA_FILES

# --- 1. CONFIGURATION ---
# District Options
DISTRICT_OPTIONS = [
    'COLOMBO', 'GAMPAHA', 'KALUTARA', 'MATHALE', 'KANDY', 'NUWARA ELIYA', 'GALLE', 
    'MATARA', 'HAMBANTHOTA', 'JAFFNA', 'KILINOCHCHI', 'MANNAR', 'MULLAITIVU', 
    'VAVUNIYA', 'TRINCOMALEE', 'BATTICALOA', 'AMPARA', 'PUTTALAM', 'KURUNAGALA', 
    'ANURADHAPURA', 'POLONNARUWA', 'BADULLA', 'MONARAGALA', 'KEGALLE', 'RATHNAPURA'
]
PRIMARY_FIELD_OPTIONS = ['MEDICINE', 'DENTAL SURGERY', 'VETERINARY SCIENCE', 'BIOCHEMISTRY & MOLECULAR BIOLOGY', 'AGRICULTURAL TECHNOLOGY & MANAGEMENT', 'AGRICULTURE', 'FOOD SCIENCE & NUTRITION', 'FOOD SCIENCE & TECHNOLOGY', 'BIOLOGICAL SCIENCE', 'APPLIED SCIENCES (BIO.SC)', 'ENGINEERING', 'ENGINEERING (EM)', 'ENGINEERING (TM)', 'QUANTITY SURVEYING', 'COMPUTER SCIENCE', 'PHYSICAL SCIENCE', 'SURVEYING SCIENCE', 'APPLIED SCIENCES (PHY.SC)', 'MANAGEMENT', 'REAL ESTATE MANAGEMENT & VALUATION', 'COMMERCE', 'MANAGEMENT AND PUBLIC POLICY', 'BUSINESS INFORMATION SYSTEMS', 'FINANCIAL ENGINEERING', 'BANKING & INSURANCE', 'SERVICE MANAGEMENT', 'LAW', 'ARTS *', 'ARTS (SP) / MASS MEDIA* #', 'ARTS (SP) / PERFORMING ARTS * #','ACCOUNTING INFORMATION SYSTEMS', 'AGRICULTURAL RESOURCE MANAGEMENT AND', 'AGRICULTURAL TECHNOLOGY & MANAGEMENT', 'AGRICULTURE', 'AGRI BUSINESS MANAGEMENT', 'ANIMAL PRODUCTION AND FOOD TECHNOLOGY', 'ANIMAL SCIENCE & FISHERIES', 'APPLIED CHEMISTRY', 'APPLIED SCIENCES (BIO.SC)', 'APPLIED SCIENCES (PHY.SC)', 'AQUATIC BIORESOURCES', 'ARABIC LANGUAGE *', 'ARCHITECTURE #', 'ARTS *', 'ARTS (SAB) - A * [ARTS STREAM]', 'ARTS (SAB) - B * [COMMERCE STREAM]', 'ARTS (SP) / MASS MEDIA* #', 'ARTS (SP) / PERFORMING ARTS * #', 'ARTS-INFORMATION TECHNOLOGY *', 'ARTIFICIAL INTELLIGENCE', 'AYURVEDA MEDICINE & SURGERY', 'BANKING & INSURANCE', 'BIOCHEMISTRY & MOLECULAR BIOLOGY', 'BIOLOGICAL SCIENCE', 'BIOMEDICAL TECHNOLOGY', 'BUSINESS INFORMATION SYSTEMS', 'BUSINESS SCIENCE', 'COMMERCE', 'COMMUNICATION STUDIES *', 'COMPUTER SCIENCE', 'COMPUTER SCIENCE & TECHNOLOGY', 'CREATIVE MUSIC TECHNOLOGY & PRODUCTION', 'DATA SCIENCE', 'DENTAL SURGERY', 'DESIGN #', 'ELECTRONICS AND COMPUTER SCIENCE', 'ENGINEERING', 'ENGINEERING (EM)', 'ENGINEERING (TM)', 'ENTREPRENEURSHIP AND MANAGEMENT', 'ENVIRONMENTAL CONSERVATION &', 'EXPORT AGRICULTURE', 'FACILITIES MANAGEMENT', 'FASHION DESIGN & PRODUCT DEVELOPMENT #', 'FINANCIAL ECONOMICS', 'FINANCIAL ENGINEERING', 'FINANCIAL MATHEMATICS AND INDUSTRIAL STATISTICS', 'FISHERIES & MARINE SCIENCES', 'FOOD BUSINESS MANAGEMENT', 'FOOD PRODUCTION', 'FOOD SCIENCE & NUTRITION', 'FOOD SCIENCE & TECHNOLOGY', 'GEOGRAPHICAL INFORMATION SCIENCE', 'GREEN TECHNOLOGY', 'HEALTH INFORMATION AND COMMUNICATION', 'HEALTH PROMOTION', 'HEALTH TOURISM AND HOSPITALITY MANAGEMENT', 'HUMAN RESOURCE DEVELOPMENT', 'INDIGENOUS MEDICINAL RESOURCES', 'INDIGENOUS PHARMACEUTICAL TECHNOLOGY', 'INDUSTRIAL INFORMATION', 'INDUSTRIAL STATISTICS &', 'INFORMATION AND COMMUNICATION TECHNOLOGY', 'INFORMATION SYSTEMS', 'INFORMATION TECHNOLOGY (IT)', 'INFORMATION TECHNOLOGY & MANAGEMENT', 'ISLAMIC STUDIES *', 'LANDSCAPE ARCHITECTURE #', 'LAW', 'MANAGEMENT', 'MANAGEMENT AND INFORMATION', 'MANAGEMENT AND PUBLIC POLICY', 'MANAGEMENT STUDIES (TV) - A', 'MANAGEMENT STUDIES (TV) - B', 'MARINE AND FRESHWATER SCIENCES', 'MEDICAL IMAGING TECHNOLOGY', 'MEDICAL LABORATORY SCIENCES', 'MEDICINE', 'MINERAL RESOURCES AND', 'NURSING', 'OCCUPATIONAL THERAPY', 'OPTOMETRY', 'PEACE & CONFLICT RESOLUTION *', 'PHARMACY', 'PHYSICAL EDUCATION #', 'PHYSICAL SCIENCE', 'PHYSIOTHERAPY', 'PRIMARY EDUCATION', 'QUANTITY SURVEYING', 'RADIOGRAPHY', 'REAL ESTATE MANAGEMENT & VALUATION', 'SCIENCE AND TECHNOLOGY', 'SERVICE MANAGEMENT', 'SIDDHA MEDICINE & SURGERY', 'SOCIAL STUDIES IN INDIGENOUS KNOWLEDGE', 'SOCIAL WORK *', 'SOFTWARE ENGINEERING', 'SPEECH AND HEARING SCIENCES', 'SPORTS SCIENCE & MANAGEMENT #', 'STATISTICS & OPERATIONS RESEARCH', 'SURVEYING SCIENCE', 'TOURISM & HOSPITALITY MANAGEMENT', 'UNANI MEDICINE & SURGERY', 'URBAN BIORESOURCES', 'URBAN INFORMATICS AND PLANNING', 'VETERINARY SCIENCE', 'YOGA AND PARAPSYCHOLOGY','AQUATIC RESOURCES TECHNOLOGY', 'HOSPITALITY, TOURISM', 'ENGLISH LANGUAGE & APPLIED LINGUISTICS', 'PLANTATION MANAGEMENT AND TECHNOLOGY', 'POLYMER SCIENCE AND INDUSTRIAL MANAGEMENT', 'ENGINEERING TECHNOLOGY (ET)', 'BIOSYSTEMS TECHNOLOGY (BST)', 'INFORMATION COMMUNICATION TECHNOLOGY', 'PHYSICAL SCIENCE -ICT', 'TRANSLATION STUDIES', 'FILM & TELEVISION STUDIES #', 'PROJECT MANAGEMENT', 'TEACHING ENGLISH AS A SECOND', 'VISUAL ARTS', 'MUSIC #', 'DANCE', 'DRAMA & THEATRE #', 'ART & DESIGN', 'VISUAL & TECHNOLOGICAL ARTS']
STREAM_OPTIONS = ['Science', 'Technology', 'Arts', 'Commerce', 'Mathamatics']
# --- END CONFIGURATION ---

# 2. Initial data loading (only once when the web app starts)
@st.cache_data
def get_data():
    """Load and average Z-Score data from multiple files."""
    st.info(f"Loading and averaging Z-Scores from {len(ZSCORE_DATA_FILES)} files...")
    df = load_data(ZSCORE_DATA_FILES)
    if df is None or df.empty:
        st.error("🚨 Data loading failed. Please check if the CSV files are present in the directory.")
    return df

df_cutoffs = get_data()

# --- Custom CSS for Styling ---
def apply_custom_css():
    st.markdown("""
        <style>
        /* 1. Background layer with blur */
        .stApp:before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url(https://i.pinimg.com/1200x/00/81/89/00818908f33afe772a0844a0c253633e.jpg);
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            filter: blur(3px);
            z-index: -1;
        }*/
        
        /* 2. Main content area readability overlay */
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.9); /* Semi-transparent white overlay */
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        /* 3. Sidebar background */
        .stSidebar {
            background-color: rgba(255, 255, 255, 0.95); 
        }
        
        /* 4. Header Styling */
        .main .stTitle {
            color: #007bff; 
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        /* 5. Subheader Styling */
        h3{
            color: #333333;
            border-left: 5px solid #ff6347; 
            padding-left: 10px;
            font-weight: 600;
        }

        /* 6. Button Styling */
        .stButton>button { 
            color: #FFFFFF !important; 
            background-color: #007bff; 
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 1.1em;
            font-weight: bold; 
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0056b3; 
        }

        /* 7. Metric Boxes */
        [data-testid="stMetricValue"] {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff; 
        }
        
        /* 8. Analysis Box */
        .analysis-box {
            background-color: #e0f7fa; 
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #00bcd4;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        /* 9. Mobile Responsiveness Fix (Force 100% width on small screens) */
        @media (max-width: 600px) {
        /* General class names used by Streamlit for columns */
        /* This forces all blocks within columns to take 100% width */
        .st-emotion-cache-1r6r4v5, .st-emotion-cache-1c9v9yl, .st-emotion-cache-1q1g793, .st-emotion-cache-1r4w75t {
        width: 100% !important;
         flex-direction: column !important;/* - This may not be necessary, but try it if issues persist */
    }
}

        </style>
    """, unsafe_allow_html=True)

# --- Apply CSS and Set Page Config ---
apply_custom_css()

st.set_page_config(
    page_title="University Course Recommendation System",
    layout="wide",
    initial_sidebar_state="auto" 
)

# --- HEADER AND INFO ---
st.title("🎓 University Course Recommendation System (3-Year Average)")
st.write("Select the most suitable university courses based on your Z-Score and preferences. The Cutoff Z-Scores here are based on the 3-year average values.")

if df_cutoffs is None or df_cutoffs.empty:
    st.stop()

# --- UI Input Section ---
st.subheader("⚙️ Input Data (Your Inputs)")
with st.form("student_inputs", clear_on_submit=False):
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        z_score = st.number_input("1. Your Z-Score:", min_value=0.0000, max_value=4.0000, step=0.0001, format="%.4f")
    
    with col_b:
        district = st.selectbox("2. District (District Code):", DISTRICT_OPTIONS)
    
    with col_c:
        stream = st.selectbox("3. A/L Stream:", STREAM_OPTIONS)
    
    st.markdown("---")
    st.markdown("#### 🎯 Preference Fields (Preferences)")
    
    col_d, col_e = st.columns(2)
    with col_d:
        primary_field = st.selectbox("4. Primary Preference (Field):", PRIMARY_FIELD_OPTIONS)
    
    with col_e:
        # Set a default index for secondary field (e.g., IT)
        try:
            secondary_field_default_index = PRIMARY_FIELD_OPTIONS.index('IT')
        except ValueError:
            secondary_field_default_index = 0
            
        secondary_field = st.selectbox("5. Secondary Preference (Field):", PRIMARY_FIELD_OPTIONS, index=secondary_field_default_index)
    
    st.markdown("---")
    submitted = st.form_submit_button("✅ Get Recommendations", type="primary", use_container_width=True)

# --- Main Content Area for Results ---

if submitted and df_cutoffs is not None:
    st.subheader("📊 Analysis Results")
    
    # 2. Running the algorithm
    recommendations_df = calculate_compatibility_score(
        student_z_score=z_score,
        district=district,
        primary_field=primary_field,
        secondary_field=secondary_field,
        stream=stream,
        df_cutoffs=df_cutoffs
    )
    
    st.markdown("---")

    if recommendations_df.empty:
        st.error("😔 **Sorry:** No suitable courses were found based on your inputs. Please check your Stream, Z-Score, or District values.")
    else:
        # --- Z-SCORE ANALYSIS & SAFETY MARGIN FOR TOP COURSE ---
        
        top_recommendation = recommendations_df.iloc[0]
        top_course = top_recommendation['Course']
        required_cutoff = top_recommendation['Z_Score']
        safety_margin = top_recommendation['Safety_Margin']
        
        # Determine Safety Status and Message
        if safety_margin >= 0.15:
            status_emoji = "🟢"
            margin_status = "Very High Chance (Very Safe Margin)"
            status_color = "#28a745" # Green
        elif safety_margin >= 0.05:
            status_emoji = "🟡"
            margin_status = "Good Chance (Safe Margin)"
            status_color = "#ffc107" # Yellow
        elif safety_margin > 0.0:
            status_emoji = "🟠"
            margin_status = "Moderate Chance (Moderate Margin)"
            status_color = "#fd7e14" # Orange
        else:
            status_emoji = "⚠️"
            margin_status = "Close to Cutoff (Zero or Low Margin)"
            status_color = "#17a2b8" # Info/Blue 

        st.markdown(f'<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("#### 📈 Z-Score Analysis (Top Recommendation)")
        
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 8px; background-color: #fff; margin-bottom: 15px;">
            <h5 style="margin-top: 0; color: #007bff;">Top Recommendation: {top_course}</h5>
            <p style="font-size: 1.1em; font-weight: bold; color: {status_color};">{status_emoji} {margin_status}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Your Z-Score", f"{z_score:.4f}")
        with col2:
            st.metric("3-Year Avg. Cutoff", f"{required_cutoff:.4f}")
        with col3:
            # Display margin with delta (color coded arrow)
            st.metric("Safety Margin", f"{safety_margin:.4f}", delta=f"{safety_margin:.4f}")
            
        st.markdown(f'</div>', unsafe_allow_html=True)
        # --- END Z-SCORE ANALYSIS ---
        
        # 4. DATA VISUALIZATION SECTION
        st.markdown("---")
        st.subheader("📉 Z-Score Comparison Chart")

        # 4.1. Data Preparation
        # Combine Course and University to create a Course ID for the chart
        recommendations_df['Course_Uni'] = recommendations_df['Course'] + " (" + recommendations_df['University'] + ")"
        
        # Plot only the Top 10 recommendations
        plot_df = recommendations_df.head(10).copy() 
        
        # Data for Cutoff Z-Scores
        plot_data = pd.DataFrame({
            'Course': plot_df['Course_Uni'],
            'Z_Score_Type': ['Cutoff Z-Score'] * len(plot_df),
            'Z_Score_Value': plot_df['Z_Score']
        })
        
        # Add the student's Z-Score as a comparison column for all courses
        student_z_score_df = pd.DataFrame({
            'Course': plot_df['Course_Uni'],
            'Z_Score_Type': ['Your Z-Score'] * len(plot_df),
            'Z_Score_Value': [z_score] * len(plot_df)
        })
        
        # Concatenate the dataframes
        final_plot_df = pd.concat([plot_data, student_z_score_df])

        # 4.2. Create the Plotly Bar Chart
        fig = px.bar(
            final_plot_df, 
            x='Z_Score_Value', 
            y='Course', 
            color='Z_Score_Type',
            orientation='h', # Horizontal Bar Chart
            barmode='group', # Grouped bars for comparison
            title="Comparison of Your Z-Score and 3-Year Avg. Cutoff Z-Scores (Top 10)",
            labels={'Z_Score_Value': 'Z-Score', 'Course': 'Course Name'},
            height=500,
            # Set custom color scale
            color_discrete_map={'Cutoff Z-Score': '#4c78a8', 'Your Z-Score': '#ff6347'} 
        )
        
        # Adjust axis range for better visualization
        min_score = final_plot_df['Z_Score_Value'].min()
        max_score = final_plot_df['Z_Score_Value'].max()
        
        # Adjust the x-axis range slightly wider than the data range
        if min_score > 0:
             fig.update_xaxes(range=[min_score - 0.05, max_score + 0.05])
        
        # Layout settings for a clean look
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            xaxis=(dict(showgrid=True, gridcolor='#e0e0e0')), 
            legend_title_text=''
        )

        # 4.3. Display the Plotly chart
        st.plotly_chart(fig, use_container_width=True)
        
        # END DATA VISUALIZATION SECTION

        st.markdown("---")
        st.subheader("📚 All Recommended Courses (Ranked by Compatibility Score)")
        
        st.dataframe(
            recommendations_df.rename(columns={
                'Course': 'Course',
                'University': 'University',
                'Z_Score': 'Avg. Cutoff Z-Score',
                'District': 'District',
                'Compatibility_Score': 'Compatibility Score',
                'Safety_Margin': 'Safety Margin'
            }).drop(columns=['Course_Uni']).reset_index(drop=True), 
            use_container_width=True
        )

        st.info("ℹ️ Compatibility Score: This is the final score calculated based on your Z-Score margin and your selected Preference Fields. A higher score indicates a better fit.")