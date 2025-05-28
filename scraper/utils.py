import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

def scrape_page_with_selenium(url):
    # 1) Configure Selenium options
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

    # 2) Determine remote Selenium URL (public Railway default)
    selenium_url = os.getenv(
        'SELENIUM_URL',
        'https://standalone-chrome.up.railway.app/wd/hub'
    )

    driver = None
    try:
        # 3) Connect to remote WebDriver
        driver = webdriver.Remote(command_executor=selenium_url, options=options)
        # 4) Increase timeouts for page loads & element waits
        driver.set_page_load_timeout(60)          # 60s for page load
        wait = WebDriverWait(driver, 30)          # 30s for element conditions

        # 5) Navigate and wait for the product grid
        try:
            driver.get(url)
        except TimeoutException:
            return {'error': 'Page load timed out after 60 seconds'}

        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.main-products-grid__results ul li')
            ))
        except TimeoutException:
            return {'error': 'Products grid did not appear within 30 seconds'}

        # 6) Optionally click “Show more”
        try:
            show_more = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Show more')))
            show_more.click()
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.main-products-grid__results ul li')
            ))
        except TimeoutException:
            # No Show more button or it didn’t load more items in time
            pass

        html = driver.page_source

    except WebDriverException as e:
        return {'error': f'Selenium connection error: {e}'}

    finally:
        if driver:
            driver.quit()

    # 7) Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.main-products-grid__results ul li')

    if not items:
        return {'error': 'No products found on the page'}

    # 8) Extract data
    extracted = []
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
        extracted.append({
            'title': title_el.get_text(strip=True) if title_el else 'No title',
            'price': price_el.get_text(strip=True) if price_el else 'No price'
        })

    return {'data': extracted}
