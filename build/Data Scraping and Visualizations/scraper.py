from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Setup WebDriver
driver = webdriver.Chrome()

# List of genres to scrape
#genres = ["biography"]
genres = ["fantasy", "adventure", "family", "biography", "animation"]

# Function to convert votes to integers after scraping
def convert_votes_to_int(vote):
    try:
        # Ensure that vote is a string (if it's an int, convert it to string)
        if isinstance(vote, int):
            vote = str(vote)
        
        # Clean the vote string by removing unwanted characters
        vote = vote.strip()  # Remove leading and trailing spaces

        # Remove parentheses, commas, and any unwanted characters
        vote = vote.replace('(', '').replace(')', '')  # Remove parentheses
        vote = vote.replace(',', '')  # Remove commas
        vote = vote.strip()  # Remove any remaining spaces

        # Check if the vote contains 'K' (for thousands)
        if 'K' in vote:
            vote = vote.replace('K', '')  # Remove 'K'
            vote = float(vote) * 1000  # Convert to float and multiply by 1000
        else:
            # Convert to float, ensuring it's valid
            vote = float(vote)

        # Convert float to int (round it if necessary)
        return int(vote)
    except Exception as e:
        print(f"Skipping invalid vote: '{vote}', error: {e}")
        return 0  # Default to 0 for invalid votes


def convert_duration_to_minutes(duration):
    try:
        # If the duration contains hours and minutes (e.g., "1h 30m")
        if 'h' in duration and 'm' in duration:
            hours = int(duration.split('h')[0].strip())  # Extract hours
            minutes = int(duration.split('h')[1].split('m')[0].strip())  # Extract minutes
            total_minutes = (hours * 60) + minutes  # Convert hours to minutes and add minutes
        # If the duration contains only minutes (e.g., "90m")
        elif 'm' in duration:
            minutes = int(duration.split('m')[0].strip())  # Extract minutes
            total_minutes = minutes
        elif 'h' in duration:
            hours = int(duration.split('h')[0].strip())  # Extract minutes
            total_minutes = hours * 60
        else:
            total_minutes = 0  # If the format is unexpected, set to 0
        
        return total_minutes
    except Exception as e:
        print(f"Error converting duration: {e}")
        return 0  # Return 0 if there's an error

# Function to scrape movie details from the page
def scrape_movies():
    names = []
    votes = []
    durations = []
    ratings = []
    
    movies = driver.find_elements(By.XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li')
    
    if not movies:
        print("No movies found on the page!")
    
    for movie in movies:
        try:
            name = movie.find_element(By.XPATH, './div/div/div/div[1]/div[2]/div[1]/a/h3').text
            vote = movie.find_element(By.XPATH, './div/div/div/div[1]/div[2]/span/div/span/span[2]').text
            duration = movie.find_element(By.XPATH, './div/div/div/div[1]/div[2]/div[2]/span[2]').text
            rating = movie.find_element(By.XPATH, './div/div/div/div[1]/div[2]/span/div/span/span[1]').text
            
            # Clean and convert vote
            votes.append(convert_votes_to_int(vote))
            duration_minutes = convert_duration_to_minutes(duration)  # Convert duration to minutes
            #duration .append(convert_duration_to_minutes(duration))

            #rating - convert float into int
            #rating=round(float(rating))

            if rating:
              rating = round(float(rating))  # Convert rating to integer by rounding
            else:
              rating = 0  # Default to 0 if no rating is found

            # Collect other details
            names.append(name)
            durations.append(duration_minutes)
            ratings.append(rating)
        except Exception as e:
            print(f"Error extracting data for a movie: {e}")
            continue
    
    return names, votes, durations, ratings

# Function to load more movies until all are scraped
def next_page():
    try:
        # Wait for the "Load More" button to become clickable
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[2]/div/span/button/span/span'))
        )

        # Scroll to the "Load More" button to make sure it's in view
        ActionChains(driver).move_to_element(load_more_button).perform()
        print("Clicking 'Load More' button...")
        load_more_button.click()
        time.sleep(3)  # Wait for new movies to load
        return True
    except Exception as e:
        print("Error with 'Load More' button or no more pages:", e)
        return False

# Function to scrape movies from a specific genre and save to CSV
def scrape_genre_movies(genre):
    imdb_url = f"https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&genres={genre}"
    driver.get(imdb_url)
    time.sleep(5)  # Wait for page to load (increase wait time if necessary)

    # Initialize empty lists for each genre to store the movie details
    names = []
    votes = []
    durations = []
    ratings = []
    
    # Loop to keep clicking "Load More" until all pages are loaded
    while next_page():
        print(f"Loading more {genre} movies...")

    # Get movie details after all pages are loaded
    additional_names, additional_votes, additional_durations, additional_ratings = scrape_movies()
    names.extend(additional_names)
    votes.extend(additional_votes)
    durations.extend(additional_durations)
    ratings.extend(additional_ratings)

    # Check if data is collected
    print(f"Collected {len(names)} movies in {genre} genre.")

    # Create a DataFrame for the genre and save it to a CSV file
    genre_data = pd.DataFrame({
        'Name': names,
        'Genre': [genre] * len(names),  # Assign the genre to each movie
        'Rating': ratings,
        'Votes': votes,
        'Duration': durations
    })
    
    genre_file = f"{genre}_movies_2024.csv"
    genre_data.to_csv(genre_file, index=False)
    print(f"Data saved to {genre_file}")

# Loop through the genres and scrape data
for genre in genres:
    print(f"Scraping {genre} genre...")
    scrape_genre_movies(genre)

# Close the WebDriver
driver.quit()

# Now combining all genre CSVs into a single DataFrame
#genre_files = ["biography_movies_2024.csv"]
genre_files = ["fantasy_movies_2024.csv", "adventure_movies_2024.csv", "family_movies_2024.csv", "biography_movies_2024.csv", "animation_movies_2024.csv"]
dataframes = []

for genre_file in genre_files:
    try:
        df = pd.read_csv(genre_file)  # Read each genre CSV into a DataFrame
        dataframes.append(df)  # Append the DataFrame to the list
        print(f"Successfully read {genre_file}")
    except Exception as e:
        print(f"Error reading {genre_file}: {e}")

# Concatenate all DataFrames into one
combined_data = pd.concat(dataframes, ignore_index=True)

# After scraping the data, apply the conversion to the 'Votes' column
combined_data['Votes'] = combined_data['Votes'].apply(convert_votes_to_int)

# Save the combined DataFrame to a new CSV file
combined_data.to_csv('combined_movies_2024.csv', index=False)

# Print confirmation
print("Combined data saved to combined_movies_2024.csv")
