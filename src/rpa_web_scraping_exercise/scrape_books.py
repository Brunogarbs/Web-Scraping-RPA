from decimal import Decimal
from typing import TypedDict

from playwright.sync_api import Page

URL: str = "https://books.toscrape.com/"


class BookData(TypedDict):
    url: str
    name: str
    rating: int
    price: Decimal
    in_stock: bool


def scrape_books(page: Page, *, category: str | None, max_books: int) -> list[BookData]:
    """Scrape book data from https://books.toscrape.com/.

    After navigating to the site homepage, scrapes book data following this
    contract:

    - `category` is `None`: scrape all books, following the pagination from
      the homepage without navigating into any category.
    - `category` matches a sidebar category (case-insensitive): scrape only
      that category's books, following its pagination.
    - `category` does not match any sidebar category (or is empty /
      whitespace-only): return an empty list.

    Stops as soon as `max_books` books have been collected and never request
    pages beyond the limit. If `max_books` is less than or equal to zero, an
    empty list is returned.

    Args:
        page: A Playwright page, already created and navigable.
        category: The category to scrape, or `None` to scrape all books.
        max_books: Maximum number of books to scrape.

    Returns:
        A list of the scraped books.
    """
    page.goto(URL)
    raise NotImplementedError

