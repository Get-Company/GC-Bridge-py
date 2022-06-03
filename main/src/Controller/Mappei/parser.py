# https://lxml.de/lxmlhtml.html
import requests
import lxml.html
from main.src.Controller.Mappei.xmlreader import XMLReader
from main.src.Entity.Mappei.MappeiProductEntity import *
from main.src.Entity.Mappei.MappeiPriceEntity import *
from main.src.Repository.functions_repository import parse_a_date


def get_html_content(url):
    print('Get content from url: %s' % url)
    html = requests.get(url)
    html_content = lxml.html.fromstring(html.content)
    return html_content


def is_product(content):
    if content.find_class('product-detail'):
        print('This is a Product Page')
        return True
    else:
        print('This is not a Product Page. Skip\n')
        return False


def get_article_price(content):
    is_staffel = content.find_class('product-block-prices')
    if is_staffel:
        price_highest = get_itemprop_att(content, 'meta', 'highPrice', 'content')
        price_lowest_amount = get_itemprop_att(content, 'meta', 'offerCount', 'content')
        price_lowest = get_itemprop_att(content, 'meta', 'lowPrice', 'content')
        price = {
            "highest": price_highest,
            "lowest": price_lowest,
            "lowest_amount": price_lowest_amount
        }
    else:
        price = get_itemprop_att(content, 'meta', 'price', 'content')

    return price


def get_article_number(content):
    number = get_itemprop(content, 'span', 'sku')
    return number


def get_article_name(content):
    name = get_itemprop(content, 'title', 'name')
    return name


def get_article_img(content):
    img = get_itemprop_att(content, 'img', 'image', 'src')
    return img


def get_article_description(content):
    description = get_itemprop(content, 'div', 'description')
    return description


def get_release_date(content):
    release_date = get_itemprop_att(content, 'meta', 'releaseDate', 'content')
    # Example string 01.01.90
    date_obj = parse_a_date(release_date)
    return date_obj


def get_itemprop(content, tag, itemproperty, nr=0):
    property_raw = content.xpath(f'//{tag}[@itemprop="{itemproperty}"]//text()')
    if property_raw:
        property = property_raw[nr].strip()
        print('Get %s from %s: "%s"' % (itemproperty, tag, property))
        return property
    else:
        return


def get_itemprop_att(content, tag, itemproperty, attribute, nr=0):
    property_raw = content.xpath(f'//{tag}[@itemprop="{itemproperty}"]')
    if property_raw:
        property = property_raw[nr].get(attribute)
        print('Get %s from %s: "%s"' % (itemproperty, tag, property))
        return property
    else:
        return


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
    for url in urls:
        content = get_html_content(url[0].text)
        product = is_product(content)
        if product:

            # Set the product
            new_product = MappeiProductEntity()
            new_product.nr = get_article_number(content)
            new_product.name = get_article_name(content)
            new_product.image = get_article_img(content)
            new_product.release_date = get_release_date(content)

            # Set the prices
            new_prices = MappeiPriceEntity()
            price = get_article_price(content)
            # If Staffelprices
            if isinstance(price, dict):
                new_prices.price_high = price['highest']
                new_prices.price_low = price['lowest']
                new_prices.price_quantity = price['lowest_amount']
                new_prices.land = language_iso
            # If not Staffelprices
            else:
                new_prices.price_high = price
                new_prices.land = language_iso

            new_product_filter = {'nr': get_article_number(content)}
            upsert_product_and_prices(new_product, new_product_filter, new_prices)

    return True


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
