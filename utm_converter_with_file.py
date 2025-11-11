import streamlit as st
import pandas as pd
from pyproj import Transformer
import io

# Function to convert UTM coordinates between zones
def convert_utm_to_utm(easting, northing, src_zone, dst_zone, hemisphere='N'):
    # Define source and destination projections
    src_proj = f"epsg:326{src_zone}" if hemisphere == 'N' else f"epsg:327{src_zone}"
    dst_proj = f"epsg:326{dst_zone}" if hemisphere == 'N' else f"epsg:327{dst_zone}"

    # Create a transformer to convert between the projections
    transformer = Transformer.from_crs(src_proj, dst_proj)

    # Perform the transformation
    new_easting, new_northing = transformer.transform(easting, northing)
    
    return new_easting, new_northing

# Streamlit interface
st.title("UTM Coordinate Converter")

st.sidebar.header("Upload File with Coordinates")

# File uploader for CSV or Text files
uploaded_file = st.sidebar.file_uploader("Choose a CSV or text file", type=["csv", "txt"])

# Input fields for UTM Zone Conversion
src_zone = st.sidebar.number_input("Source UTM Zone (e.g., 33)", min_value=1, max_value=60, step=1)
dst_zone = st.sidebar.number_input("Destination UTM Zone (e.g., 34)", min_value=1, max_value=60, step=1)

hemisphere = st.sidebar.selectbox("Hemisphere", ["Northern Hemisphere (N)", "Southern Hemisphere (S)"])
hemisphere = 'N' if hemisphere == "Northern Hemisphere (N)" else 'S'

# Button to perform the conversion after file upload
if uploaded_file is not None:
    # Read the uploaded file into a DataFrame
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        # Assume text file with space or tab separated values
        content = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(content), delim_whitespace=True)

    # Check if required columns exist in the uploaded data
    if "easting" in df.columns and "northing" in df.columns:
        st.write("Data from file:")
        st.dataframe(df)

        # Perform conversion for each row in the DataFrame
        converted_easting = []
        converted_northing = []

        for idx, row in df.iterrows():
            easting = row["easting"]
            northing = row["northing"]
            # Convert UTM coordinates
            new_easting, new_northing = convert_utm_to_utm(easting, northing, src_zone, dst_zone, hemisphere)
            converted_easting.append(new_easting)
            converted_northing.append(new_northing)

        # Add the new coordinates to the DataFrame
        df["converted_easting"] = converted_easting
        df["converted_northing"] = converted_northing

        # Display the converted coordinates
        st.write("Converted Coordinates:")
        st.dataframe(df[["easting", "northing", "converted_easting", "converted_northing"]])
    else:
        st.error("Uploaded file does not contain 'easting' and 'northing' columns.")
else:
    st.info("Please upload a CSV or text file containing UTM coordinates.")
