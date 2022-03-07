import re
import os
from sqlalchemy.orm import joinedload
from main import db
import datetime


def find_all_images_by_name_with_trailing_digits():
    """
    https://regex101.com/r/sv4byS/1/
    Use the os function for iteration through the "Bilder" directory. Collect all images from the dataset
    into a json string
    :param dataset:
    :return: json string {"img1":[900000.jpg],"img2":[900000_02.jpg],...}
    """
    img_path = "D:\Bilder\Classei\Produkte\Shopware"
    name = "591002"
    pattern = "(" + name + ")([.]|[_]\d\d[.])+(jpg|jpeg|png|gif|webp)"
    regex = re.compile(pattern)
    res = []

    for root, dirs, files in os.walk(img_path):
        for file in files:
            if regex.match(file):
                res.append(file)

                print(res)
    return


def get_parent_entity_from_child(parent, child, match):
    """

    :param parent:
    :param child:
    :param match:
    :return:
    """
    child_return = db.session.query(parent). \
        join(parent.translations). \
        options(joinedload(parent.translations)). \
        filter(child.id == match). \
        filter(child.id2 == 'dk-DK'). \
        first()

    return child_return


def parse_a_date(date_string="01.01.90", input_format="%d.%m.%y"):
    """
    Input any string and match the input_format to the string. Now set the output Format as you wish
    :param date_string: string The date string.
    :param input_format: string The format of the date string
    :return: obj datetime Object
    """
    datetime_obj = datetime.datetime.strptime(date_string, input_format)
    return datetime_obj


def parse_european_number_to_float(number):
    """
    Nicely all commas are removed. The thousand sepparator stays
    https://regex101.com/  with the pattern: (?<=\d),(?=\d)
    :param number:string German number with or without currency: 1.2365,35
    :return:
    """
    if not number or number == '':
        return
    else:
        decmark_reg = re.compile('(?<=\d),(?=\d)')
        number_float_english = decmark_reg.sub('.', number)
        return number_float_english


def iterate_list(example_list=None):
    """
    This iterates over a multiple (2 levels) dict
    :param example_list: dict
    :return: None
    """
    example_list = {
        1: {"007510": "845125"},
        2: {"091300": "401000"},
        3: {"104014": "304488"},
        4: {"104016": "304154"},
        5: {"104051": "304163"},
        6: {"104070": "304784"},
        7: {"104170": "324484"},
        8: {"104522": "314165"},
        9: {"144050": "194750"},
        10: {"144150": "354373"}
    }
    for p_id, p_info in example_list.items():
        print("\nID:", p_id)
    for key in p_info:
        print(key + ': ' + p_info[key])


def parse_english_number_to_european(number):
    """
    Nicely all dots are removed. The thousand sepparator stays
    https://regex101.com/  with the pattern: (?<=\d),(?=\d)
    :param number:string German number with or without currency: 1.2365,35
    :return: float
    """
    if not number or number == '':
        return
    else:
        decmark_reg = re.compile('(?<=\d)\.(?=\d)')
        number_float_eu = decmark_reg.sub('.', number)
        return number_float_eu


def write_log(text):
    timestamp = datetime.datetime.now()
    filename_date = timestamp.strftime("%y-%m-%d")

    base_dir = os.path.dirname(os.path.abspath(__name__))
    filename = "logfiles/" + filename_date+'.txt'
    file = os.path.join(base_dir, filename)
    with open(file, 'a', encoding="utf-8") as f:
        f.write(timestamp.strftime("%H:%M:%S - ")+text+'\n')
