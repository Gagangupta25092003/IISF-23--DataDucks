import geopandas as gpd
import h3
import os
import logging
from concurrent.futures import ProcessPoolExecutor
from rtree import index
from shapely.geometry import shape, box
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString
import pickle

class GeoJsonProcessor:
    def __init__(self, target_crs="EPSG:4326", h3_resolution=6):
        self.target_crs = target_crs
        self.h3_resolution = h3_resolution
        logging.basicConfig(level=logging.INFO)


    def h3_index_for_geometry(self, geom):
        if geom.geom_type == "Point":
            return h3.geo_to_h3(geom.y, geom.x, self.h3_resolution)
        elif geom.geom_type == "Polygon":
            return [
                h3.geo_to_h3(y, x, self.h3_resolution) for x, y in geom.exterior.coords
            ]
        elif geom.geom_type == "LineString":
            return [h3.geo_to_h3(y, x, self.h3_resolution) for x, y in geom.coords]
        elif geom.geom_type == "MultiPolygon":
            return [
                h3.geo_to_h3(y, x, self.h3_resolution)
                for polygon in geom.geoms
                for x, y in polygon.exterior.coords
            ]
        elif geom.geom_type == "MultiLineString":
            return [
                h3.geo_to_h3(y, x, self.h3_resolution)
                for linestring in geom.geoms
                for x, y in linestring.coords
            ]
        else:
            return h3.geo_to_h3(geom.centroid.y, geom.centroid.x, self.h3_resolution)

    def process_geojson(self, file_path):
        try:
            gdf = gpd.read_file(file_path)
            gdf["geometry"] = gdf["geometry"].apply(
                lambda geom: geom.buffer(0) if not geom.is_valid else geom
            )

            if gdf.crs != self.target_crs:
                gdf = gdf.to_crs(self.target_crs)

            gdf["area"] = gdf["geometry"].apply(
                lambda geom: geom.area
                if geom.geom_type in ["Polygon", "MultiPolygon"]
                else None
            )
            gdf["geometry"] = gdf["geometry"].to_crs(self.target_crs)

            gdf["length"] = gdf["geometry"].apply(
                lambda geom: geom.length
                if geom.geom_type in ["LineString", "MultiLineString"]
                else None
            )

            gdf["bounding_box"] = gdf["geometry"].bounds.apply(
                lambda row: f"({row['minx']}, {row['miny']}), ({row['maxx']}, {row['miny']}), ({row['maxx']}, {row['maxy']}), ({row['minx']}, {row['maxy']})",
                axis=1,
            )

            gdf["h3_index"] = gdf["geometry"].apply(
                lambda geom: self.h3_index_for_geometry(geom)
            )
            gdf["h3_index"] = gdf["h3_index"].apply(
                lambda h3_indices: ",".join(h3_indices)
                if isinstance(h3_indices, list)
                else h3_indices
            )

            standard_columns = [
                "id",
                "name",
                "type",
                "geometry",
                "area",
                "length",
                "bounding_box",
                "h3_index",
            ]

            for col in standard_columns:
                if col not in gdf.columns:
                    gdf[col] = None
            gdf = gdf[standard_columns]

            return gdf
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            return None

    def save_processed_geojson(self, gdf, output_path):
        try:
            gdf.to_file(output_path, driver="GeoJSON")
        except Exception as e:
            logging.error(f"Error saving file {output_path}: {e}")

    def preprocess_geojson_files(self, input_folder, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with ProcessPoolExecutor() as executor:
            futures = []
            for file_name in os.listdir(input_folder):
                if file_name.endswith(".geojson"):
                    logging.info(f"Processing file: {file_name}")
                    file_path = os.path.join(input_folder, file_name)
                    output_path = os.path.join(output_folder, file_name)
                    futures.append(
                        executor.submit(self.process_and_save, file_path, output_path)
                    )

            for future in futures:
                future.result()

    def process_and_save(self, file_path, output_path):
        processed_gdf = self.process_geojson(file_path)
        if processed_gdf is not None:
            self.save_processed_geojson(processed_gdf, output_path)
            logging.info(f"Processed and saved: {os.path.basename(output_path)}")

class GeospatialIndexer:
    def __init__(self, target_crs="EPSG:4326", h3_resolution=6):
        self.target_crs = target_crs
        self.h3_resolution = h3_resolution

    def create_rtree_index(self, gdf):
        spatial_index = index.Index()
        for idx, row in gdf.iterrows():
            spatial_index.insert(idx, shape(row["geometry"]).bounds)
        return spatial_index

    def add_h3_index(self, gdf):
        gdf["h3_index"] = gdf["geometry"].apply(
            lambda geom: h3.geo_to_h3(
                geom.centroid.y, geom.centroid.x, self.h3_resolution
            )
        )
        return gdf

    def process_and_index_geojson(self, file_path):
        gdf = gpd.read_file(file_path)
        gdf = self.add_h3_index(gdf)
        rtree_index = self.create_rtree_index(gdf)
        final_metadata = {"geo_dataframe": gdf, "rtree_index": rtree_index}
        return final_metadata

class GeoJsonProcessingAndIndexing:
    def __init__(self, input_folder, output_folder, target_crs="EPSG:4326", h3_resolution=6):
        self.processor = GeoJsonProcessor(target_crs, h3_resolution)
        self.indexer = GeospatialIndexer(target_crs, h3_resolution)
        self.input_folder = input_folder
        self.output_folder = output_folder

    def process_and_index_files(self, file_name, file_path, output_folder):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        if file_name.endswith(".geojson"):
            file_path = os.path.join(self.input_folder, file_name)
            output_path = os.path.join(self.output_folder, file_name)
            return self.process_and_save(file_path, output_path)
            


    def process_and_index(self, file_path, output_path):
        processed_gdf = self.processor.process_geojson(file_path)
        if processed_gdf is not None:
            final_metadata = self.indexer.process_and_index_geojson(file_path)
            final_metadata['geo_dataframe'] = processed_gdf
            return final_metadata


# # Example usage
# input_folder = "/path/to/your/input/folder"
# output_folder = "/path/to/your/output/folder"
# processing_and_indexing = GeoJsonProcessingAndIndexing(input_folder, output_folder)
# processing_and_indexing.process_and_index_files()