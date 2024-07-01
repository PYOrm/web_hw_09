import json

import requests
from bs4 import BeautifulSoup


class Parser:
    base_url = "https://quotes.toscrape.com"
    authors_set = set()
    authors = []
    quotes = []

    def parse(self, url=base_url):
        next_url, authors_url, quotes = self.parse_quotes(url)
        if quotes:
            self.quotes.extend(quotes)
        for author_url in authors_url:
            author_name = str(author_url).split("/")[2]
            if author_name not in self.authors_set:
                self.authors.append(self.parse_author(self.base_url + author_url))
                self.authors_set.add(author_name)
        if next_url:
            self.parse(self.base_url + next_url)

    def save_data(self):
        self.save_quotes()
        self.save_authors()

    def parse_quotes(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            quotes = soup.find_all('div', class_='quote')
            authors_url = []
            res_quotes = []
            for qt in quotes:
                quote = qt.find_all('span', class_='text')[0].text
                author = qt.find_all('small', class_='author')[0].text
                tags = [tg.text for tg in qt.find_all('a', class_='tag')]
                author_url = qt.find('small', class_='author').parent.find('a')["href"]
                quote = {
                    "quote": quote,
                    "author": author,
                    "tags": tags
                }
                res_quotes.append(quote)
                authors_url.append(author_url)
            try:
                next_page = soup.find('li', class_='next').find('a')["href"]
            except AttributeError:
                next_page = None
            return next_page, authors_url, res_quotes

    def parse_author(self, url) -> dict:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            author_name = soup.find('h3', class_='author-title').text
            author_birthday = soup.find('span', class_='author-born-date').text
            author_birth_location = soup.find('span', class_='author-born-location').text
            author_description = soup.find('div', class_='author-description').text

            author = {
                "fullname": author_name,
                "born_date": author_birthday,
                "born_location": author_birth_location,
                "description": author_description
            }
            return author

    def save_authors(self):
        with open("authors.json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(self.authors))

    def save_quotes(self):
        with open("quotes.json", "w+", encoding="utf-8")as f:
            f.write(json.dumps(self.quotes))


def main():
    parser = Parser()
    parser.parse()
    parser.save_data()


if __name__ == "__main__":
    main()
