import  logging


logger = logging.getLogger('XiaoQiang')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

fh = logging.FileHandler('access.log')
fh.setLevel(logging.CRITICAL)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')