import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px  # New: Interactive Charts with Plotly

# Set Streamlit page config
st.set_page_config(page_title="Data Sweeper", page_icon="🧹", layout="wide")

# ---- Sidebar ----
st.sidebar.title("⚙️ Options & Settings")
st.sidebar.write("Upload your dataset and choose cleaning options.")

# ---- Main App ----
st.title("🧹 Data Sweeper: Clean & Transform Your Data")
st.write("Easily clean, organize, and convert your datasets.")

# ---- File Upload ----
uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Detect file type
    file_extension = uploaded_file.name.split(".")[-1]

    # Load data
    if file_extension == "csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---- Data Preview & Summary ----
    st.subheader("👀 Data Preview")
    st.dataframe(df.head(10))

    st.subheader("📊 Dataset Summary")
    st.write(df.describe())  # Show statistical summary

    st.subheader("📉 Missing Values")
    st.write(df.isnull().sum())  # Show missing values count

    # ---- Data Cleaning Options ----
    st.sidebar.subheader("🧹 Data Cleaning")

    if st.sidebar.button("Remove Duplicates"):
        df = df.drop_duplicates()
        st.success("✅ Duplicates removed!")

    missing_value_option = st.sidebar.radio(
        "Handle Missing Values",
        ["Do Nothing", "Fill with Mean", "Fill with Median", "Fill with 0", "Fill with 'Missing'"]
    )
    
    if missing_value_option == "Fill with Mean":
        df.fillna(df.mean(), inplace=True)
    elif missing_value_option == "Fill with Median":
        df.fillna(df.median(), inplace=True)
    elif missing_value_option == "Fill with 0":
        df.fillna(0, inplace=True)
    elif missing_value_option == "Fill with 'Missing'":
        df.fillna("Missing", inplace=True)

    # ---- Data Organization ----
    st.sidebar.subheader("🛠 Organize Data")
    
    sort_column = st.sidebar.selectbox("Sort by Column", ["None"] + list(df.columns))
    if sort_column != "None":
        df = df.sort_values(by=sort_column)
        st.success(f"✅ Data sorted by {sort_column}!")

    rename_columns = st.sidebar.checkbox("Rename Columns")
    if rename_columns:
        col_map = {col: st.text_input(f"Rename {col}", col) for col in df.columns}
        df.rename(columns=col_map, inplace=True)
        st.success("✅ Columns renamed successfully!")

    # ---- Outlier Detection ----
    st.sidebar.subheader("📈 Detect Outliers")
    
    outlier_column = st.sidebar.selectbox("Select Column for Outlier Detection", ["None"] + list(df.columns))
    
    if outlier_column != "None":
        Q1 = df[outlier_column].quantile(0.25)
        Q3 = df[outlier_column].quantile(0.75)
        IQR = Q3 - Q1
        outlier_condition = (df[outlier_column] < (Q1 - 1.5 * IQR)) | (df[outlier_column] > (Q3 + 1.5 * IQR))
        outliers = df[outlier_column][outlier_condition]

        st.write(f"🔍 Found {len(outliers)} outliers in {outlier_column}.")
        st.write(outliers)

        if st.button("Remove Outliers"):
            df = df[~outlier_condition]
            st.success("✅ Outliers removed!")

    # ---- File Conversion ----
    st.sidebar.subheader("🔄 Convert & Download")
    
    buffer = io.BytesIO()
    
    if st.sidebar.button("Download as CSV"):
        df.to_csv(buffer, index=False)
        st.download_button("📥 Download CSV", buffer.getvalue(), "cleaned_data.csv", "text/csv")
    
    buffer.seek(0)
    
    if st.sidebar.button("Download as Excel"):
        df.to_excel(buffer, index=False, engine="openpyxl")
        st.download_button("📥 Download Excel", buffer.getvalue(), "cleaned_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ---- Data Visualization (Using Plotly) ----
    st.subheader("📊 Interactive Data Visualization")

    # Select column for visualization
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_columns:
        column_to_plot = st.selectbox("Choose a Column to Visualize", numeric_columns)

        # ---- Interactive Histogram ----
        if st.button("📊 Generate Interactive Histogram"):
            fig = px.histogram(df, x=column_to_plot, title=f"Histogram of {column_to_plot}",
                               color_discrete_sequence=["#1f77b4"], nbins=20)
            st.plotly_chart(fig, use_container_width=True)

        # ---- Interactive Boxplot ----
        if st.button("📦 Generate Interactive Boxplot"):
            fig = px.box(df, y=column_to_plot, title=f"Boxplot of {column_to_plot}",
                         color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig, use_container_width=True)

        # ---- New: Interactive Scatter Plot ----
        scatter_x = st.selectbox("Choose X-axis for Scatter Plot", numeric_columns, index=0)
        scatter_y = st.selectbox("Choose Y-axis for Scatter Plot", numeric_columns, index=1)
        
        if st.button("📈 Generate Interactive Scatter Plot"):
            fig = px.scatter(df, x=scatter_x, y=scatter_y, title=f"Scatter Plot: {scatter_x} vs {scatter_y}",
                             color_discrete_sequence=["#2ca02c"])
            st.plotly_chart(fig, use_container_width=True)

    st.success("🎉 Your data is now clean, organized, and ready to use!")

else:
    st.info("📤 Please upload a dataset to get started.")
