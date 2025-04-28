from bs4 import BeautifulSoup
import requests 
import streamlit as st
import pandas as pd

st.set_page_config('Taiko No Tatsujin Data', '🥁', layout='wide')
st.title('Taiko No Tatsujin!')

@st.cache_data
def scrape_website():

    base_url='https://taiko.namco-ch.net/taiko/en/songlist/'
    res = requests.get(base_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    

    music_categories = [category_anchor.get('href') for category_anchor in soup.select_one('nav#sgnavi').select('a')]

    song_titles = []
    categories = []
    artists = []
    easy_lv = []
    normal_lv = []
    hard_lv = []
    extreme_lv = []
    inner_extreme_lv = []

    for category in music_categories:

        category_soup = BeautifulSoup(requests.get(base_url + category).content, 'html.parser')
        category_name = category.split('.')[0].title()

        song_rows = category_soup.select_one('table').select('tr')[2:]
        
        for row in song_rows:
            
            song_info = row.select_one('th').get_text(strip=True, separator='|').split('|')
            
            if len(song_info) > 1:
                title, *others, artist = song_info
            else:
                title = song_info[0]
                artist = '-'

            papamama, easy, normal, hard, extreme, inner_extreme, *vid = row.select('td')
            
            # Append data to relevant lists. For difficulty ratings, we can convert them back into ints.
            song_titles.append(title)
            categories.append(category_name)
            artists.append(artist)
            easy_lv.append(int(easy.text))
            normal_lv.append(int(normal.text))
            hard_lv.append(int(hard.text))
            extreme_lv.append(int(extreme.text))

            inner_extreme_lv.append(None if inner_extreme.text == '-' else int(inner_extreme.text))

    df = pd.DataFrame({
        'Song Title': song_titles,
        'Category': categories,
        'Artist': artists,
        'Easy': easy_lv,
        'Normal': normal_lv,
        'Hard': hard_lv,
        'Extreme': extreme_lv,
        'Extreme (Inner)': inner_extreme_lv
        
    })
    
    return df

###########################

df = scrape_website()

diff_colors = ['#FF2703', '#8CB852', '#435935', '#DB1885', '#7135DB']
cat_list = df.groupby('Category').groups.keys()
diff_list = ['Easy', 'Normal', 'Hard', 'Extreme', 'Extreme (Inner)']


# Create two columns to show the charts and pills selection widgets side by side
col1, col2= st.columns(2)

# One method to write into columns: using dot notation

# Display dataframe
col1.dataframe(df, height=400)

# Display bar chart: No. of songs per category
col2.write("Number of songs per category")
col2.bar_chart(df['Category'].value_counts(), horizontal=True, height=356)

# Display input widgets for user to modify data displayed
chosen_diff = col1.pills('View difficulty distribution for levels:', diff_list, default='Easy')
chosen_category = col2.pills('View difficulty distribution for categories:', cat_list, selection_mode = 'multi', default=cat_list)
stacked = col2.checkbox('Stack bars?', value=True)

# pills will return the chosen option (by default) / a list of chosen options (if selection_mode is 'multi').
# checkbox will return either True (if checked) or False (if unchecked).

# Error message for when user did not choose a difficulty (df cannot be generated)
if not chosen_diff: # Equivalent to if chosen_diff == None
    st.error('Please choose a difficulty to view charts.')
    
else: # If a difficulty is chosen, we will be able to display the charts.

    # Another method to write into columns: using with notation.
    with col1:
        st.subheader("Rating distribution of all songs")
        
        # Display the rating distribution of the chosen difficulty in the form of a bar chart.
        st.bar_chart(df[chosen_diff].value_counts(),\
                    x_label=chosen_diff + ' rating', y_label='No. of Songs',\
                    color=diff_colors[diff_list.index(chosen_diff)])
                    # You can modify the labels on the chart!
                    # The color is dependent on the difficulty chosen. They are defined in diff_colors.

    with col2:
        st.subheader("Rating distribution according to categories")
        
        # If no category is chosen, no data will be shown.
        # We can display a warning message to ask the user to choose at least one category.
        if not chosen_category:
            st.warning("Please choose at least one category.")
        else:
            # Grouping by Category, then counting according to difficulty rating.
            difficulty_df = pd.DataFrame(df.groupby(['Category', chosen_diff]).count().reset_index())
    
            # Further filtering: only include selected categories from the chosen_category pills widget
            difficulty_df = difficulty_df[difficulty_df['Category'].isin(chosen_category)]
            
            # Display the bar chart:
            st.bar_chart(difficulty_df,\
                        x=chosen_diff, y='Song Title',\
                        x_label = chosen_diff + ' rating', y_label='No. of Songs',\
                        color='Category', stack=stacked)




