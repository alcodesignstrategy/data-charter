import streamlit as st
import pandas as pd
import base64
from io import StringIO
import plotly.express as px

# Function to convert the uploaded file to a long-form DataFrame
def convert_to_long_format(uploaded_file):
    df = pd.read_excel(uploaded_file, header=None)
    header = df.iloc[0:2, 1:].apply(lambda x: x.map(str)).agg('_'.join).str.strip('_').tolist()
    header = ['Category'] + header
    df.columns = header
    df = df.drop([0, 1])
    df = df.melt(id_vars='Category', var_name='Year_Subcategory', value_name='Amount')
    df[['Year', 'Subcategory']] = df['Year_Subcategory'].str.split('_', expand=True)
    df = df.drop('Year_Subcategory', axis=1)
    df = df[['Category', 'Year', 'Subcategory', 'Amount']]
    return df

# Function to download data as a CSV file
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="transformed_data.csv">Download CSV file</a>'
    return href

# Function to plot the data using plotly
def plot_data(df, year_range, categories, subcategories):
    df['Year'] = df['Year'].astype(int)  # Convert 'Year' column to integers
    df_filtered = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) & 
        df['Category'].isin(categories) & 
        df['Subcategory'].isin(subcategories)
    ]
    fig = px.line(
        df_filtered, 
        x='Year', 
        y='Amount', 
        color='Category', 
        line_group='Subcategory', 
        hover_name='Subcategory'
    )
    fig.update_layout(title='Sales by Category and Subcategory', xaxis_title='Year', yaxis_title='Sales')
    return fig

# Main function that runs the Streamlit app
def main():
    st.title('Data Transformation Tool')

    # File uploader allows user to add their own excel file
    uploaded_file = st.file_uploader("Upload your input Excel file", type=["xlsx"])

    if uploaded_file is not None:
        data = convert_to_long_format(uploaded_file)
        st.write(data)

        # Generate the download link and show it
        st.markdown(get_table_download_link(data), unsafe_allow_html=True)

  # Visualization section
    if uploaded_file is not None:
        data = convert_to_long_format(uploaded_file)
        st.write(data)

        # Generate the download link and show it
        st.markdown(get_table_download_link(data), unsafe_allow_html=True)

        # Visualization widgets
        st.write("### Data Visualization")
        year_range = st.slider('Select Year Range', int(data['Year'].min()), int(data['Year'].max()), (int(data['Year'].min()), int(data['Year'].max())))
        categories = st.multiselect('Select Categories', options=data['Category'].unique(), default=data['Category'].unique())
        subcategories = st.multiselect('Select Subcategories', options=data['Subcategory'].unique(), default=data['Subcategory'].unique())

        # Plot button
        if st.button('Plot Data'):
            fig = plot_data(data, (year_range[0], year_range[1]), categories, subcategories)
            st.plotly_chart(fig)


if __name__ == "__main__":
    main()
