import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
import random
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
import re

def initialize_driver(headless=True):
    """
    Initializes a Selenium WebDriver for Chrome with anti-detection measures.
    
    Args:
        headless (bool): If True, runs the browser in headless mode (without a UI).
                         Defaults to True for efficiency and server environments.
                         
    Returns:
        webdriver.Chrome: An initialized Chrome WebDriver instance.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent spoofing to mimic a real browser
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.implicitly_wait(10) # Set a default implicit wait time for element lookups
    
    # Execute JavaScript to further mask automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def navigate_and_interact(driver, url, max_scrolls=3, scroll_pause_time=2):
    """
    Navigates to a given URL, handles cookie consent, and simulates user interaction
    through scrolling and random clicks.
    
    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        url (str): The URL to navigate to.
        max_scrolls (int): Maximum number of times to scroll down the page.
        scroll_pause_time (int): Base time to pause between scrolls.
        
    Returns:
        bool: True if navigation and initial interaction were successful, False otherwise.
    """
    # The URL formatting should ideally happen BEFORE calling this function,
    # to ensure consistency. However, adding a check for robustness.
    if not re.match(r'^https?://', url):
        print(f"Invalid URL format: {url}. Please provide a full URL including http:// or https://")
        return False

    try:
        driver.get(url)
        print(f"Navigating to: {url}")
        
        WebDriverWait(driver, 30).until( # Increased timeout for initial page load
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully (body element found).")
        
        # --- Handle potential cookie consent banners or pop-ups ---
        try:
            # Common XPath/CSS selectors for cookie consent buttons.
            consent_selectors = [
                (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok') or contains(@aria-label, 'accept') or contains(@title, 'accept')]"),
                (By.CSS_SELECTOR, "button[id*='cookie'][id*='accept'], a[id*='cookie'][id*='accept'], button[class*='cookie'][class*='accept'], a[class*='cookie'][class*='accept']"),
                (By.XPATH, "//div[contains(@class, 'cookie-consent')]//button | //div[contains(@id, 'cookie-consent')]//button"),
                (By.XPATH, "//button[text()='Allow all cookies']"),
                (By.XPATH, "//button[text()='Accepter']"), # For non-English sites
                (By.XPATH, "//button[contains(text(), 'قبول')]"), # Example for Persian "Accept"
                (By.XPATH, "//button[contains(text(), 'متوجه شدم')]") # Example for Persian "I understand"
            ]
            
            consent_button = None
            for selector_type, selector_value in consent_selectors:
                try:
                    consent_button = WebDriverWait(driver, 10).until( # Shorter wait for specific element
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if consent_button:
                        print(f"Found potential cookie consent button using {selector_type}: {selector_value}")
                        break # Found a button, exit loop
                except TimeoutException:
                    continue # Try next selector
            
            if consent_button:
                try:
                    consent_button.click()
                    print("Clicked cookie consent button.")
                    time.sleep(random.uniform(2, 4)) # Give time for banner to disappear
                except ElementClickInterceptedException:
                    print("Click intercepted, trying JavaScript click for consent.")
                    driver.execute_script("arguments[0].click();", consent_button)
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"Error clicking consent button: {e}")
            else:
                print("No cookie consent banner found or clickable within timeout using common selectors.")
        except Exception as e:
            print(f"General error handling cookie banner: {e}")

        # --- Simulate human-like scrolling to load dynamic content ---
        last_height = driver.execute_script("return document.body.scrollHeight")
        print("Starting scroll simulation...")
        for i in range(max_scrolls):
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);") # Scroll by 80% of view height
            time.sleep(scroll_pause_time + random.uniform(0.5, 1.5)) # Add randomness
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print(f"Scroll reached end of page after {i+1} scrolls.")
                break
            last_height = new_height
        print(f"Finished scrolling. Scrolled {min(i+1, max_scrolls)} times.")

        # --- Simulate random clicks on a few links to mimic user behavior ---
        try:
            # Find visible links, excluding internal anchors and mailto/tel links
            all_links = driver.find_elements(By.TAG_NAME, "a")
            clickable_links = []
            for link in all_links:
                href = link.get_attribute('href')
                if link.is_displayed() and href and not href.startswith('#') and not href.startswith('mailto:') and not href.startswith('tel:'):
                    # Filter out links that stay on the same page or are purely navigational
                    if href != url and not (href.startswith(url.split('?')[0].split('#')[0]) and len(href) > len(url.split('?')[0].split('#')[0]) and '#' in href):
                        clickable_links.append(link)
            
            if clickable_links:
                num_clicks = min(random.randint(1, 3), len(clickable_links)) # Click 1 to 3 random links
                print(f"Attempting to click {num_clicks} random links.")
                for _ in range(num_clicks):
                    target_link = random.choice(clickable_links)
                    try:
                        link_width = target_link.size.get('width', 0) # Use .get with default 0
                        link_height = target_link.size.get('height', 0)

                        # Validate dimensions for random.randint
                        if link_width <= 1 or link_height <= 1:
                            print(f"Skipping click on tiny/invisible link (dim: {link_width}x{link_height}): {target_link.get_attribute('href')}")
                            continue # Skip this link and try next if available
                        
                        offset_x = random.randint(1, link_width - 1)
                        offset_y = random.randint(1, link_height - 1)

                        # Use ActionChains for human-like click with offset
                        ActionChains(driver).move_to_element_with_offset(target_link, 
                                                                         offset_x, 
                                                                         offset_y).click().perform()
                        print(f"Clicked random link: {target_link.get_attribute('href')}")
                        time.sleep(random.uniform(3, 7)) # Random wait after click
                        
                        driver.back() # Go back to the original page
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        print("Returned to previous page.")
                    except StaleElementReferenceException:
                        print("Stale element, link might have reloaded or moved. Skipping click.")
                        # Re-find elements if StaleElementReferenceException is common
                        all_links_recheck = driver.find_elements(By.TAG_NAME, "a")
                        clickable_links = [link for link in all_links_recheck if link.is_displayed() and link.get_attribute('href') and not link.get_attribute('href').startswith('#')]
                        if not clickable_links: 
                            print("No more clickable links after stale element recheck.")
                            break # Exit loop if no more links can be found
                    except ElementClickInterceptedException:
                        print("Click intercepted on random link, trying next.")
                    except Exception as e:
                        print(f"Error clicking random link: {e}")
            else:
                print("No suitable clickable links found for random interaction.")
        except Exception as e:
            print(f"Error during random link interaction: {e}")

    except TimeoutException:
        print(f"Timeout while loading {url} (initial page load or element detection). Skipping.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during navigation to {url}: {e}")
        return False
    return True

def extract_cookies(driver, url):
    """
    Extracs cookies from the current WebDriver session, formatting them to match
    'Domain', 'cookie_domain', 'name', and 'value' columns.
    
    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        url (str): The URL from which cookies were collected (for context, though not stored).
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a cookie
              with only 'Domain', 'cookie_domain', 'name', and 'value' attributes.
    """
    cookies_list = []
    try:
        all_cookies = driver.get_cookies()
        for cookie in all_cookies:
            # Get the domain as provided by the cookie
            domain_raw = cookie.get('domain', '').lstrip('.') # Remove leading dot if present

            # Construct 'cookie_domain' with a leading dot
            cookie_domain_with_dot = '.' + domain_raw if domain_raw else ''

            cookies_list.append({
                # Ensure these keys EXACTLY match the column names
                'Domain': domain_raw,
                'cookie_domain': cookie_domain_with_dot,
                'name': cookie.get('name', ''),
                'value': cookie.get('value', '')
            })
        print(f"Extracted {len(cookies_list)} cookies from {url}.")
    except Exception as e:
        print(f"Error extracting cookies from {url}: {e}")
    return cookies_list

def load_existing_data(file_path):
    """
    Loads existing data from a CSV or Excel file into a Pandas DataFrame.
    
    Args:
        file_path (str): The path to the data file.
        
    Returns:
        pd.DataFrame: The loaded DataFrame, or an empty DataFrame if the file
                      does not exist or an error occurs.
    """
    if os.path.exists(file_path):
        try:
            if file_path.endswith('.xlsx'):
                return pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            else:
                print(f"Unsupported file format for loading: {file_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading existing data from {file_path}: {e}")
            return pd.DataFrame()
    print(f"No existing data file found at: {file_path}. Starting with empty DataFrame.")
    return pd.DataFrame()

def append_and_save_data(new_data_df, output_file_path, existing_file_path=None, output_format='csv'):
    """
    Saves new data to a file, ensuring column names match the specified format.
    
    Args:
        new_data_df (pd.DataFrame): The new data to save.
        output_file_path (str): The path where the data will be saved.
        existing_file_path (str, optional): Path to an existing file (not used for merging in this independent script).
        output_format (str): The format to save the output file ('csv' or 'xlsx').
    """
    # Define the exact column order and names that the final output should have
    target_columns = ['Domain', 'cookie_domain', 'name', 'value']

    # Reindex the new data to precisely match the target columns
    final_df = new_data_df.reindex(columns=target_columns, fill_value=None)
            
    if output_format == 'csv':
        final_df.to_csv(output_file_path, index=False, encoding='utf-8')
        print(f"Data saved to {output_file_path} in CSV format.")
    elif output_format == 'xlsx':
        final_df.to_excel(output_file_path, index=False, engine='xlsxwriter')
        print(f"Data saved to {output_file_path} in XLSX format.")
    else:
        print("Unsupported output format. Data not saved.")

def format_url_from_domain(domain: str) -> str:
    """
    Formats a raw domain string into a full HTTPS URL with 'www.' if missing.
    
    Args:
        domain (str): The raw domain string (e.g., "example.com", "sub.example.com").
        
    Returns:
        str: The formatted URL (e.g., "https://www.example.com/").
    """
    # Remove any existing protocol
    domain = re.sub(r'^(http|https)://', '', domain, flags=re.IGNORECASE)
    # Remove any trailing slash
    domain = domain.rstrip('/')

    # Add 'www.' if it's a typical root domain (e.g., example.com) and doesn't already have 'www.'
    # or if it's just a single part (e.g., 'google' -> 'www.google')
    if not domain.lower().startswith('www.'):
        parts = domain.split('.')
        # If it's a simple domain (e.g., 'example.com') or a very short domain, add 'www.'
        # This is a heuristic, assuming most top-level sites use 'www.' by default if not a specific subdomain.
        if len(parts) <= 2 or (len(parts) > 2 and all(p.lower() != 'www' for p in parts)):
            domain = f"www.{domain}"
    
    # Ensure it starts with https://
    return f"https://{domain}/"


if __name__ == "__main__":
    # Define input CSV file path
    csv_file_path = input("Enter the path to your CSV file containing website URLs: ").strip()
    
    # Define output file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_collected_cookies_path_csv = os.path.join(script_dir, 'collected_cookies.csv')
    output_collected_cookies_path_xlsx = os.path.join(script_dir, 'collected_cookies.xlsx')

    target_urls = []
    if os.path.exists(csv_file_path):
        try:
            # Read CSV without a header, assuming URLs are in the first column (index 0)
            df = pd.read_csv(csv_file_path, header=None)
            
            # Extract URLs from the first column (index 0)
            raw_domains = df.iloc[:, 0].dropna().astype(str).tolist() # .iloc[:, 0] selects the first column
            
            for domain in raw_domains:
                formatted_url = format_url_from_domain(domain)
                target_urls.append(formatted_url)
            print(f"Loaded {len(target_urls)} URLs from '{csv_file_path}'.")

        except Exception as e:
            print(f"Error reading CSV file or processing URLs: {e}")
            exit()
    else:
        print(f"Error: CSV file not found at '{csv_file_path}'. Please check the path.")
        exit()
        
    if not target_urls:
        print("No valid URLs found in the CSV file. Exiting.")
        exit()

    all_session_cookies = []

    print("\n--- Starting Web Crawl for Cookie Collection ---")
    driver = None # Initialize driver outside the loop to handle potential errors before loop

    try:
        print("Initializing Selenium WebDriver (headless mode)...")
        driver = initialize_driver(headless=True)
        print("WebDriver initialized successfully.")

        for i, url in enumerate(target_urls[450:500]):
            print(f"\n--- Processing URL {i+1}/{len(target_urls[450:500])}: {url} ---")
            
            # Navigate and interact with the website
            success = navigate_and_interact(driver, url, max_scrolls=5, scroll_pause_time=2)
            
            if success:
                # Extract cookies in format directly
                current_url_cookies = extract_cookies(driver, url)
                if current_url_cookies:
                    all_session_cookies.extend(current_url_cookies)
                else:
                    print(f"No cookies extracted from {url} or an error occurred during extraction for this URL.")
            else:
                print(f"Failed to navigate and interact with {url}. Skipping cookie extraction for this URL.")
            
            # Introduce a random delay between URLs to mimic human Browse and avoid detection
            time.sleep(random.uniform(5, 10)) # Wait 5-10 seconds before next URL

    except Exception as e:
        print(f"An unrecoverable error occurred during the crawling process: {e}")
    finally:
        if driver:
            print("\n--- Crawl session finished. Quitting WebDriver ---")
            driver.quit()
        
    if all_session_cookies:
        print(f"\nTotal cookies collected across all URLs: {len(all_session_cookies)}")
        # Create DataFrame from the list of cookie dictionaries
        collected_cookies_df = pd.DataFrame(all_session_cookies)
        
        print("Saving collected cookies to files...")
        
        # Save to CSV
        append_and_save_data(collected_cookies_df, 
                             output_file_path=output_collected_cookies_path_csv, 
                             output_format='csv')
        
        # # Save to XLSX
        # append_and_save_data(collected_cookies_df, 
        #                      output_file_path=output_collected_cookies_path_xlsx, 
        #                      output_format='xlsx')
        
        print("\n--- Cookie Collection Process Completed ---")
    else:
        print("\nNo cookies were collected during this session.")