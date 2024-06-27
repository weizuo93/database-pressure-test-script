from datetime import datetime
import logging


def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler('log/db-concurrent-query.' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log')
    fh.setLevel(logging.INFO)

    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)

    logger.addHandler(fh)
    # logger.addHandler(ch)

    return logger


LOG = setup_logging()
