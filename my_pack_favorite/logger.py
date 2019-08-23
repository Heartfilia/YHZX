# There is no need to import the log module
# LOG objects are common
import os, time, sys
import logging
from logging import getLogger


# Here are the packaged packages, you need to rewrite something.
# LEVEL:: CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
LOG = getLogger()
LOG.setLevel(logging.DEBUG)  # Change the level of logging::

# You can modify the following code to change the location::
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = BASE_DIR + f'/{time.asctime()[-4:]}.log'

formatter = logging.Formatter(
        "%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s"
	)  # Define the log output format

# file log
fh = logging.FileHandler(filename=filename, encoding="utf-8")
fh.setFormatter(formatter)

# Console log
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter

# Add a log handler to the LOG
LOG.addHandler(fh)
LOG.addHandler(console_handler)

# Setting the log level::
LOG.setLevel(logging.INFO)

# you can use LOG.info('Anything you want to input here')
