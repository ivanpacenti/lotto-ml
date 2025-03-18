import pyodbc

# Configura la connessione al database
DB_SERVER = "localhost"
DB_DATABASE = "lotto"
DB_USER = "SA"
DB_PASSWORD = "YourPassword123"

def get_db_connection():
    """Crea e restituisce una connessione al database SQL Server."""
    conn_str = f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USER};PWD={DB_PASSWORD}"
    conn = pyodbc.connect(conn_str)
    return conn
