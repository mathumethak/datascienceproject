import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# -------------------------- Streamlit Config -------------------------- #
st.set_page_config(page_title="🎬 Movie Data Dashboard", layout="wide")
sns.set_theme()

# -------------------------- MySQL Database Config -------------------------- #
db_user = "your_username"
db_password = "your_password"
db_host = "host_name"
db_port = "port_number"
db_name = "database_name"
table_name = "table_name"

# -------------------------- Load Data from MySQL -------------------------- #
@st.cache_data
def load_data():
    engine = create_engine(f"mysql+pymysql://db_user:db_password@host_name:{db_port}/{db_name}")
    connection = engine.connect()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, con=connection)
    return df

# Load data
try:
    df = load_data()
    if df.empty:
        st.warning("No data found in the MySQL table.")
        st.stop()
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# Convert key columns to numeric
df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')

# -------------------------- Tabs Setup -------------------------- #
tab1, tab2 = st.tabs(["📊 Dashboard", "🎛️ Filter Movies"])

# -------------------------- TAB 1: Dashboard -------------------------- #
with tab1:
    st.title("🎬 Movie Data Scraping and Visualization (via MySQL)")
    st.write("Data Source: MySQL Table → `movies`")

    st.subheader("📋 Full Dataset")
    st.dataframe(df, use_container_width=True)

    top_movies = df.sort_values(by=["Rating", "Votes"], ascending=[False, False]).head(10)
    st.subheader("1. Top 10 Movies by Rating and Votes")
    st.dataframe(top_movies)

    # Rating Bar Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_movies['Name'], top_movies['Rating'], color='skyblue')
    ax.set_title("Top 10 Movies by Rating")
    ax.set_xlabel("Movie Name")
    ax.set_ylabel("Rating")
    ax.tick_params(axis='x', rotation=90)
    st.pyplot(fig)

    # Votes Bar Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_movies['Name'], top_movies['Votes'], color='lightgreen')
    ax.set_title("Top 10 Movies by Votes")
    ax.set_xlabel("Movie Name")
    ax.set_ylabel("Number of Votes")
    ax.tick_params(axis='x', rotation=90)
    st.pyplot(fig)

    # Genre Distribution
    st.subheader("2. Genre Distribution")
    all_genres = df['Genre'].dropna().str.split(',').explode().str.strip()
    genre_counts = all_genres.value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    genre_counts.plot(kind='bar', ax=ax, color='orange')
    ax.set_title("Number of Movies per Genre")
    ax.set_xlabel("Genre")
    ax.set_ylabel("Count")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    st.dataframe(genre_counts, use_container_width=True)

    # Average Duration by Genre
    st.subheader("3. Average Duration by Genre")
    genre_duration = df.dropna(subset=['Genre', 'Duration'])
    genre_duration['Genre'] = genre_duration['Genre'].str.split(',').explode().str.strip()
    avg_duration = genre_duration.groupby('Genre')['Duration'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    avg_duration.plot(kind='barh', ax=ax, color='teal')
    ax.set_title("Average Duration per Genre")
    ax.set_xlabel("Duration (min)")
    st.pyplot(fig)
    st.dataframe(avg_duration, use_container_width=True)

    # Average Voting by Genre
    st.subheader("4. Average Voting Counts by Genre")
    genre_votes = df.dropna(subset=['Genre', 'Votes'])
    genre_votes['Genre'] = genre_votes['Genre'].str.split(',').explode().str.strip()
    avg_votes = genre_votes.groupby('Genre')['Votes'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    avg_votes.plot(kind='barh', ax=ax, color='purple')
    ax.set_title("Average Votes per Genre")
    st.pyplot(fig)
    st.dataframe(avg_votes, use_container_width=True)

    # Rating Distribution by Genre
    st.subheader("5. Rating Distribution by Genre")
    df_genre_rating = df.dropna(subset=['Genre', 'Rating'])
    df_genre_rating['Genre'] = df_genre_rating['Genre'].str.split(',').explode().str.strip()
    plot_type = st.selectbox("Choose plot type:", ["Boxplot", "Histogram"])
    fig, ax = plt.subplots(figsize=(12, 6))
    if plot_type == "Boxplot":
        sns.boxplot(data=df_genre_rating, x='Genre', y='Rating', ax=ax, palette='Set2')
        ax.set_title("Rating Boxplot by Genre")
        ax.tick_params(axis='x', rotation=45)
    else:
        top_genres = df_genre_rating['Genre'].value_counts().head(5).index
        for genre in top_genres:
            subset = df_genre_rating[df_genre_rating['Genre'] == genre]
            sns.histplot(subset['Rating'], kde=True, label=genre, bins=10)
        ax.set_title("Rating Histogram by Top Genres")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        ax.legend()
    st.pyplot(fig)

    # Rating Summary
    rating_summary = df_genre_rating.groupby('Genre')['Rating'].agg(
        Average_Rating='mean',
        Median_Rating='median',
        Min_Rating='min',
        Max_Rating='max',
        Movie_Count='count'
    ).sort_values(by='Average_Rating', ascending=False).round(2).reset_index()
    st.subheader("Rating Summary Stats by Genre")
    st.dataframe(rating_summary, use_container_width=True)

    # Top Rated Movie in Each Genre
    st.subheader("6. Top Rated Movie in Each Genre")
    top_rated_movies = []
    unique_genres = df_genre_rating['Genre'].unique()
    for genre in unique_genres:
        genre_movies = df[df['Genre'].str.contains(genre, case=False, na=False)]
        top_movie = genre_movies.loc[genre_movies['Rating'].idxmax()]
        top_rated_movies.append({
            'Genre': genre,
            'Top Rated Movie': top_movie['Name'],
            'Rating': top_movie['Rating'],
            'Votes': top_movie['Votes'],
            'Duration': top_movie['Duration']
        })
    st.dataframe(pd.DataFrame(top_rated_movies), use_container_width=True)

    # Pie Chart - Votes by Genre
    st.subheader("7. Most Popular Genres by Total Votes")
    genre_votes_sum = df.dropna(subset=['Genre', 'Votes'])
    genre_votes_sum['Genre'] = genre_votes_sum['Genre'].str.split(',').explode().str.strip()
    vote_totals = genre_votes_sum.groupby('Genre')['Votes'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(vote_totals, labels=vote_totals.index, autopct='%1.1f%%', startangle=90)
    ax.set_title("Total Voting Distribution by Genre")
    st.pyplot(fig)
    st.dataframe(vote_totals.reset_index().rename(columns={"Votes": "Total Votes"}), use_container_width=True)

    # Duration Extremes
    st.subheader("8. Duration Extremes (Shortest & Longest Movies)")
    valid_duration = df.dropna(subset=['Duration'])
    shortest = valid_duration.loc[valid_duration['Duration'].idxmin()]
    longest = valid_duration.loc[valid_duration['Duration'].idxmax()]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 Shortest Movie")
        st.write(f"**Name:** {shortest['Name']}")
        st.write(f"**Genre:** {shortest['Genre']}")
        st.write(f"**Duration:** {shortest['Duration']} min")
        st.write(f"**Rating:** {shortest['Rating']}")
    with col2:
        st.markdown("### 🔵 Longest Movie")
        st.write(f"**Name:** {longest['Name']}")
        st.write(f"**Genre:** {longest['Genre']}")
        st.write(f"**Duration:** {longest['Duration']} min")
        st.write(f"**Rating:** {longest['Rating']}")

    # Heatmap - Average Ratings by Genre
    st.subheader("9. Heatmap: Average Rating by Genre")
    avg_rating = df.groupby('Genre')['Rating'].mean().sort_values(ascending=False).reset_index()
    heatmap_data = avg_rating.pivot_table(index='Genre', values='Rating')
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data.T, annot=True, cmap='coolwarm')
    plt.title("Average Ratings by Genre")
    st.pyplot(plt.gcf())
    st.dataframe(avg_rating, use_container_width=True)

    # Correlation Analysis: Rating vs Votes
    st.subheader("10. Correlation: Rating vs. Votes")
    correlation_df = df.dropna(subset=['Rating', 'Votes'])
    correlation_df['Votes'] = pd.to_numeric(correlation_df['Votes'], errors='coerce')
    correlation_df['Rating'] = pd.to_numeric(correlation_df['Rating'], errors='coerce')
    correlation = correlation_df['Rating'].corr(correlation_df['Votes'])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=correlation_df, x='Votes', y='Rating', ax=ax, color='coral', alpha=0.6)
    ax.set_title(f"Ratings vs Votes (Correlation = {correlation:.2f})")
    ax.set_xscale("log")
    st.pyplot(fig)
    st.markdown(f"**Correlation Coefficient:** `{correlation:.2f}`")

with tab2:
     st.header("🎛️ Interactive Movie Filter")

     st.sidebar.header('Filter Movies')

    # Duration Filter
     duration_filter = st.sidebar.selectbox(
        'Select Duration Range (in hours)',
        ['< 1.5 hrs', '< 2 hrs', '2-3 hrs', '> 3 hrs']
     )

    # Rating Filter
     rating_filter = st.sidebar.slider(
        'Minimum IMDb Rating',
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
     )

    # Votes Filter
     votes_filter = st.sidebar.number_input(
        'Minimum Number of Votes',
        min_value=0,
        max_value=int(df['Votes'].max()),
        value=10000,
        step=1000
     )

    # Genre Filter
     all_genres_set = df['Genre'].dropna().str.split(',').explode().str.strip().unique()
     genre_filter = st.sidebar.multiselect(
        'Select Genres',
        options=sorted(all_genres_set),
        default=[]
     )

    # Apply filters
     filtered_df = df.copy()

     if duration_filter == '< 1.5 hrs':
        filtered_df = filtered_df[filtered_df['Duration'] < 90]
     elif duration_filter == '< 2 hrs':
        filtered_df = filtered_df[filtered_df['Duration'] < 120]
     elif duration_filter == '2-3 hrs':
        filtered_df = filtered_df[(filtered_df['Duration'] >= 120) & (filtered_df['Duration'] <= 180)]
     else:
        filtered_df = filtered_df[filtered_df['Duration'] > 180]

     filtered_df = filtered_df[filtered_df['Rating'] >= rating_filter]
     filtered_df = filtered_df[filtered_df['Votes'] >= votes_filter]

     if genre_filter:
        genre_pattern = '|'.join(genre_filter)
        filtered_df = filtered_df[filtered_df['Genre'].str.contains(genre_pattern, case=False, na=False)]

     st.markdown("### 🎬 Filtered Movies Based on the Selected Criteria")
     st.dataframe(filtered_df, use_container_width=True)
