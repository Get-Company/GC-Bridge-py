from main.src.SW6_Bridge.process import MainProcess
import logging
from logging.config import dictConfig
from main.src.SW6_Bridge.config.config import config

if __name__ == '__main__':
    logger = logging.getLogger()
    #dictConfig(config['logging'])
    #logger.info("---------------------------------")
    #logger.info("Project started")
    process = MainProcess(config)
    process.sync_to_sw()
    #logger.info("Project finished")
