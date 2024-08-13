import pymongo

from pymongo.errors import ServerSelectionTimeoutError


class CosmosDBClient:
    """
    Cliente para interactuar con una base de datos Cosmos DB utilizando MongoDB API.

    Esta clase proporciona métodos para conectarse a Cosmos DB, crear y manejar colecciones,
    y realizar operaciones CRUD básicas sobre la información de los clientes.

    Attributes:
        connection_string (str): Cadena de conexión para Cosmos DB.
        db_name (str): Nombre de la base de datos.
        collection_names (list): Lista de nombres de colecciones a crear.
        client (pymongo.MongoClient): Cliente MongoDB para la conexión.
        db (pymongo.database.Database): Objeto de base de datos.
        client_info_collection (pymongo.collection.Collection): Colección para información de clientes.
    """
    def __init__(self, connection_string, db_name, collection_names):
        """
        Inicializa una instancia de CosmosDBClient.

        Args:
            connection_string (str): Cadena de conexión para Cosmos DB.
            db_name (str): Nombre de la base de datos a utilizar.
            collection_names (list): Lista de nombres de colecciones a crear.

        Raises:
            TimeoutError: Si la conexión a la base de datos falla.
        """
        self.connection_string = connection_string
        self.db_name = db_name
        self.collection_names = collection_names
        self.client = self._initialize_client()
        self.db = self._create_database_and_collections()
        self.client_info_collection = self.db["Clients"]

    def _initialize_client(self):
        """ Inicializa y verifica la conexión con el cliente MongoDB.

        Returns:
            pymongo.MongoClient: Cliente MongoDB inicializado.

        Raises:
            TimeoutError: Si la conexión falla o el tiempo de espera se agota."""
        try:
            client = pymongo.MongoClient(self.connection_string)
            client.server_info()
            return client
        except ServerSelectionTimeoutError:
            raise TimeoutError(
                "Invalid API for MongoDB connection string or timed out when attempting to connect"
            )

    def _create_database_and_collections(self):
        """
        Crea la base de datos y las colecciones especificadas si no existen.

        Returns:
            pymongo.database.Database: Objeto de base de datos inicializado.
        """
        db = self.client[self.db_name]
        for collection_name in self.collection_names:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
        return db

    def insert_client_info(self, client_info):
        
        """
        Inserta información de un cliente en la colección 'Clients'.

        Args:
            client_info (dict): Diccionario con la información del cliente a insertar.
                Debe contener una clave '_id' como identificador único del cliente.

        Prints:
            Mensaje de confirmación con el ID del cliente insertado.
        """
        collection = self.db["Clients"]
        collection.insert_one(client_info)
        print(f"Inserted client info for client {client_info['_id']}")

    def upsert_client_info(self, client_info):
        """
        Inserta o actualiza la información de un cliente en la colección.

        Si existe un documento con el mismo '_id', se actualiza; de lo contrario, se inserta uno nuevo.

        Args:
            client_info (dict): Diccionario con la información del cliente a insertar o actualizar.
                Debe contener una clave '_id' como identificador único del cliente.

        Prints:
            Mensaje de confirmación con el ID del cliente actualizado o insertado.
        """
        self.client_info_collection.update_one(
            {"_id": client_info["_id"]}, {"$set": client_info}, upsert=True
        )
        print("Upserted client info for client {}".format(client_info["_id"]))

    def get_client_info(self, client_id):
        """
        Obtiene la información de un cliente específico de la colección.

        Args:
            client_id: Identificador único del cliente a buscar.

        Returns:
            dict or None: Diccionario con la información del cliente si se encuentra,
                          None si no se encuentra ningún cliente con el ID especificado.
        """
        return self.client_info_collection.find_one({"_id": client_id})
