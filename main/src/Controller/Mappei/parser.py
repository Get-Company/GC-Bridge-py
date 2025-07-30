# https://lxml.de/lxmlhtml.html
import requests
import lxml.html
from main.src.Controller.Mappei.xmlreader import XMLReader
from main.src.Entity.Mappei.MappeiProductEntity import *
from main.src.Entity.Mappei.MappeiPriceEntity import *
from main.src.Repository.functions_repository import parse_a_date


def get_html_content(url: str) -> 'lxml.html.HtmlElement':
    """
    Fetches the HTML content of a given URL and returns it as parsed lxml HtmlElement.

    Parameters:
    url (str): The URL to retrieve the HTML content from.

    Returns:
    lxml.html.HtmlElement: The HTML content of provided URL parsed into an lxml HtmlElement.
    """
    try:
        # Output the URL being accessed
        print('Get content from url: %s' % url)

        # Fetch the HTML content of the URL
        html = requests.get(url)

        # Parse HTML content using lxml
        html_content = lxml.html.fromstring(html.content)

        return html_content

    except Exception as e:
        # Log any errors or exceptions
        print(f'Error while retrieving HTML content: {e}')


def is_product(content):
    if content.find_class('product-detail'):
        print('This is a Product Page')
        return True
    else:
        print('This is not a Product Page. Skip\n')
        return False

def get_article_number(content):
    """
    This function retrieves the product's article number from the provided HTML content.

    Parameters:
    content (str): The HTML content from which to extract the product's article number.

    Returns:
    str: The product's article number as a string.
    """
    try:
        # Retrieving article number using a helper function
        number = get_itemprop(content, 'span', 'sku')
        return number
    except Exception as e:
        # Logging error details in case of any exception
        print('An error occurred while retrieving the article number: {}'.format(e))
        return None


def get_article_price(content):
    """
    This function takes the parsed HTML content and retrieves the product
    prices. If prices are listed in ranges (staffel), it retrieves highest, lowest,
    and lowest amount prices. If a single price is provided, it retrieves the price.

    :param content: a parsed HTML content
    :return: a dictionary with price details if staffel prices present; otherwise a single price
    """
    try:
        # Check if the content contains class for staffel prices
        is_staffel = get_itemprop_att(content, 'meta', 'offerCount', 'content')

        if is_staffel:
            # Retrieve price details if staffel prices present
            price_highest = get_itemprop_att(content, 'meta', 'highPrice', 'content')
            price_lowest_amount = get_itemprop_att(content, 'meta', 'offerCount', 'content')
            price_lowest = get_itemprop_att(content, 'meta', 'lowPrice', 'content')
            price = {
                "highest": price_highest,
                "lowest": price_lowest,
                "lowest_amount": price_lowest_amount
            }
        else:
            # Retrieve the price if a single price is provided
            price = get_itemprop_att(content, 'meta', 'price', 'content')

    except Exception as e:
        print(f"Error occurred while getting article price. Exception: {e}")
        return None

    return price


def get_article_name(content):
    """
    Get the name of the article from the content.

    Parameters:
    content (str): The HTML content from which to extract the article name.

    Returns:
    str: The article name as a string.
    """
    try:
        # Retrieving article name
        name = get_itemprop(content, 'title', 'name')
        return name
    except Exception as e:
        print('An error occurred while retrieving the article name: {}'.format(e))
        return None


def get_article_img(content):
    """
    Get the image URL of the article from the content.

    Parameters:
    content (str): The HTML content from which to extract the image URL.

    Returns:
    str: The image URL as a string.
    """
    try:
        # Retrieving article image URL
        img = get_itemprop_att(content, 'img', 'image', 'src')
        return img
    except Exception as e:
        print('An error occurred while retrieving the article image URL: {}'.format(e))
        return None


def get_article_description(content):
    """
    Get the description of the article from the content.

    Parameters:
    content (str): The HTML content from which to extract the article description.

    Returns:
    str: The article description as a string.
    """
    try:
        # Retrieving article description
        description = get_itemprop(content, 'div', 'description')
        return description
    except Exception as e:
        print('An error occurred while retrieving the article description: {}'.format(e))
        return None


def get_release_date(content):
    """
    Get the release date of the article from the content.

    Parameters:
    content (str): The HTML content from which to extract the article release date.

    Returns:
    datetime: The release date of the article as a datetime object.
    """
    try:
        # Retrieving raw release date string
        release_date = get_itemprop_att(content, 'meta', 'releaseDate', 'content')
        # Parsing release date
        date_obj = parse_a_date(release_date)
        return date_obj
    except Exception as e:
        print('An error occurred while retrieving the article release date: {}'.format(e))
        return None


def get_itemprop(content, tag, itemproperty, nr=0):
    """
    Get the value of a specific itemprop from the content.

    Parameters:
    content (str): The HTML content from which to extract the value of the itemprop.
    tag (str): The HTML tag where the itemprop can be found.
    itemproperty (str): The itemprop to be retrieved.
    nr (int, optional): The index of the itemprop's value if there are more than one. Defaults to 0.

    Returns:
    str: The value of the itemprop as a string.
    """
    try:
        # Retrieving element containing itemprop
        property_raw = content.xpath(f'//{tag}[@itemprop="{itemproperty}"]//text()')
        if property_raw:
            property = property_raw[nr].strip()
            return property
        else:
            return None
    except Exception as e:
        print('An error occurred while retrieving the value of the itemprop: {}'.format(e))
        return None


