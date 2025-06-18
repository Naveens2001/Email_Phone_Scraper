import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

visited_urls = set()

def get_website_content(url):
    """Fetch and return the content of a website."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

def find_emails_and_phones(content):
    """Find and return emails and phone numbers in the content."""
    emails = re.findall(r'[\w\.\-]+@[\w\.-]+\.\w+', content)

    phone_pattern = r'''
        (?:(?:\+91[\-\s]?|0)?                # Optional country code or leading 0
        (?:\d{3,5}[\-\s]?\d{3,5}[\-\s]?\d{0,5}))  # Number parts with optional separators
    '''

    raw_phones = re.findall(phone_pattern, content, re.VERBOSE)

    phones = []
    for num in raw_phones:
        digits = re.sub(r'\D', '', num)
        if 10 <= len(digits) <= 12:
            phones.append(num.strip())

    return set(emails), set(phones)

def crawl_website(url, base_domain):
    """Recursively crawl pages and extract emails and phone numbers."""
    if url in visited_urls:
        return set(), set()

    visited_urls.add(url)
    content = get_website_content(url)
    if not content:
        return set(), set()

    soup = BeautifulSoup(content, 'html.parser')
    emails, phones = find_emails_and_phones(content)

    # Find internal links
    links = soup.find_all('a', href=True)
    for link in links:
        full_url = urljoin(url, link['href'])
        if base_domain in full_url and full_url not in visited_urls:
            sub_emails, sub_phones = crawl_website(full_url, base_domain)
            emails.update(sub_emails)
            phones.update(sub_phones)

    return emails, phones

if __name__ == "__main__":
    start_url = input("Enter the URL: ").strip()
    domain = urlparse(start_url).netloc

    print("Crawling website. Please wait...\n")
    emails, phones = crawl_website(start_url, domain)

    print(f"\nEmails found ({len(emails)}):")
    for email in sorted(emails):
        print(f" - {email}")

    print(f"\nPhone numbers found ({len(phones)}):")
    for phone in sorted(phones):
        print(f" - {phone}")
