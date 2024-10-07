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
    - fetched_products.json (Start with an empty array `[]` or add a few product ids to limit the number of products to be scraped)

4. **Generate a Google Sheets API service account key:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project or select an existing one.
    - Enable the Google Sheets API for your project.
    - Go to "Credentials" and click "Create credentials" > "Service account key".
    - Fill in the service account details and select "JSON" as the key type.
    - Download the JSON file and rename it to `service_account.json`.
    - Place the `service_account.json` file in the root directory of the project.

5. **Set up Google Sheets permissions:**
    - Open the `service_account.json` file and copy the "client_email" value.
    - Create a new Google Sheet or use an existing one for the scraper output.
    - Share the Google Sheet with the email address you copied, giving it edit permissions.

6. **Configure the .env file:**
    - Rename `.env.sample` to `.env`.
    - Open the `.env` file and add your Google Sheet ID:
      ```
      SPREADSHEET_ID=your_google_sheet_id_here
      ```
    - You can find the Sheet ID in the URL of your Google Sheet:
      https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=0

## Execute the Python App

1. **Run the scraper:**
    ```sh
    python app.py
    ```

2. **Check the output:**
    - The output will be saved the google sheets id mentioned in the .env file.