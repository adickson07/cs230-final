""" Name: Abby Dickson
CS230: Section 3
Data: Skyscrapers
URL:Link to your web application on Streamlit Cloud (if posted)
Description:This program develops a website that shows various data visualizations developed from Skyscraper Data.
            It's designed to show you the different heights of skyscrapers across various cities. After choosing your cities,
            maximum height, and minimum number of floors, the website will develop a few images. The first is a pie chart
            displaying the percentage of skyscrapers under your chosen max height in each city. This helps you to notice
            which city has the most skyscrapers of the size you are looking for. Next, you will see a bar chart displaying
            the average heights of all skyscrapers under your max height and containing your minimum chosen floors in each city.
            This way, you can get a better idea of how tall skyscrapers are in each city that is under your max height.
            Next you will see a box plot displaying a more detailed outlay of the median height of skyscrapers under your
            max height, and the Q1 and Q3 values and any outliers there may be. Next, there's a table with a new column I created
            that displays each city skyscraper from your selected cities and either how many years it took to complete,
            or that it's incomplete. Finally, there is a map displaying the general area of the cities you have chosen."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pydeck as pdk
import seaborn as sns

#Read in Data
def read_data():
     try:    #[PY3] Error checking with try/except
        data_read = pd.read_csv("skyscrapers(in).csv").set_index("id")
        return data_read
     except:
         print("Unable to read file")
         return None

#Code for completion_status based on code from ChatGPT. See section 2 of accompanying document.
# [DA7]: Create new column
def completion_status(data, selected_cities):
    df = read_data()
    df = df[df['location.city'].isin(selected_cities)]
    df['years_to_finish'] = df['status.completed.year'] - df['status.started.year']
    df['status'] = df.apply(lambda row: 'incomplete' if row['status.started.year'] == 0 or
                    ['status.completed.year'] == 0 or row['years_to_finish'] < 0
    else f"{row['years_to_finish']} years",axis = 1) #[DA1]: Clean Data with Lambda
    #Code for this line based on code from ChatGPT. See section 3 of accompanying document.
    df_sorted = df[['location.city', 'status']].sort_values(by='location.city', ascending=True)
    return df_sorted

#Filter the Data
#Default values:
default_city = ['Detroit', 'Indianapolis', 'Kansas City','Atlanta']
default_height = 1600
default_floors = 30

#[PY1] A function with two or more parameters
def filter_data(selected_cities, max_height, min_floors):
    df = read_data()
    df = df.loc[df['location.city'].isin(selected_cities)]
    df = df.loc[df['statistics.height'] < max_height]
    df = df.loc[df['statistics.floors above'] > min_floors]

    return df
#Creting a Pivot Table
#Code for pivot table based on code from ChatGPT. See section 5 of accompanying document.
#[DA6]: Analyza data with pivot table
def create_pivot_table():
    df = read_data()

    if df is not None:
        pivot_df = df.pivot_table( index=["location.city"],
                            values=[ "statistics.height", "statistics.floors above",
                            "location.latitude", "location.longitude"],
                            aggfunc = 'mean',
                            dropna = False)

        return pivot_df
    else:
        return None


#Findig the tallest and shortest skyscrapers
#Code for largest_smallest function based on code from ChatGPT. See section 6 of accompanying document.
#[DA3]: Find te top largest or smallest value of a column
def largest_smallest():
    df = read_data()
    df_filtered = df[df['statistics.height'] > 0]
    df_filtered['location.city'] = df_filtered['location.city'].str.strip()

    if df_filtered.empty:
        print("no valid skyscraper data (all heights are zero.")
        return None, None, None, None

    largest = df_filtered['statistics.height'].max()
    largest_city_df = df_filtered.loc[df_filtered['statistics.height'] == largest]

    if not largest_city_df.empty:
        largest_city = largest_city_df['location.city'].iloc[0]
    else:
        largest_city = "not found"

    smallest = df_filtered['statistics.height'].min()
    smallest_city_df = df_filtered.loc[df_filtered['statistics.height'] == smallest]

    if not smallest_city_df.empty:
        smallest_city = smallest_city_df['location.city'].iloc[0]
    else:
        smallest_city = "not found"

    return largest, largest_city, smallest, smallest_city  #[PY2] A function that returns more than one value




def all_cities():
    df = read_data()
    return df['location.city'].unique().tolist() #[DA4]: Filter data by one condition


def count_cities(cities, df):
    return [df.loc[df['location.city'].isin([city])].shape[0] for city in cities]

def skyscraper_heights(df):
    heights = [row['statistics.height'] for ind, row in df.iterrows()] #[PY4] A list comprehension
    cities = [row['location.city'] for ind, row in df.iterrows()] #[PY4] A list comprehension #[DA8] use iterrows()
    dict = {} #[PY5] A dictionary where you write code to access its keys, values, or items
    for city in cities:
        dict[city] = []
    for i in range(len(heights)):
        dict[cities[i]].append(heights[i])


    return dict

def skyscraper_height_averages(dict_heights):
    dict = {}
    for key in dict_heights.keys():
        dict[key] = float(np.mean(dict_heights[key])) #[DA9] Perform calculation on DataFrame columns (average)

    return dict
#Bar chart:
#[VIZ1] Chart: Bar Chart
def generate_bar_chart(dict_averages):

    df5 = pd.DataFrame(list(dict_averages.items()), columns =['location.city', 'statistics.height'])
    plt.figure(figsize = (10, 6))
    sns.barplot(data=df5, x='location.city', y='statistics.height', hue = 'location.city', palette = "Set2")
    plt.xlabel('City', fontname = 'Times New Roman', fontsize = 12, fontweight = 'bold')
    plt.ylabel('Average Skyscraper Height (meters)', fontname = 'Times New Roman', fontsize = 12, fontweight = 'bold')
    plt.title("Average Sky-Scraper Heights in Meters Across Selected Cities", fontname = 'Times New Roman', fontweight = 'bold', fontsize = 16)
    plt.xticks(rotation = 45, fontname = 'Times New Roman', fontsize = 10)
    plt.yticks(fontname = 'Times New Roman', fontsize = 10)

    plt.show()

    return plt

#Pie Chart
#[VIZ2]: Pie Chart
def generate_piechart(counts, selected_cities):

    cmap = plt.get_cmap("Set3")
    colors = [cmap(i / len(counts)) for i in range(len(counts))]
    explodes = [0 for i in range(len(selected_cities))]
    maximum = counts.index(np.max(counts))
    explodes[maximum] = 0.25

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(counts, labels = selected_cities, explode = explodes, autopct = "%.2f", colors = colors)
    #Code for pie chart fonts, fontsizes, colors, and weights based on code from ChatGPT. See section 1 of accompanying document.
    for text in texts:
        text.set_fontname('Times New Roman')
        text.set_fontsize(11)
        text.set_fontweight('bold')

    for autotext in autotexts:
        autotext.set_fontname('Times New Roman')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        plt.title("Percentage of Sky-Scrapers Found in Each City", fontname = 'Times New Roman', fontsize = 16, fontweight = 'bold')
    return plt


#Creating a Box Plot
#Code for box plot based on code from ChatGPT. See section 4 of accompanying document.
#[VIZ3] Box Plot
def generate_boxplot(data, x = None, y = None, plot_type = 'seaborn', title = 'Boxplot',
                     x_label = 'Cities', y_label = 'Heights in Meters', palette = 'Set2', width = .5, fliersize = 5):
    plt.figure(figsize=(10,6))


    if plot_type == 'matplotlib':
        plt.boxplot(data)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks([1], [x])

    elif plot_type == 'seaborn':
        if isinstance(data, pd.DataFrame) and x and y:
            sns.boxplot(x=x, y=y, data = data, palette = palette, width = width, fliersize = fliersize)
        else:
            sns.boxplot(data=data, palette=palette, width=width, fliersize=fliersize)

        plt.title(title, fontname = 'Times New Roman', fontsize = 16, fontweight = 'bold') #[ST4] Customized design: Font
        plt.xlabel(x_label, fontname = 'Times New Roman', fontsize = 12, fontweight = 'bold') #[ST4] Customized design: Font
        plt.ylabel(y_label, fontname = 'Times New Roman', fontsize = 12, fontweight = 'bold') #[ST4] Customized design: Font
        plt.xticks(fontname = 'Times New Roman', fontsize = 12) #[ST4] Customized design:Font
        plt.yticks(fontname = 'Times New Roman', fontsize = 12) #[ST4] Customized design:Font


    else:
        raise ValueError("plot_type must be either 'matplotlib' or 'seaborn'")

    return plt


data = pd.read_csv('skyscrapers(in).csv')
generate_boxplot(data, x='location.city', y='statistics.height',
                plot_type='seaborn',
                title="Heights of Skyscrapers")


#Creating a Map
#[MAP] One map, couldn't figure out scatterplot layer
def generate_map(df):
    map_df = df[['location.city', 'location.latitude', 'location.longitude', 'statistics.height']].copy()
    map_df.rename(columns={'location.latitude': 'latitude', 'location.longitude': 'longitude'}, inplace=True)


    view_state = pdk.ViewState(
        latitude=map_df['latitude'].mean(),
        longitude=map_df['longitude'].mean(),
        zoom=4
    )

    layer = pdk.Layer(
        'ScatterplotLayer',
        map_df,
        pickable=True,
        opacity = .8,
        stroked = True,
        filled = True,
        radius_scale = 6,
        radius_min_pixels = 1,
        radius_max_pixels = 100,
        line_width_min_pixels = 1,
        get_position=['location.longitude, location.latitude'],
        get_radius=1000,
        get_fill_color=[255, 140, 0],
        get_line_color = [0,0,0]
    )

    # Sample icon data
    icon_data = [{'name': "location1", 'latitude': 37.7749, 'longitude': -122.4194},
                 {"name": 'location2', 'latitude': 34.0522, 'longitude': -118.2437}]

    for item in icon_data:
        item['icon'] = 'https://banner2.cleanpng.com/20180619/crk/aa67ojt85.webp'


    icon_layer = pdk.Layer(
        'IconLayer',
        data=icon_data,
        get_icon='icon',
        get_size=30,
        size_scale=10,
        get_position=['longitude', 'latitude'],
        pickable=True
    )

    tool_tip = {
        'html': '<b>{location.city}</b><br/>Height: {statistics.height} meters',
        'style': {'backgroundColor': 'steelblue', 'color': 'white'}
    }

    deck_map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer, icon_layer],
        tooltip=tool_tip
    )


    st.pydeck_chart(deck_map)

def main():
    st.markdown("<h1 style= 'text-align: center; font-family: Serif, Times New Roman;', >Skyscraper Data Visualization</h1>", unsafe_allow_html=True)
    st.markdown("""<p style='text-align: center; font-family: Serif, Times New Roman;', >The following data visualizations are 
    designed to show you the different heights of skyscrapers across various cities. After choosing your cities, 
    maximum height, and minimum number of floors, the website will develop a few images. The first is a pie chart 
    displaying the percentage of skyscrapers under your chosen max height in each city. This helps you to notice 
    which city has the most skyscrapers of the size you are looking for. Next, you will see a bar chart displaying 
    the average heights of all skyscrapers under your max height and containing your minimum chosen floors in each city. 
    This way, you can get a better idea of how tall skyscrapers are in each city that is under your max height. 
    Next you will see a box plot displaying a more detailed outlay of the median height of skyscrapers under your 
    max height, and the Q1 and Q3 values and any outliers there may be. After that you will see a table displaying 
    each skyscraper in each city and either how many years it took to complete the building, 
    or if it is incomplete. Finally, there is a map displaying the general 
    area of the cities you have chosen. Ultimately, this could be helpful if you were looking for a city to live in and 
    wanted a better idea of skyscraper heights. This could help you figure out which city would be the best fit for you. 
    """, unsafe_allow_html=True)

    #Code for adding an image based on code from ChatGPT. See section 7 of accompanying document.
    st.image('C:\\Users\\ardic\\OneDrive - Bentley University\\PROGRAM 3\\class11_18\\sunset_skyscrapers.jpg') #[ST4] Customized design: image
    st.sidebar.write("Please choose your options to display data")#[ST4]
    cities = st.sidebar.multiselect("Select cities (2-6)", sorted([str(city) for city in all_cities()])) #[ST1] Streamlit Widget: sidebar #[DA2] sort data in ascending order by one column
    max_height = st.sidebar.slider("Select the maximum height in meters: ",36, 2000) #[ST2] Streamlit widget: Slider
    min_floorsabove = st.sidebar.number_input("Choose a minimum number of floors: ", 0, 40) #[ST3] Streamlit widget: numeric input

    data = filter_data(cities, max_height, min_floorsabove)
    series = count_cities(cities, data)

    largest, largest_city, smallest, smallest_city = largest_smallest()
    if largest is not None:
        st.markdown("<h2 style= 'text-align: center; font-family: Serif, Times New Roman;', >Skyscraper Data Overview: </h2>", unsafe_allow_html=True)
        st.markdown(f"""<p style= 'text-align: center; font-family: Serif, Times New Roman;'> The tallest skyscraper across all cities found in 
        the data is {largest:.2f} meters, located in {largest_city}.
        </p>
        <p style= 'text-align: center; font-family: Serif, Times New Roman;'> 
            The shortest skyscraper across all cities found in the data is {smallest:.2f} 
            meters, located in {smallest_city}. 
        </p>""", unsafe_allow_html = True)

    #Code for centering the pivot table based on code from ChatGPT. See section 8 of accompanying document.
    pivot_df = create_pivot_table()

    if pivot_df is not None:
        st.markdown(
            "<p style='text-align: center; font-family: Serif, Times New Roman;'>Here is a pivot table displaying the columns from "
            "the data set used in this website. It's important to note these are the averages from each city:</p>",
            unsafe_allow_html=True)

        html_table = pivot_df.to_html(index = True)
        table = f"""
        <div style="display: flex; justify-content: center; overflow-y: auto; max-height: 400px; width: 100%;">
            {html_table}
        </div>
        """
        st.markdown(table, unsafe_allow_html = True)


    else:
        st.error("Failed to create the pivot table")




    if len(cities) > 0 and max_height > 0 and min_floorsabove > 0:

        st.write('<div style="text-align:center; font-family: Serif, Times New Roman">Here is a pie chart displaying which city has the highest percentage of skyscrapers below your max height out of all the skyscrapers below your max height in these cities:</div>', unsafe_allow_html=True)
        st.pyplot(generate_piechart(series, cities))

        st.write('<div style="text-align:center; font-family: Serif, Times New Roman">Here is a bar chart displaying the average heights of skyscrapers under your selected max height in each city: </div>', unsafe_allow_html=True)
        st.pyplot(generate_bar_chart(skyscraper_height_averages(skyscraper_heights(data))))

        st.write('<div style="text-align:center; font-family: Serif, Times New Roman">Here is a boxplot displaying the min, max, Q1, median, Q3, and outlier values of skyscraper heights below your selected max height in your selected cities: </div>', unsafe_allow_html=True)
        st.pyplot(generate_boxplot(data, x='location.city', y='statistics.height',
                plot_type='seaborn',
                title="Heights of Skyscrapers"))

        completion_data = completion_status(data, cities)

        if not completion_data.empty:

            st.write(
                '<div style="text-align:center; font-family: Serif, Times New Roman">Here is a table displaying how many years it took each skyscraper in each city to be completed, and also if the skyscraper is incomplete: </div>',
                unsafe_allow_html=True)
            table_html = completion_data.to_html(index=True)
            table = f"""
                                    <div style="display: flex; justify-content: center; overflow-y: auto; max-height: 400px; width: 100%;">
                                        {table_html}
                                    </div>
                                    """
            st.markdown(table, unsafe_allow_html=True)
        else:
            st.error("No data available for the selected filters. ")

        st.write('<div style="text-align:center; font-family: Serif, Times New Roman">Here is a map of the average location of the cities you selected: </div>', unsafe_allow_html=True)
        generate_map(data)

main()


#data = filter_data(default_city, default_height, default_floors)
#counts = count_cities(default_city, data)
#st.pyplot(generate_piechart(counts, default_city))
#heights = skyscraper_heights(data)
#averages = skyscraper_height_averages(heights)
#st.pyplot(generate_bar_chart(averages))
#generate_map(data)
#st.pyplot(generate_boxplot(data, x='location.city', y='statistics.height',
                #plot_type='seaborn',
                #title="Heights of Skyscrapers" ))







