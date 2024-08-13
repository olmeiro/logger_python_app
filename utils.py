import logging
import random

def generate_random_number():
    logger = logging.getLogger('logger_app.utils')

    random_number = random.randint(1, 100)
    logger.debug(f"Generated random number: {random_number}")

    if random_number < 30:
        logger.info(f"Random number is less than 30: {random_number}")
    elif 30 <= random_number < 70:
        logger.warning(f"Random number is between 30 and 70: {random_number}")
    else:
        logger.error(f"Random number is greater than or equal to 70: {random_number}")

    return random_number
