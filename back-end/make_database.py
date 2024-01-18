import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

params = {
    "database": "postgres",
    "user": "postgres",
    "password": "12345678",
    "host": "localhost",
    "port": 5432,
}

# conn = psycopg2.connect(**params)
# conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
# cursor = conn.cursor()

dbname = 'postgres'
user = 'postgres'
password = '12345678'
host = 'localhost'
port = '5432'
connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cursor = connection.cursor()

# # cursor.execute("CREATE DATABASE geospatial;")
# cursor.execute("CONNECT TO geospatial;")
# cursor.execute("\c geospatial_db")
cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

# commands = (
#     """
    # CREATE TABLE common_metadata (
    # file_id SERIAL,
    # file_name VARCHAR(255) NOT NULL,
    # file_location VARCHAR(255) PRIMARY KEY,
    # file_type VARCHAR(50) NOT NULL,
    # file_size INT,
    # creation_date TIMESTAMP,
    # last_accessed TIMESTAMP,
# );
#     """,
#     """
    # CREATE TABLE geojson_metadata (
    # file_location VARCHAR(255) PRIMARY KEY REFERENCES common_metadata(file_path),
    # ids TEXT,
    # data_names TEXT,
    # data_types TEXT,
    # geometries TEXT,
    # area TEXT,
    # length TEXT,
    # bounding_box TEXT,
    # h3_index TEXT
    # );
#     """,
#     """
    # CREATE TABLE tiff_metadata (
    # file_path VARCHAR(255) PRIMARY KEY REFERENCES common_metadata(file_path),
    # projection TEXT,
    # geotransform TEXT,
    # centerx TEXT,
    # centery TEXT,
    # bounding_box TEXT,
    # caption_conditional TEXT,
    # caption_unconditional TEXT
    # );
#     """,
#     """
    # CREATE TABLE las_metadata (
    # file_path VARCHAR(255) PRIMARY KEY REFERENCES common_metadata(file_path),
    # point_format TEXT,
    # number_of_points TEXT,
    # scale_factors TEXT,
    # offsets TEXT,
    # min_bounds TEXT,
    # max_bounds TEXT,
    # bounding_box TEXT,
    # h3_index TEXT
    # );
#     """
# )

commands = (
    
    """
    CREATE TABLE geojson_metadata (
        file_location VARCHAR(255) PRIMARY KEY REFERENCES common_metadata(file_location),
        ids TEXT,
        data_names TEXT,
        data_types TEXT,
        geometries TEXT,
        area TEXT,
        length TEXT,
        bounding_box TEXT,
        h3_index TEXT
    )
    """,
    """
    CREATE TABLE tiff_metadata (
        file_location VARCHAR(255) PRIMARY KEY REFERENCES common_metadata(file_location),
        projection TEXT,
        geotransform DOUBLE PRECISION[],
        centerx DOUBLE PRECISION,
        centery DOUBLE PRECISION,
        bounding_box GEOMETRY,
        caption_conditional TEXT,
        caption_unconditional TEXT
    )
    """,
    """
    CREATE TABLE las_metadata (
        file_location VARCHAR(255) PRIMARY KEY REFERENCES common_metadata(file_location),
        point_format INT,
        number_of_points BIGINT,
        scale_factors DOUBLE PRECISION[],
        offsets DOUBLE PRECISION[],
        min_bounds GEOMETRY,
        max_bounds GEOMETRY,
        bounding_box GEOMETRY,
        h3_index TEXT
    )
    """   )

for command in commands:
    cursor.execute(command)

cursor.close()
connection.close()
