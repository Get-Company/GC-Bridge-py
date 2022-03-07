import re
from lxml import etree
import datetime
import os
from config import MappeiConfig, BASE_DIR
import requests
import gzip
import shutil


class XMLReader:
    def __init__(self, source_int, language_int):
        # Get the path to the local xml
        self.path_to_xml_folder_os = os.path.abspath(os.path.dirname(__file__)) + '/xml/'

        # Get Sorce Site or File
        self.source = self.get_source(source_int)

        # Get Language
        self.language = self.get_language_iso(language_int)

        # Get language sitemap Path
        self.sitemap_language_filename = getattr(MappeiConfig, 'mappei_' + self.language + '_sitemap')

        # Get Product Sitemap path and filename
        self.sitemap_product_filename = 'product-' + self.language + '-sitemap.xml'

    def get_urls(self):
        if self.source == 'site':
            urls = self.get_products_sitemap_from_site()
        elif self.source == 'file':
            urls = self.get_products_sitemap_from_file()
        else:
            urls = self.get_products_sitemap_from_site()

        return urls

    def get_products_sitemap_from_site(self):
        """
        Reads the sitemap and gets all the urls from the category sitemap
        Saves the sitemap into the xml folder
        :return: list of urls
        """
        print('Seite: %s wird aufgerufen.' % self.sitemap_language_filename)
        root = self.get_file_from_site_gz(self.sitemap_language_filename)

        sitemap_link = root.getchildren()
        # If there are more than 1 sitemaps linked
        if len(sitemap_link) > 1:
            nr = self.ask_wich_sitemap(sitemap_link)
            children = sitemap_link[nr].getchildren()
        else:
            children = sitemap_link[0].getchildren()

        path_product_sitemap = children[0].text
        date_product_sitemap = self.parse_date(children[1].text)

        print('\nAlles klar, die Sitemap wurde zuletzt am %s um %s geändert.' %
              (date_product_sitemap.strftime("%d.%m.%Y"), date_product_sitemap.strftime("%H:%M")))

        # We are in the sitemap
        url_set = self.get_file_from_site_gz(path_product_sitemap)
        urls = url_set.getchildren()

        return urls

    def get_file_from_site_gz(self, path_product_sitemap):
        # Check if gzip
        pattern = ".(gz|xml.gz)"
        m = re.search(pattern, path_product_sitemap)
        if m:
            print("Datei ist gezipped. Unzipping...")
            file = m.group(0)
            filename_gz = self.download_file(path_product_sitemap)
            filename = self.decompress_file(filename_gz)
            print("Datei lokal in xml/ gespeichert.")

            root = self.get_file_root(self.path_to_xml_folder_os + self.sitemap_product_filename)
        else:
            r = requests.get(self.sitemap_language_filename)
            root = etree.fromstring(r.content)

        return root

    def get_products_sitemap_from_file(self):
        """
        Read the sitemap from the file, if the sitemaps was previously downloaded
        :return:
        """
        print("Datei xml/-" + self.sitemap_product_filename + " wird aufgerufen.")
        try:
            with open(self.path_to_xml_folder_os + self.sitemap_product_filename) as f:
                tree = etree.parse(self.path_to_xml_folder_os + self.sitemap_product_filename)
                urlset = tree.getroot()
                urls = urlset.getchildren()
                return urls
        except IOError:
            print("Die Datei %s existiert ned. Ich hol Sie von Mappei." % self.sitemap_product_filename)
            urls = self.get_products_sitemap_from_site()
            return urls

    def get_file_root(self, path_file):
        file = etree.parse(path_file)
        root = file.getroot()
        return root

    def download_file(self, url):
        file = url
        print('Url: %s wird aufgerufen.' % url)
        filename = file.split("/")[-1]
        with open(self.path_to_xml_folder_os + filename, "wb") as f:
            r = requests.get(file)
            f.write(r.content)

        print('Datei "%s" von "%s" heruntergeladen und in "xml/" gespeichert.' % (filename, url))
        return filename

    def decompress_file(self, filename):
        print('Datei "%s wird geöffnet und in xml/ decompressed' % filename)
        with gzip.open(self.path_to_xml_folder_os + filename, 'rb') as f_in:
            with open(self.path_to_xml_folder_os + self.sitemap_product_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return True

    def ask_wich_sitemap(self, sitemap):
        """
        Simply ask for the index of the sitemap, wich you want to read.
        :param sitemap: list All Sitemap Elements of the XML
        :return: int Return the Number of
        """
        print("Es gibt %s Sitemap(s) auf %s" % (len(sitemap), self.sitemap_language_filename))
        nr = input("Welche willst du?:\n")
        if not isinstance(nr, int) or int(nr) > len(sitemap) or not nr:
            print('Sorry, aber deine Nummer: "%s" gibt es nicht. Ich geb dir einfach die 1. Sitemap' % nr)
            return 0
        return nr - 1

    def get_language_iso(self, language_int):
        switcher = {
            1: 'de',
            2: 'at',
            3: 'ch'
        }
        return switcher.get(language_int, 'de')

    def get_source(self, source_int):
        switcher = {
            1: 'site',
            2: 'file'
        }
        return switcher.get(source_int, 'site')

    def parse_date(self, date_string):
        date_parsed = datetime.datetime.fromisoformat(date_string)
        return date_parsed
