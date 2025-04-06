# scraper/views.py

from django.shortcuts import render
from .utils import scrape_page_with_bs4
import re

def parse_price(price_str):
    """Clean and convert price string to float."""
    return float(re.sub(r'[^\d.]', '', price_str)) if price_str else 0.0

def home(request):
    context = {}
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            result = scrape_page_with_bs4(url)
            if 'error' in result:
                context['error'] = result['error']
            else:
                processors = result.get('data', [])
                
                # Sort processors by price (low to high)
                processors.sort(key=lambda x: parse_price(x.get('price', '')))
                
                context['processors'] = processors  # Pass sorted data
            context['url'] = url
    return render(request, 'scraper/home.html', context)
