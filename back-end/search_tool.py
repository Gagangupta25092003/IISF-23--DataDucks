import psycopg2
import nltk
from sqlalchemy import create_engine, text
# from sqlalchemy.sql.expression import concat
nltk.download("stopwords")
nltk.download("punkt")
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import ast
import requests
from file_parser import file_gis_extensions

# defining waits for relevance sorting

weights = {"file_name": 5, "file_type": 1, "file_size": 0.5, "creation_date": 1.5}
database_uri='postgresql://postgres:12345678@localhost/postgres'
engine = create_engine(database_uri)




#to find if a location is inside our catalogue or not###########################################

# Parse bounding box coordinates from string
def parse_bounding_box(bounding_box_str):
    """
    Parses the bounding box coordinates from a string.
    """
    return ast.literal_eval(bounding_box_str.replace('(', '[').replace(')', ']'))

# Check if location is inside bounding box
def check_location(coordinates, bounding_box_str):
    longitude, latitude = coordinates
    try:
       # Extract coordinates from string, ensuring correct format
        bounding_box = parse_bounding_box(bounding_box_str)
        x1, y1, x2, y2 = bounding_box
        # Check if the location point is within the bounding box
        return x1[0] <= longitude <= x2[0] and y1[1] <= latitude <= y2[1]
       
    except ValueError:  # Handle potential errors in bounding box format
       print("Invalid bounding box format present")

def get_location_coordinates(location):
    """
    Get the coordinates of a given location using the OpenStreetMap Nominatim API.

    :param location: The location to search for in the format "address, city, country".
    :return: A tuple of (latitude, longitude) or None if the request fails.
    """
    geocode_url = f'https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1'
    try:
        geocode_response = requests.get(geocode_url)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()
        if geocode_data:
            lat = geocode_data[0]['lat']
            lon = geocode_data[0]['lon']
            return [float(lat), float(lon)]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')
        return None

    return None

# Fetch rows from common_metadata and check location
def find_coordinates_in_db(coordinates):
    try:
        # cursor = connection.cursor()

        # Fetch rows from common_metadata
        # cursor.execute("SELECT * FROM common_metadata")
        with engine.connect() as connection_:
            common_metadata_rows = connection_.execute(text("SELECT * FROM common_metadata"))
            common_metadata_rows = common_metadata_rows.fetchall()
        output = []
        # Iterate through rows
        for row in common_metadata_rows:
            file_type = row[4]

            # Determine the appropriate table based on file_type
            if file_type in file_gis_extensions["vector"]:
                table_name = "geojson_metadata"
            elif file_type in file_gis_extensions["raster"] or file_type in file_gis_extensions["compressed_raster"] or file_type in file_gis_extensions["multitemporal"]:
                table_name = "tiff_metadata"
            elif file_type in file_gis_extensions["lidar"]:
                table_name = "las_metadata"
            else:
                # No bounding box data for this file_type
                continue

            # Fetch bounding box data from the determined table
            with engine.connect() as connection_:
                bounding_boxes = connection_.execute(f"SELECT bounding_box FROM {table_name} WHERE file_path = %s", (row[3],))
                bounding_box = bounding_box.fetchall()
                
            # bounding_boxes = cursor.fetchall()
            for bounding_box in bounding_boxes:
                bounding_box_str = bounding_box[0]
                if bounding_box_str != None :
                    # Split the string into individual bounding boxes
                    individual_boxes = bounding_box_str.split(';')
                    for individual_box_str in individual_boxes:
                        # Process each individual bounding box
                        if check_location(coordinates, individual_box_str):
                            print(f"Location is within the bounding box of file_id {row[0]}")
                            output.append(row)
                            break  # Exit the loop if found
                else:
                    return None
        if output != []:
            return output
        else:
            print('The given location was not found in any of the files.')
        

    except Exception as e:
        print(f"Error: {e}")

    # finally:
    #     if cursor:
    #         cursor.close()

