import logging

logger = logging.getLogger(__name__)

def logException(etype, evalue, tb):
    logger.error('Exception type: {0}'.format(etype))
    logger.error('Exception value: {0}'.format(evalue))
    logger.error('Exception at: {0}:{1}'.format(tb.tb_frame.f_code.co_filename, tb.tb_lineno))
