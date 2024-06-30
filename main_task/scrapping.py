import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com"


def parse_page(url):
    html_doc = requests.get(url)
    soup = BeautifulSoup(html_doc.text, "html.parser")

    quotes = []
    authors = {}

    for quote in soup.find_all("div", class_="quote"):
        quote_text = quote.find("span", class_="text").get_text().strip()
        author_name = quote.find("small", class_="author").get_text().strip()
        tags = [tag.get_text().strip() for tag in quote.find_all("a", class_="tag")]

        quotes.append({"quote": quote_text, "author": author_name, "tags": tags})

        if author_name not in authors:
            author_url = BASE_URL + quote.find("a")["href"]
            author_html_doc = requests.get(author_url)
            author_soup = BeautifulSoup(author_html_doc.text, "html.parser")

            author_fullname = (
                author_soup.find("h3", class_="author-title").get_text().strip()
            )
            author_born_date = (
                author_soup.find("span", class_="author-born-date").get_text().strip()
            )
            author_born_location = (
                author_soup.find("span", class_="author-born-location")
                .get_text()
                .strip()
            )
            author_description = (
                author_soup.find("div", class_="author-description").get_text().strip()
            )

            authors[author_fullname] = {
                "fullname": author_fullname,
                "born_date": author_born_date,
                "born_location": author_born_location,
                "description": author_description,
            }

    return quotes, authors


def scrape_quotes():
    all_quotes = []
    all_authors = {}
    page_url = "/"

    while page_url:
        quotes, authors = parse_page(BASE_URL + page_url)

        all_quotes.extend(quotes)
        all_authors.update(authors)

        html_doc = requests.get(BASE_URL + page_url)
        soup = BeautifulSoup(html_doc.text, "html.parser")

        next_btn = soup.find("li", class_="next")
        page_url = next_btn.find("a")["href"] if next_btn else None

    return all_quotes, all_authors


if __name__ == "__main__":
    quotes, authors_dict = scrape_quotes()
    authors = list(authors_dict.values())

    with open("quotes.json", "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=4)

    with open("authors.json", "w", encoding="utf-8") as f:
        json.dump(authors, f, ensure_ascii=False, indent=4)
