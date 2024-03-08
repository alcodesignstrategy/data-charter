import streamlit as st
import pandas as pd
import base64
from io import StringIO
import plotly.express as px
import plotly.graph_objs as go
import plotly.colors as colors
from colour import Color 

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

def get_color_shades(base_color, num_shades):
    base = Color(base_color)
    return [base.get_hex_l() for base in base.range_to(Color("white"), num_shades)]

def plot_data(df, year_range, categories, subcategories):
    df['Year'] = df['Year'].astype(int)  # Convert 'Year' column to integers
    df_filtered = df[
        (df['Year'] >= year_range[0]) &
        (df['Year'] <= year_range[1]) &
        df['Category'].isin(categories) &
        df['Subcategory'].isin(subcategories)
    ]

    # Create a new column with combined Category and Subcategory
    df_filtered['Category_Subcategory'] = df_filtered['Category'] + ' - ' + df_filtered['Subcategory']

    # Create a line chart
    fig = go.Figure()

    # Manually define a list of base colors
    base_colors = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        # Add more colors as needed
    ]

    # Loop through each category to assign colors and create shades for subcategories
    for i, (category, category_group) in enumerate(df_filtered.groupby('Category')):
        color_index = i % len(base_colors)
        base_color = base_colors[color_index]
        num_subcategories = len(category_group['Subcategory'].unique())
        subcategory_colors = get_color_shades(base_color, num_subcategories + 1)[1:]
        
        for j, (subcategory, subcategory_group) in enumerate(category_group.groupby('Subcategory')):
            fig.add_trace(go.Scatter(
                x=subcategory_group['Year'],
                y=subcategory_group['Amount'],
                mode='lines+markers',  # Use 'lines' if you don't want markers
                name=f"{category} - {subcategory}",
                line=dict(color=subcategory_colors[j % num_subcategories])
            ))

    fig.update_layout(
        title='Category-wise and Subcategory-wise Amounts',
        xaxis_title='Year',
        yaxis_title='Amount',
        legend_title='Category - Subcategory',
    )

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
