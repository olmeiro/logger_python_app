import logging
import datetime
from pymongo.errors import ServerSelectionTimeoutError

class CosmosDBHandler(logging.Handler):
    """
    Logging handler que envía los registros a una base de datos Cosmos DB utilizando la API de MongoDB.

    Attributes:
        cosmos_client (CosmosDBClient): Instancia del cliente para interactuar con Cosmos DB.
        log_collection (pymongo.collection.Collection): Colección para almacenar los logs.
    """
    def __init__(self, cosmos_client, log_collection_name="Logs"):
        """
        Inicializa una instancia de CosmosDBHandler.

        Args:
            cosmos_client (CosmosDBClient): Instancia de la clase CosmosDBClient.
            log_collection_name (str): Nombre de la colección donde se almacenarán los logs.
        """
        # logging.Handler.__init__(self)
        super().__init__()
        self.cosmos_client = cosmos_client
        self.log_collection = self._initialize_log_collection(log_collection_name)
        self.logs = []
        self.closed = False  # Inicializa la variable closed
        self.custom_id = None  # Variable para almacenar el custom_id

    def _initialize_log_collection(self, log_collection_name):
        """
        Inicializa la colección de logs en Cosmos DB.

        Args:
            log_collection_name (str): Nombre de la colección de logs a crear o utilizar.

        Returns:
            pymongo.collection.Collection: Colección para almacenar los logs.
        """
        if log_collection_name not in self.cosmos_client.db.list_collection_names():
            self.cosmos_client.db.create_collection(log_collection_name)
        return self.cosmos_client.db[log_collection_name]

    def emit(self, record):
        """
        Envía un registro de log a la colección de Cosmos DB.

        Args:
            record (logging.LogRecord): El registro de log a almacenar.
        """
        if self.formatter:
            log_entry = self.format(record)
            timestamp = self.formatter.formatTime(record)
        else:
            log_entry = record.getMessage()
            timestamp = record.created
        
        # Acceder al campo personalizado 'iteration_name' en el record
        iteration_name = record.__dict__.get('iteration_name', 'unknown_iteration')

        # Crear un ID único que combine el nombre de la iteración y la fecha si no se ha creado antes
        if self.custom_id is None:
            iteration_time = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d_%H-%M-%S")
            self.custom_id = f"{iteration_name}_{iteration_time}"
        else:
            # Si self.custom_id ya está definido, extrae la parte del timestamp
            iteration_time = self.custom_id.split('_')[-1]
       

        log_document = {
            "_id": iteration_time,
            "level": record.levelname,
            "message": log_entry,
            "timestamp": timestamp,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread_name": record.threadName,
            "exc_info": self.format(record) if record.exc_info else None  # Usar self.format para formatear exc_info
        }

        self.logs.append(log_document)
            
    def flush(self):
        """
        Inserta todos los logs acumulados como un solo documento en la colección de Cosmos DB.
        """
        if self.logs:
            print(f"Flushing {len(self.logs)} logs to Cosmos DB")
            document = {
                "_id": self.custom_id,  # Usar el tiempo actual como ID único
                "execution_logs": self.logs
            }
            try:
                self.log_collection.insert_one(document)
            except ServerSelectionTimeoutError as e:
                print(f"Failed to log to Cosmos DB: {e}")
            finally:
                self.logs = []  # Limpiar los logs después de insertar

    def close(self):
        """
        Cierra el handler asegurándose de que todos los logs acumulados se inserten en Cosmos DB.
        """
        if self.closed:
            return  # Prevent further closing actions if already closed
        else:
            self.flush()
            self.closed = True  # Marca el handler como cerrado
            super().close()