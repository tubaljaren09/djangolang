import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_page_with_selenium(url):
    # Configure Selenium options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/58.0.3029.110 Safari/537.36'
    )
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')

    # Use remote Selenium server instead of local chromedriver
    selenium_url = os.getenv('SELENIUM_URL', 'http://selenium:4444/wd/hub')
    driver = webdriver.Remote(command_executor=selenium_url, options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        driver.get(url)
        # Wait until the product grid is loaded
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.main-products-grid__results ul li')
        ))
        
        # Try to click the "Show more" button if it's present
        try:
            show_more_button = wait.until(EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Show more')
            ))
            show_more_button.click()
            # Wait until new content is loaded
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.main-products-grid__results ul li')
            ))
        except Exception as click_exception:
            print(f"Warning: 'Show more' button issue: {click_exception}")
        
        html = driver.page_source
    except Exception as e:
        driver.quit()
        return {'error': f'Error fetching URL with Selenium: {e}'}
    
    driver.quit()
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.main-products-grid__results ul li')

    if not items:
        return {'error': 'Target div not found'}

    extracted_data = []
    for div in items:
        title_el = div.select_one(
            'product-card div.card__info-container '
            'div.card__info-inner p.card__title a'
        )
        price_el = div.select_one(
            'product-card div.card__info-container '
            'div.card__info-inner div.price.price--top '
            'strong.price__current'
        )
        extracted_data.append({
            'title': title_el.get_text(strip=True) if title_el else 'No title',
            'price': price_el.get_text(strip=True) if price_el else 'No price'
        })

    return {'data': extracted_data}
