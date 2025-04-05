from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import tempfile  # import tempfile to create a temporary directory
import time

def scrape_page_with_selenium(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
    
    # Create a temporary directory for Chrome's user data
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_dir}")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load completely

        show_more_button = driver.find_element(By.LINK_TEXT, 'Show more')

        # Click the "Show More" button
        show_more_button.click()
        
        # Wait for new content to load after clicking the "Show More" button
        time.sleep(5)  # Adjust sleep time if necessary

        html = driver.page_source

    except Exception as e:
        driver.quit()
        return {'error': f'Error fetching URL with Selenium: {e}'}
    
    driver.quit()
    
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    target_div = soup.select('div.main-products-grid__results ul li')  # Adjust selector based on the HTML structure

    if target_div:
        extracted_data = []
        for div in target_div:
            title = div.select_one('product-card div.card__info-container div.card__info-inner p.card__title a')  # Example selector for the title
            price = div.select_one('product-card div.card__info-container div.card__info-inner div.price.price--top strong.price__current')
            
            data = {
                'title': title.get_text(strip=True) if title else 'No title',
                'price': price.get_text(strip=True) if price else 'No price'
            }
            extracted_data.append(data)

        return {'data': extracted_data}  # Return the extracted data
