# acquire-scraper
Scraper for acquire app

## Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/bytes2ravi/acquire-scraper.git
    cd acquire-scraper
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Replace Sample Files

**Locate the example files and replace them with your own:**
    - .env.sample
    - service_account.json.sample (Replace with your own service account key)
    - fetched_products.json (Start with an empty array `[]` or add a few product ids to limit the number of products to be scraped)

## Execute the Python App

1. **Run the scraper:**
    ```sh
    python app.py
    ```

2. **Check the output:**
    - The output will be saved the google sheets id mentioned in the .env file.