def check_loc(location=None,coordinates=None):
    '''
    Parameters provide by user as query from frontend
    ----------
    location :  either string or None
        DESCRIPTION. The default is None.
    coordinates : either tuple containing two float values or None
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''
    try:
        if location:
            # find coordinates of given location
            location_coordinates = get_location_coordinates(location)
            print(f"Coordinates of {location}: {location_coordinates}")
            find_coordinates_in_db(location_coordinates)
        elif coordinates:
            find_coordinates_in_db(coordinates)
        else:
            print('location aur coordinates dono he niye diye h...')
    
    except Exception as e:
        print(f"Error: {e}")


#############################################################################################

def process_natural_language_query(query):
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(query.lower())
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    return keywords


def execute_sql_query(query):
    try:
        # cursor = .cursor()
        with engine.connect() as connection_:
            result= connection_.execute(query)
            result= result.fetchall()
            # cursor.execute(query)
        # result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error: Unable to execute SQL query. {e}")
        return None
    # finally:
    #     if cursor:
    #         cursor.close()


def calculate_score_expression(weights, keywords):
    expressions = []
    for keyword in keywords:
        keyword_expressions = []
        for key, weight in weights.items():
            if key in ["file_name", "file_type"]:
                keyword_expressions.append(
                    f"{weight} * (CASE WHEN LOWER({key}) LIKE '%{keyword}%' THEN 1 ELSE 0 END)"
                )
            else:
                keyword_expressions.append(
                    f"{weight} * (CASE WHEN CAST({key} AS TEXT) LIKE '%{keyword}%' THEN 1 ELSE 0 END)"
                )
        expressions.append(f"({' + '.join(keyword_expressions)})")
    return f"{' + '.join(expressions)}"

def all():
    with engine.connect() as connection_:
            common_metadata_rows = connection_.execute(text("SELECT * FROM common_metadata"))
            common_metadata_rows = common_metadata_rows.fetchall()
            
    return common_metadata_rows
    
def search_files(query=None, location1 = None, coordinate1 = None):
    '''

    Parameters
    ----------
    connection : db_connection
        DESCRIPTION.
    query : string or None
        DESCRIPTION. The default is None.
    location1 : string or None
        DESCRIPTION. The default is None. 
    coordinate1 : tuple or None
        DESCRIPTION. The default is None.
    Returns
    -------
    None.

    '''
    if query and location1 and coordinate1 :
        print("Error: Please provide either location or coordinates.")
    if query and (location1 or coordinate1) :
        # Implementing query-based search
        keywords = process_natural_language_query(query)
        print("Keywords extracted:", keywords)
        if keywords:
            try:
                score_expression = calculate_score_expression(weights, keywords)
                where_clauses = []
                for keyword in keywords:
                    keyword_clauses = [
                        f"LOWER(file_name) LIKE '%{keyword}%'",
                        f"LOWER(file_type) LIKE '%{keyword}%'",
                    ]
                    if "file_size" in weights:
                        keyword_clauses.append(
                            f"CAST(file_size AS TEXT) LIKE '%{keyword}%'"
                        )
                    if "creation_date" in weights:
                        keyword_clauses.append(
                            f"CAST(creation_date AS TEXT) LIKE '%{keyword}%'"
                        )
                    where_clauses.append(" OR ".join(keyword_clauses))

                    search_query = text(f"""
                    SELECT file_id, file_name, file_type, file_size, creation_date, ({score_expression}) AS relevance_score
                    FROM common_metadata
                    WHERE {' OR '.join(where_clauses)} ORDER BY relevance_score DESC 
                    """)    
                    # search_query += " ORDER BY relevance_score DESC"
                results = execute_sql_query(search_query)
                if results:
                    for result in results:
                        print(result)
                else:
                    print("No results found.")
            except Exception as e:
                print(f"Error: Unable to execute SQL query. {e}")
                
        # extracting file metadata which contains the given coordinate
        output = check_loc(location=location1,coordinates=coordinate1)
        print(output)
        
        # giving the common files as ouput
        final = []
        if result == None:
            if output == None:
                print("Both Results None")
                return final
            else:
                print("printing location based results")
                return output
        if output != None:
            for i in results:
                if i[0:4] in output:
                    final.append(i)
        print(final)
        return final
    elif query:
        keywords = process_natural_language_query(query)
        print("Keywords extracted:", keywords)
        if keywords:
            try:
                score_expression = calculate_score_expression(weights, keywords)
                where_clauses = []
                for keyword in keywords:
                    keyword_clauses = [
                        f"LOWER(file_name) LIKE '%{keyword}%'",
                        f"LOWER(file_type) LIKE '%{keyword}%'",
                    ]
                    if "file_size" in weights:
                        keyword_clauses.append(
                            f"CAST(file_size AS TEXT) LIKE '%{keyword}%'"
                        )
                    if "creation_date" in weights:
                        keyword_clauses.append(
                            f"CAST(creation_date AS TEXT) LIKE '%{keyword}%'"
                        )
                    where_clauses.append(" OR ".join(keyword_clauses))

                search_query = text(f"""
                   SELECT file_id, file_name, file_type, file_size, creation_date, ({score_expression}) AS relevance_score
                   FROM common_metadata
                   WHERE {' OR '.join(where_clauses)} ORDER BY relevance_score DESC 
                """)
                # search_query = search_query.concat(text(" "))
                results = execute_sql_query(search_query)
                
                
                if results:
                    
                    for result in results:
                        print(result)
                    return results
                else:
                    print("No results found.")
            except Exception as e:
                print(f"Error: Unable to execute SQL query. {e}")
    elif location1 or coordinate1:
        #Implemented coordinate-based search
        output = check_loc(location=location1,coordinates=coordinate1)
        print(output)
        return output
        
    else:
        print(
            "Error: Insufficient input. Please provide either a query or coordinates."
        )
