from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import tempfile

def scrape_page_with_selenium(url):
    # Configure Selenium options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
    
    # Create a temporary directory for a unique user data directory
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_dir}")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        driver.get(url)
        
        # Wait until the product grid is loaded
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.main-products-grid__results ul li')))
        
        # Try to click the "Show more" button if it's present
        try:
            show_more_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Show more')))
            show_more_button.click()
            # Wait until new content is loaded (you may adjust the selector as needed)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.main-products-grid__results ul li')))
        except Exception as click_exception:
            # If "Show more" isn't found or clickable, log the warning and continue
            print(f"Warning: 'Show more' button issue: {click_exception}")
        
        html = driver.page_source

    except Exception as e:
        driver.quit()
        return {'error': f'Error fetching URL with Selenium: {e}'}
    
    driver.quit()
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    target_div = soup.select('div.main-products-grid__results ul li')

    if target_div:
        extracted_data = []
        for div in target_div:
            title = div.select_one('product-card div.card__info-container div.card__info-inner p.card__title a')
            price = div.select_one('product-card div.card__info-container div.card__info-inner div.price.price--top strong.price__current')
            data = {
                'title': title.get_text(strip=True) if title else 'No title',
                'price': price.get_text(strip=True) if price else 'No price'
            }
            extracted_data.append(data)
        return {'data': extracted_data}
    else:
        return {'error': 'Target div not found'}
