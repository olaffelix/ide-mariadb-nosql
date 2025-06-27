# Lógica para gestionar conexiones y consultas a MariaDB
import pymysql

class ConnectionManager:
    def __init__(self, connections):
        self.connections = connections

    def get_databases(self, conn):
        connection = pymysql.connect(
            host=conn['host'], user=conn['user'], password=conn['password'], port=conn['port']
        )
        with connection.cursor() as cursor:
            cursor.execute('SHOW DATABASES')
            dbs = [row[0] for row in cursor.fetchall() if row[0] not in ('information_schema', 'mysql', 'performance_schema', 'sys')]
        connection.close()
        return dbs

    def get_tables(self, conn, db):
        connection = pymysql.connect(
            host=conn['host'], user=conn['user'], password=conn['password'], port=conn['port'], database=db
        )
        with connection.cursor() as cursor:
            cursor.execute('SHOW TABLES')
            tables = [row[0] for row in cursor.fetchall()]
        connection.close()
        return tables

    def get_table_data(self, conn, db, table, limit=100):
        connection = pymysql.connect(
            host=conn['host'], user=conn['user'], password=conn['password'], port=conn['port'], database=db
        )
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [row[0] for row in cursor.fetchall()]
            cursor.execute(f"SELECT * FROM `{table}` LIMIT {limit}")
            rows = cursor.fetchall()
        connection.close()
        return columns, rows

