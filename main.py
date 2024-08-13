import logging
import json
import logging.config
import logging.handlers
import pathlib
import atexit
import datetime

from cosmos_db import CosmosDBClient
from secrets_logs import SecretManager

from utils import generate_random_number

secret_manager = SecretManager()
cosmos_connection_string = secret_manager.get_secret("COSMOS-CONNECTION-STRING")


db_name = "mongodb-ofertaideal-database"
collection_names = ["Logs"]  # Colección de develop (test)

cosmos_client = CosmosDBClient(
    cosmos_connection_string, db_name, collection_names
)

def setup_logging():
    config_file = pathlib.Path("./config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)

    # Reemplaza el placeholder de 'cosmosdb' con el handler real
    config['handlers']['cosmosdb'] = {
        'class': 'cosmosdb_handler.CosmosDBHandler',
        'formatter': 'detailed',
        'cosmos_client': cosmos_client,
        'log_collection_name': 'Logs'
    }

    logging.config.dictConfig(config)

# Cierra todos los handlers correctamente al final
def close_loggers():
    # Acceder al logger subyacente
    actual_logger = logger.logger if isinstance(logger, logging.LoggerAdapter) else logger
    for handler in actual_logger.handlers:
        handler.close()

for x in range(2):

    setup_logging()

    iteration_name = f"iteration_{x}"  # Nombre de la iteración

    logger = logging.getLogger('logger_app')

    # Añadir el nombre de la iteración al logger
    logger = logging.LoggerAdapter(logger, {'iteration_name': iteration_name})

    logger.info("Starting the random number generator.")

    random_number = generate_random_number()

    logger.info(f"Generated number is {random_number}.")


    logger.debug("Just checking in!")
    logger.info("Este es un log de información.")
    logger.warning("Stay curious!")
    logger.error("Stay put!")
    logger.critical("Este es un log de error.")

    donuts = 5
    guests = 0
    try:
        donuts_per_guest = donuts / guests
    except ZeroDivisionError:
        logger.exception("DonutCalculationError")


    atexit.register(close_loggers)