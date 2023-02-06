import os
import json
import sys
from main.src.SW6_Bridge.log_exception import logException

def importConfig(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        try:
            config = json.load(f, strict=False)
            return config
        except Exception as e:
            etype, evalue, tb = sys.exc_info()
            logException(etype, evalue, tb)
            return None

config = importConfig(f"{os.path.dirname(os.path.realpath(__file__))}/config.json")