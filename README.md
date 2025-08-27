# Extracting Cookies Using Webcrawler

This project contains an advanced web crawler built with Python and Selenium, designed to collect website cookies for privacy analysis and research. The crawler simulates human-like behavior to effectively gather data from modern, dynamic websites and is specifically configured to avoid common anti-bot detection mechanisms.

The primary goal of this tool is to create a dataset of cookies that can be used for classification tasks, such as evaluating compliance with privacy regulations like the GDPR.

## Features

-   **Anti-Detection**: Implements several techniques to avoid being flagged as a bot:
    -   Disables automation-controlled flags in Chrome.
    -   Hides the `navigator.webdriver` property.
    -   Rotates `User-Agent` strings to mimic different real browsers.
-   **Human-like Interaction**: The crawler simulates a real user to trigger the setting of dynamic cookies:
    -   **Smart Consent Handling**: Automatically detects and clicks common "Accept Cookies" banners in multiple languages (including English and Persian).
    -   **Dynamic Scrolling**: Scrolls down the page to load lazy-loaded content.
    -   **Random Clicks**: Clicks on a few random internal links and navigates back to simulate browsing behavior.
-   **Flexible Input**: Reads a list of target websites from a simple CSV file with no headers.
-   **Structured Output**: Extracts all cookies and saves them in a clean, structured CSV format (`Domain`, `cookie_domain`, `name`, `value`), ready for analysis.
-   **Robustness**: Includes error handling for network timeouts, unclickable elements, and other common crawling exceptions.

---

## Getting Started 

Follow these instructions to set up and run the crawler on your local machine.

### Prerequisites

-   **Python 3.8+**
-   **Google Chrome** browser installed
-   **pip** (Python package installer)

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create and Activate a Virtual Environment (Recommended)**:
    -   Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    -   macOS / Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Required Libraries**:
    The project uses several Python libraries. Install them all with this command:
    ```bash
    pip install selenium pandas
    ```
    *Note: The script also automatically handles the installation of the correct `chromedriver` for your version of Chrome.*

---

## How to Run

1.  **Prepare Your URL List**:
    -   Create a CSV file in the main project directory (e.g., `urls.csv`).
    -   Add the websites you want to crawl to this file, one per line, in the first column. **Do not add a header row.**
    -   Example `urls.csv`:
        ```
        example.com
        another-website.org
        test-site.net
        ```

2.  **Run the Crawler Script**:
    Execute the main Python script from your terminal:
    ```bash
    python your_script_name.py
    ```
    *(Replace `your_script_name.py` with the actual name of your Python file)*

3.  **Provide Input**:
    The script will prompt you to enter the path to your URL file:
    ```
    Enter the path to your CSV file containing website URLs: urls.csv
    ```

4.  **Monitor the Process**:
    The crawler will start, initializing a headless Chrome browser. You will see real-time logs in your terminal as it navigates to each URL, interacts with the page, and extracts cookies.

5.  **Get the Output**:
    Once the crawl is complete, a new file named `collected_cookies.csv` will be created in the same directory. This file contains all the cookies collected during the session, formatted and ready for your analysis.

---

## Code Overview

-   **`initialize_driver()`**: Sets up the Selenium Chrome WebDriver with all the anti-detection options.
-   **`Maps_and_interact()`**: The core function for visiting a URL and simulating user behavior (handling consent, scrolling, clicking).
-   **`extract_cookies()`**: Retrieves all cookies from the current browser session.
-   **`if __name__ == "__main__":`**: The main execution block that orchestrates the entire process from reading the input file to saving the final output.
