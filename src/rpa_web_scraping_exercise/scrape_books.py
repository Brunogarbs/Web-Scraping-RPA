import re
from decimal import Decimal
from typing import TypedDict
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page

URL = "https://books.toscrape.com/"

RATING_WORDS: dict[str, int] = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BookData(TypedDict):
    url: str
    name: str
    rating: int
    price: Decimal
    in_stock: bool


def scrape_books(page: Page, category: str | None, max_books: int) -> list[BookData]:
    """ Coleta livros """
    if max_books <= 0:
        return []

    page.goto(URL)

    if category is not None:
        category_url = _find_category_url(page, category)
        if category_url is None:
            return []
        page.goto(category_url)

    books: list[BookData] = []
    while True:
        for article in page.locator("article.product_pod").all():
            books.append(_parse_book(article, page.url))
            if len(books) >= max_books:
                return books

        next_url = _next_page_url(page)
        if next_url is None:
            return books
        page.goto(next_url)


def _find_category_url(page: Page, category: str) -> str | None:
    """ Procura a categoria """
    wanted = category.casefold()
    for link in page.locator(".side_categories ul li ul li a").all():
        if link.inner_text().strip().casefold() == wanted:
            return urljoin(page.url, _required_attribute(link, "href"))
    return None


def _parse_book(article: Locator, page_url: str) -> BookData:
    """ Extrai os dados de um livro """
    link = article.locator("h3 a")
    return BookData(
        url=urljoin(page_url, _required_attribute(link, "href")),
        name=_required_attribute(link, "title"),
        rating=_parse_rating(_required_attribute(article.locator("p.star-rating"), "class")),
        price=_parse_price(article.locator("p.price_color").inner_text()),
        in_stock="in stock" in article.locator("p.availability").inner_text().casefold(),
    )


def _parse_rating(class_attribute: str) -> int:
    """ Converte a classe de avaliação em número inteiro """
    for word in class_attribute.split():
        if word in RATING_WORDS:
            return RATING_WORDS[word]
    raise ValueError(f"Unknown rating: {class_attribute!r}")


def _parse_price(text: str) -> Decimal:
    """ Converte o preço exibido em Decimal, removendo símbolos de moeda """
    return Decimal(re.sub(r"[^\d.]", "", text))


def _next_page_url(page: Page) -> str | None:
    """ Retorna a URL absoluta """
    next_link = page.locator("li.next a")
    if next_link.count() == 0:
        return None
    return urljoin(page.url, _required_attribute(next_link, "href"))


def _required_attribute(locator: Locator, name: str) -> str:
    """ Lê um atributo obrigatório do elemento """
    value = locator.get_attribute(name)
    if value is None:
        raise ValueError(f"Missing attribute {name!r}")
    return value