def get_itemprop_att(content, tag, itemproperty, attribute, nr=0):
    """
    This function parses an lxml.html object to find and return a specfic itemprop attribute.

    :param content: Parsed lxml.html object
    :param tag: HTML tag where to look for the itemprop.
    :param itemproperty: itemprop name to look for.
    :param attribute: Attribute of the itemprop to return.
    :param nr: Index of the tag to consider if multiple tags with the same itemprop exist. Default is 0.
    :return: Value of required attribute for the itemprop if exist, else return None.
    """

    try:
        # Attempt to find the itemprop in the content
        property_raw = content.xpath(f'//{tag}[@itemprop="{itemproperty}"]')

        # If the itemprop is found, get the required attribute value
        if property_raw:
            property = property_raw[nr].get(attribute)

            # Log the property found
            # print(f'Get {itemproperty} from {tag}: "{property}"')

            return property

        else:

            # Log that the itemprop wasn't found
            # print(f'No {itemproperty} found in {tag}')

            return

    except Exception as e:
        # Log any exceptions that occur
        print(f'An error occurred while fetching itemprop: {e}')


def get_products_list():
    languages = {1: 'de', 2: 'at', 3: 'ch'}
    source_int = int(input("Neu laden (1) oder vorhanden verwenden (2):\n"))
    language_int = int(input("de(1), at(2), ch(3) oder alle(4) (Standard is de):\n"))

    if language_int == 4:
        for language_id, language in languages.items():
            xmlreader = XMLReader(source_int, language_id)
            language_iso = xmlreader.get_language_iso(language_id)
            urls = xmlreader.get_urls()
            read_urls_and_save_in_db(urls, language_iso)
    else:
        xmlreader = XMLReader(source_int, language_int)
        language_iso = xmlreader.get_language_iso(language_int)
        urls = xmlreader.get_urls()
        read_urls_and_save_in_db(urls, language_iso)


def read_urls_and_save_in_db(urls, language_iso):
    """
    ```python
    This function reads given URLs, collects product related information from each URL and stores it in the database.

    Parameters:
    urls (str,list): One or more URL(s) from which the product info should be extracted.
    language_iso (str): The language in ISO format for the pages being processed.

    Returns:
    bool: Indicates whether the function executed successfully. True if successful, False otherwise.
    ```
    """
    try:
        # Ensure input 'urls' is a list
        if not isinstance(urls, list):
            urls = [urls]

        # Process each URL
        for url in urls:
            content = get_html_content(url)
            if is_product(content):  # Check if content corresponds to a product
                # Initialize product entity and populate properties
                new_product = MappeiProductEntity()
                new_product.nr = get_article_number(content)
                new_product.name = get_article_name(content)
                new_product.image = get_article_img(content)
                new_product.release_date = get_release_date(content)

                # Initialize price entity and populate properties
                new_prices = MappeiPriceEntity()
                price = get_article_price(content)

                if isinstance(price, dict):  # Check if price contains multiple price levels
                    new_prices.price_high = price['highest']
                    new_prices.price_low = price['lowest']
                    new_prices.price_quantity = price['lowest_amount']
                    new_prices.land = language_iso
                else:  # Single price level
                    new_prices.price_high = price
                    new_prices.land = language_iso

                new_product_filter = {'nr': get_article_number(content)}

                # Store new product and its price in the database
                upsert_product_and_prices(new_product, new_product_filter, new_prices)

            return True

    except Exception as e:
        # Logging
        print(f'Something went wrong during URL processing and data storage. Error details: {e}')

        return False


def upsert_product_and_prices(parent, parent_filter, child):

    # 1. Check for Update Parent
    parent_db = parent.query.filter_by(**parent_filter).first()
    if parent_db:
        print('Parent in db. Update.')
        parent.id = parent_db.id

        db.session.merge(parent)
    else:
        print('Parent NOT in db. Insert')
        parent.prices = [child]  # Needs to be in brackets, since it's a list
        db.session.add(parent)
    # 3. Commit Parent and refresh to get its id
    db.session.commit()
    print('Parent name: %s was upserted. Now Child:' % parent.name)

    # Check for Update Child - Add more filter specific
    child_db = child.query. \
        filter_by(product_id=parent.id). \
        filter_by(land=child.land). \
        first()

    print('Search Child product_id:"%s" - land:"%s"' % (parent.id, child.land))
    if child_db:
        print('Child in db. Update. Child_db product_id:"%s" - lang:"%s"' % (child_db.product_id, child_db.land))
        child.id = child_db.id
        child.product = parent
        db.session.merge(child)
    else:
        print('Child NOT in db. Adding.')
        child.product = parent
        db.session.merge(child)

    db.session.commit()

