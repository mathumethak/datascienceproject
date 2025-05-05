README FILE

# 🎬 Movie Data Scraper & Dashboard (2024)

This project is a full pipeline for scraping, storing, and visualizing IMDB movie data by genre for the year 2024. It consists of two main components:
- A **Selenium-based scraper** that extracts data from IMDB and saves it as CSV.
- A **Streamlit dashboard** that reads the data from a MySQL database and visualizes it interactively.

---

## 📁 Project Structure

📂 movie-dashboard-project/
├── scraper.py # Scrapes movie data from IMDB by genre
├── dashboard.py # Streamlit app to visualize and filter movie data
├── requirements.txt # Python dependencies
├── .env.example # Template for environment variables
└── README.md # Project documentation



---

## 🔧 Requirements

- Python 3.8+
- Google Chrome + ChromeDriver
- MySQL Server
- Libraries (see `requirements.txt`):
  - selenium
  - pandas
  - streamlit
  - matplotlib
  - seaborn
  - python-dotenv
  - sqlalchemy
  - pymysql

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Data-Scraping-and-Visualizations.git
cd Data-Scraping-and-Visualizations

2. Install Dependencies
pip install -r requirements.txt

3. Setup .env File
Create a .env file in the root directory using the provided .env.example:


DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=hostname
DB_PORT=portnumber
DB_NAME=databasename
TABLE_NAME=tablename
4. Run the Scraper
This script (scraper.py) scrapes multiple genres of movies from IMDB for 2024 and saves them as CSVs.
python scraper.py

5. Import Data into MySQL
After CSVs are generated (e.g. fantasy_movies_2024.csv), import the combined data (combined_movies_2024.csv) into your MySQL database.

📊 Running the Dashboard
Start the Streamlit app:

streamlit run dashboard.py
Open the local URL in your browser (usually http://localhost:8501).

📌 Features
Scrapes 2024 movie data by genre

Converts durations and votes to numeric formats

Saves and merges multiple genre CSVs

Loads data into MySQL

Interactive dashboard with:

Top 10 movies by rating and votes

Genre distributions and averages

Filterable view by duration, genre, rating, and vote count

Visuals: bar plots, pie chart, heatmap, boxplots, histograms

🛡️ Security
Never commit your actual passwords or .env files. Use .gitignore to keep sensitive files private.

📃 License
This project is licensed under the MIT License.

🙌 Acknowledgments
IMDB for data source

Selenium

Streamlit



---






