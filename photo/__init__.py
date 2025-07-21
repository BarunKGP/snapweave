import logging

LOGLEVEL = logging.DEBUG
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s: [%(levelname)s] - %(asctime)s: %(message)s")

logger = logging.getLogger("photo")
logger.setLevel(LOGLEVEL)
ch.setLevel(LOGLEVEL)
ch.setFormatter(formatter)

logger.addHandler(ch)
