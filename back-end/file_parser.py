import laspy
import numpy as np
import geopandas as gpd
import h3
from shapely.geometry import Point
import pathlib
import psycopg2
from datetime import datetime
import geopandas as gpd
import os
import logging
from concurrent.futures import ProcessPoolExecutor
from rtree import index
from shapely.geometry import shape, box
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString
import pickle
import rasterio
from osgeo import gdal
from PIL import Image
import multiprocessing
import logging
import json
import requests
import pickle
from transformers import BlipProcessor, BlipForConditionalGeneration
import geopandas as gpd
import shapely
import cv2
from loguru import logger
from concurrent.futures import ProcessPoolExecutor
import rtree  # Import the R-tree library
from osgeo import osr

from osgeo import osr
from osgeo import ogr
from osgeo import gdal
import psycopg2
from shapely.geometry import box
from shapely.wkb import dumps
from osgeo import gdal
from metadata_tables import Common_Metadata, Geojson_Metadata, Tiff_Metadata, Las_Metadata

# Read the array from the file
with open('data_extensions.pkl', 'rb') as file:
    type_dict = list(pickle.load(file))

with open('data_size.pkl', 'rb') as file:
    size_dict = pickle.load(file)

file_gis_extensions = {
    "vector": [
        ".shp",
        ".dbf",
        ".shx",
        ".geojson",
        ".json",
        ".gml",
        ".kml",
        ".kmz",
        ".gpx",
        ".vct",
        ".vdc",
        ".tab",
        ".dat",
        ".id",
        ".map",
        ".ind",
        ".osm",
        ".dlg",
        ".dgn",
        ".dxf",
        ".e00",
        ".gpkg",
        ".mif",
        ".sbn",
        ".sbx",
    ],
    "raster": [
        ".tif",
        ".tiff",
        ".img",
        ".ecw",
        ".sid",
        ".jp2",
        ".jpeg",
        ".png",
        ".bmp",
        ".gif",
        ".grd",
        ".hdf",
        ".dem",
        ".dt2",
        ".asc",
        ".nc",
        ".adf",
        ".bil",
        ".bip",
        ".bsq",
        ".cub",
        ".hdr",
        ".raw",
        ".terr",
        ".hgt",
        ".dtm",
    ],
    "compressed_raster": [".mrsid", ".jpx"],
    "lidar": [".las", ".laz", ".e57", ".ply", ".pts"],
    "multitemporal": [".hdf5"],
    ## Cannot be worked on directly since we do not know what to expect inside these
    "tabular": [".csv", ".xls", ".xlsx", ".dbf", ".tsv"],
    "web": [".wms", ".wfs", ".wcs", ".wmts", ".pdf"],
    "cartographic": [".mxd", ".qgs", ".lyr", ".style", ".sld"],
    "geographic_database": [".gdb", ".mdb", ".sde", ".sqlite"],
}


vector_extensions = file_gis_extensions["vector"]
raster_extensions = file_gis_extensions["raster"]
multitemporal_extensions = file_gis_extensions["multitemporal"]
lidar_extensions = file_gis_extensions["lidar"]
compressed_raster_extensions = file_gis_extensions["compressed_raster"]
other_extensions = (
    file_gis_extensions["tabular"]
    + file_gis_extensions["web"]
    + file_gis_extensions["cartographic"]
    + file_gis_extensions["geographic_database"]
)



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
geojson_processor = GeoJsonProcessor()

class GeoTIFFProcessor:
    def __init__(self):
        self.processor_blip = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        )
        self.model_blip = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        )
        logger.add("geotiff_processing_log.log", rotation="1 day")

    def extract_geospatial_info(self, dataset):
        """Extract geospatial information from the dataset."""
        try:
            geotransform = dataset.GetGeoTransform()
            projection = osr.SpatialReference(wkt=dataset.GetProjection())

            # Get the bounding box
            width, height = dataset.RasterXSize, dataset.RasterYSize
            minx = geotransform[0]
            miny = geotransform[3] + width * geotransform[4] + height * geotransform[5]
            maxx = geotransform[0] + width * geotransform[1] + height * geotransform[2]
            maxy = geotransform[3]

            # Center of the bounding box
            centerx = (minx + maxx) / 2
            centery = (miny + maxy) / 2

            # Convert to lat/lon if not already
            if projection.IsProjected():
                ct = osr.CoordinateTransformation(projection, projection.CloneGeogCS())
                centerx, centery, _ = ct.TransformPoint(centerx, centery)

            return centerx, centery, (minx, miny, maxx, maxy)
        except Exception as e:
            logger.error(f"Error in extract_geospatial_info: {e}")
            return None, None, None

    def extract_metadata(self, file_path):
        try:
            dataset = gdal.Open(file_path)
            if dataset is None:
                logger.warning(f"Dataset is None for file: {file_path}")
                return None

            metadata = dataset.GetMetadata()
            proj = dataset.GetProjection()
            geotransform = dataset.GetGeoTransform()

            return {
                "metadata": metadata,
                "projection": proj,
                "geotransform": geotransform,
            }
        except Exception as e:
            logger.error(f"Error in extract_metadata: {e}")
            return None

    def caption_image(self, image, conditional_text=None):
        try:
            if conditional_text:
                inputs = self.processor_blip(
                    image, conditional_text, return_tensors="pt"
                )
            else:
                inputs = self.processor_blip(image, return_tensors="pt")

            out = self.model_blip.generate(**inputs)
            return self.processor_blip.decode(out[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error in caption_image: {e}")
            return None

    def process_file(self, filename):
        file_path = filename
        try:
            metadata = self.extract_metadata(file_path)

            with rasterio.open(file_path) as src:
                img = src.read()
                img = np.transpose(img, (1, 2, 0))  # Channels last for PIL Image
                pil_image = Image.fromarray(img)
                dataset = gdal.Open(file_path)
                centerx, centery, bbox = self.extract_geospatial_info(dataset)

                if centerx is not None and centery is not None:
                    h3_index = h3.geo_to_h3(centery, centerx, resolution=9)
                else:
                    h3_index = None

            caption_conditional = self.caption_image(pil_image, "a photograph of")
            caption_unconditional = self.caption_image(pil_image)

            return {
                "filename": filename,
                "metadata": metadata,
                "h3_index": h3_index,
                "caption_conditional": caption_conditional,
                "caption_unconditional": caption_unconditional,
            }
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return {
                "filename": filename,
                "metadata": None,
                "h3_index": None,
                "caption_conditional": None,
                "caption_unconditional": None,
            }
geo_tiff_processor = GeoTIFFProcessor()

class LasFileProcessor:
    def extract_metadata(self, las):
        metadata = {
            "point_format": las.header.point_format.id,
            "number_of_points": las.header.point_count,
            "scale_factors": las.header.scale,
            "offsets": las.header.offset,
            "min_bounds": las.header.min,
            "max_bounds": las.header.max,
        }
        return metadata

    def read_las_file(self, las_file_path):
        try:
            las = laspy.read(las_file_path)
            coords = np.vstack((las.x, las.y, las.z)).transpose()
            attributes = {
                "intensity": las.intensity,
                "classification": las.classification,
            }
            metadata = self.extract_metadata(las)
            return coords, attributes, metadata, True
        except Exception as e:
            print(f"Error reading {las_file_path}: {e}")
            return None, None, None, False

    def create_geospatial_index(self, coords, attributes, metadata):
        gdf = gpd.GeoDataFrame(attributes, geometry=[Point(xyz) for xyz in coords])
        for key, value in metadata.items():
            gdf[key] = value

        min_bounds = metadata.get("min_bounds")
        max_bounds = metadata.get("max_bounds")
        if min_bounds and max_bounds:
            bounding_box = Polygon(
                [
                    (min_bounds[0], min_bounds[1]),
                    (min_bounds[0], max_bounds[1]),
                    (max_bounds[0], max_bounds[1]),
                    (max_bounds[0], min_bounds[1]),
                ]
            )
            gdf["bounding_box"] = bounding_box

        gdf["h3_index"] = gdf.apply(
            lambda row: h3.geo_to_h3(row.geometry.y, row.geometry.x, 7), axis=1
        )
        return gdf

    def process_las_file(self, las_file_path):
        coords, attributes, metadata, success = self.read_las_file(las_file_path)
        if success:
            return self.create_geospatial_index(coords, attributes, metadata)
        else:
            return None
las_file_processor = LasFileProcessor()

def convert_to_geojson(input_path):
    try:
        dataSource = ogr.Open(input_path)
        if dataSource is None:
            raise IOError(f"Failed to open file {input_path}")

        inLayer = dataSource.GetLayer()
        inLayerDefn = inLayer.GetLayerDefn()

        # Use GeoJSON driver and create a temporary file
        driver = ogr.GetDriverByName("GeoJSON")
        output_path = "check.geojson"
        if os.path.exists(output_path):
            driver.DeleteDataSource(output_path)
        outDataSource = driver.CreateDataSource(output_path)
        outLayer = outDataSource.CreateLayer("layer", geom_type=inLayer.GetGeomType())

        # Copy fields from the input layer to the output layer
        for i in range(inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)

        outLayerDefn = outLayer.GetLayerDefn()

        for inFeature in inLayer:
            geom = inFeature.GetGeometryRef()

            # Coordinate transformation to WGS 84
            sourceSR = inLayer.GetSpatialRef()
            targetSR = osr.SpatialReference()
            targetSR.ImportFromEPSG(4326)
            if sourceSR and not sourceSR.IsSame(targetSR):
                coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
                geom.Transform(coordTrans)

            outFeature = ogr.Feature(outLayerDefn)
            outFeature.SetGeometry(geom)
            for i in range(outLayerDefn.GetFieldCount()):
                outFeature.SetField(
                    outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i)
                )

            outLayer.CreateFeature(outFeature)

        dataSource = None
        outDataSource = None
    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

def convert_lidar_to_las(input_path):
    try:
        lidar_file = gdal.Open(input_path)
        if lidar_file is None:
            raise IOError(f"Failed to open file {input_path}")

        output_path = "check.las"

        driver = gdal.GetDriverByName("LAS")
        out_dataset = driver.CreateCopy(output_path, lidar_file, 0)

        lidar_file = None
        out_dataset = None

        print(f"Converted {input_path} to LAS at {output_path}")

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

def convert_compressed_raster_to_geotiff(input_path):
    try:
        compressed_raster = gdal.Open(input_path)
        if compressed_raster is None:
            raise IOError(f"Failed to open file {input_path}")

        output_path = "check.tif"

        driver = gdal.GetDriverByName("GTiff")
        options = [
            "COMPRESS=DEFLATE",
            f"NUM_THREADS=ALL_CPUS",
            f"PREDICTOR=2",
            f"ZLEVEL=9",
            f"GDAL_TIFF_INTERNAL_MASK=YES",
            f"COPY_SRC_OVERVIEWS=YES",
            f"TILED=YES",
            f"SPARSE_OK=TRUE",
            f"BLOCKXSIZE=256",
            f"BLOCKYSIZE=256",
        ]
        out_dataset = driver.CreateCopy(output_path, compressed_raster, 0, options)

        compressed_raster = None
        out_dataset = None

        print(f"Converted {input_path} to GeoTIFF")

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

def convert_multitemporal_to_geotiff(input_path):
    try:
        hdf5_file = gdal.Open(input_path)
        if hdf5_file is None:
            raise IOError(f"Failed to open file {input_path}")

        subdatasets = hdf5_file.GetSubDatasets()
        if not subdatasets:
            print(f"No subdatasets found in {input_path}")
            return

        for idx, (subdataset_name, _) in enumerate(subdatasets):
            subdataset = gdal.Open(subdataset_name)
            if subdataset is None:
                print(f"Failed to open subdataset {subdataset_name}")
                continue

            output_path = "check.tif"

            driver = gdal.GetDriverByName("GTiff")
            options = [
                "COMPRESS=DEFLATE",
                f"NUM_THREADS=ALL_CPUS",
                f"PREDICTOR=2",
                f"ZLEVEL=9",
                f"GDAL_TIFF_INTERNAL_MASK=YES",
                f"COPY_SRC_OVERVIEWS=YES",
                f"TILED=YES",
                f"SPARSE_OK=TRUE",
                f"BLOCKXSIZE=256",
                f"BLOCKYSIZE=256",
            ]
            out_dataset = driver.CreateCopy(output_path, subdataset, 0, options)

            subdataset = None
            out_dataset = None

            print(f"Converted {subdataset_name} to GeoTIFF")

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

def convert_to_geotiff(input_path):
    try:
        output_path = "check.tif"

        dataset = gdal.Open(input_path)
        if dataset is None:
            raise IOError(f"Failed to open file {input_path}")

        driver = gdal.GetDriverByName("GTiff")

        band = dataset.GetRasterBand(1)  # Assuming a single band raster here
        nodata_value = band.GetNoDataValue()
        if nodata_value is not None:
            options = [
                "COMPRESS=DEFLATE",
                f"NUM_THREADS=ALL_CPUS",
                f"PREDICTOR=2",
                f"ZLEVEL=9",
                f"GDAL_TIFF_INTERNAL_MASK=YES",
                f"COPY_SRC_OVERVIEWS=YES",
                f"TILED=YES",
                f"SPARSE_OK=TRUE",
                f"BLOCKXSIZE=256",
                f"BLOCKYSIZE=256",
            ]
            out_dataset = driver.CreateCopy(output_path, dataset, 0, options)
            out_band = out_dataset.GetRasterBand(1)
            out_band.SetNoDataValue(nodata_value)
        else:
            options = [
                "COMPRESS=DEFLATE",
                f"NUM_THREADS=ALL_CPUS",
                f"PREDICTOR=2",
                f"ZLEVEL=9",
                f"GDAL_TIFF_INTERNAL_MASK=YES",
                f"COPY_SRC_OVERVIEWS=YES",
                f"TILED=YES",
                f"SPARSE_OK=TRUE",
                f"BLOCKXSIZE=256",
                f"BLOCKYSIZE=256",
            ]
            out_dataset = driver.CreateCopy(output_path, dataset, 0, options)

        metadata = dataset.GetMetadata()
        if metadata:
            out_dataset.SetMetadata(metadata)

        dataset = None
        out_dataset = None

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

def classify_file_type(file_extension):
    vector_extensions = file_gis_extensions["vector"]
    raster_extensions = file_gis_extensions["raster"]
    multitemporal_extensions = file_gis_extensions["multitemporal"]
    lidar_extensions = file_gis_extensions["lidar"]
    compressed_raster_extensions = file_gis_extensions["compressed_raster"]
    other_extensions = (
        file_gis_extensions["tabular"]
        + file_gis_extensions["web"]
        + file_gis_extensions["cartographic"]
        + file_gis_extensions["geographic_database"]
    )

    if file_extension in vector_extensions:
        return "geojson"
    elif (
        file_extension in raster_extensions
        or file_extension in multitemporal_extensions
        or file_extension in compressed_raster_extensions
    ):
        return "geotiff"
    elif file_extension in lidar_extensions:
        return "las"
    else:
        return "others"

def insert_geojson_metadata(conn, gdf, file_path):
    # cursor = conn.cursor()
    

    ids = ",".join(map(str, gdf["id"].tolist()))
    names = ",".join(gdf["name"].astype(str).tolist()).replace("None", "")
    types = ",".join(gdf["type"].astype(str).tolist()).replace("None", "")
    geometries = ";".join(gdf["geometry"].astype(str).tolist()).replace("None", "")

    areas = ",".join(map(str, gdf["area"].tolist())).replace("None", "")
    lengths = ",".join(map(str, gdf["length"].tolist())).replace("None", "")
    bounding_boxes = ";".join(gdf["bounding_box"].tolist()).replace("None", "")
    h3_indices = ",".join(
        [",".join(h3_index.split(",")) for h3_index in gdf["h3_index"].tolist()]
    ).replace("None", "")
    
    # cursor.execute(
    #     """
    #     INSERT INTO geojson_metadata (file_location, id, name, type, geometry, area, length, bounding_box, h3_index)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     ON CONFLICT (file_path) DO NOTHING;
    #     """,
    #     (
    #         file_path,
    #         ids,
    #         names,
    #         types,
    #         geometries,
    #         areas,
    #         lengths,
    #         bounding_boxes,
    #         h3_indices,
    #     ),
    # )

    # conn.commit()
    
    new_file = Geojson_Metadata(
        file_location=file_path,
        area=areas,
        length=lengths,
        bounding_box=bounding_boxes,
        h3_index=h3_indices,
        geometries=geometries,
        data_types=types,
        data_names=names
        
    )
    conn.session.add(new_file)
    conn.session.commit()

def insert_tiff_metadata(conn, file_path, processed_data):
    # cursor = conn.cursor()

    # Extract data from the processed_data dictionary
    metadata = processed_data.get("metadata", {})
    projection = metadata.get("projection", None)
    geotransform = metadata.get("geotransform", None) if metadata else None
    centerx, centery, bbox = processed_data.get("bbox", (None, None, None))

    # Construct bounding box geometry
    if bbox:
        minx, miny, maxx, maxy = bbox
        bounding_box = box(minx, miny, maxx, maxy)
        bounding_box_wkb = dumps(
            bounding_box, hex=True
        )  # Convert to WKB hex format for PostGIS
    else:
        bounding_box_wkb = None

    caption_conditional = processed_data.get("caption_conditional", None)
    caption_unconditional = processed_data.get("caption_unconditional", None)

    # # SQL INSERT statement
    # cursor.execute(
    #     """
    #     INSERT INTO tiff_metadata (file_location, projection, geotransform, centerx, centery, bounding_box, caption_conditional, caption_unconditional)
    #     VALUES (%s, %s, %s, %s, %s, ST_GeomFromWKB(%s), %s, %s)
    #     ON CONFLICT (file_path) DO NOTHING;
    #     """,
    #     (
    #         file_path,
    #         projection,
    #         geotransform,
    #         centerx,
    #         centery,
    #         bounding_box_wkb,
    #         caption_conditional,
    #         caption_unconditional,
    #     ),
    # )

    # # Commit the transaction
    # conn.commit()
    
    new_file=Tiff_Metadata(
        file_location=file_path,
        projection=projection,
        centerx=centerx,
        centery=centery,
        bounding_box=bounding_box_wkb,
        geotransform=geotransform,
        caption_conditional=caption_conditional,
        caption_unconditional=caption_unconditional
    )
    
    conn.session.add(new_file)
    conn.session.commit()



# Database connection setup
    params = {
        "database": "dataducks",
        "user": "postgres",
        "password": "12345678",
        "host": "localhost",
        "port": 5432,
    }
    conn = psycopg2.connect(**params)
    return conn

def insert_las_metadata(conn, file_path, geospatial_index):
    # cursor = conn.cursor()

    point_format = geospatial_index["point_format"][0]
    number_of_points = geospatial_index["number_of_points"][0]
    scale_factors = geospatial_index["scale_factors"][0]
    offsets = geospatial_index["offsets"][0]

    min_bounds = geospatial_index["min_bounds"][0]
    max_bounds = geospatial_index["max_bounds"][0]
    bounding_box = Polygon(
        [
            (min_bounds[0], min_bounds[1]),
            (min_bounds[0], max_bounds[1]),
            (max_bounds[0], max_bounds[1]),
            (max_bounds[0], min_bounds[1]),
        ]
    )

    min_bounds_wkb = dumps(min_bounds, hex=True)
    max_bounds_wkb = dumps(max_bounds, hex=True)
    bounding_box_wkb = dumps(bounding_box, hex=True)

    h3_indices = ",".join(geospatial_index["h3_index"].astype(str))

    # cursor.execute(
    #     """
    #     INSERT INTO las_metadata (file_location, point_format, number_of_points, scale_factors, offsets, min_bounds, max_bounds, bounding_box, h3_index)
    #     VALUES (%s, %s, %s, %s, %s, ST_GeomFromWKB(%s), ST_GeomFromWKB(%s), ST_GeomFromWKB(%s), %s)
    #     ON CONFLICT (file_path) DO NOTHING;
    #     """,
    #     (
    #         file_path,
    #         point_format,
    #         number_of_points,
    #         scale_factors,
    #         offsets,
    #         min_bounds_wkb,
    #         max_bounds_wkb,
    #         bounding_box_wkb,
    #         h3_indices,
    #     ),
    # )

    # conn.commit()
    new_file = Las_Metadata(
        file_location=file_path,
        point_format=point_format,
        number_of_points=number_of_points,
        offsets=offsets,
        min_bounds=min_bounds_wkb,
        scale_factors=scale_factors,
        max_bounds=max_bounds_wkb,
        bounding_box=bounding_box_wkb,
        h3_index=h3_indices
    )
    
    conn.session.add(new_file)
    conn.session.commit()

def insert_metadata(conn, file_info):
    # cursor = conn.cursor()
    # cursor.execute(
    #     """
    #     INSERT INTO common_metadata (file_name, file_location, file_type, file_size, creation_date)
    #     VALUES (%s, %s, %s, %s, %s, %s)
    #     ON CONFLICT (file_location) DO NOTHING;
    #     """,
    #     (
    #         file_info["file_name"],
    #         file_info["file_owner"],
    #         file_info["file_path"],
    #         file_info["file_type"],
    #         file_info["file_size"],
    #         file_info["creation_date"]
    #     ),
    # )
    # conn.commit()
    new_file = Common_Metadata(
        file_name=file_info["file_name"],
        file_location=file_info["file_path"],
        file_type=file_info["file_type"],
        file_size=file_info["file_size"],
        creation_date=file_info["creation_date"],
        last_accessed=file_info["creation_date"]        
    )
    conn.session.add(new_file)
    conn.session.commit()

def process_files(root_directory, conn):
    file_type_counts = {}  # Dictionary to count file types
    file_size_range = {
        "min": float("inf"),
        "max": float("-inf"),
    }  # Dictionary to track min and max file sizes
    print("Reached Process Files Function")
    for folder_name, subfolders, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            if os.path.isfile(file_path):
                
                try:
                    print(filename)
                    file_stats = os.stat(file_path)
                    file_type = pathlib.Path(file_path).suffix
                    file_size = file_stats.st_size
                    
                    root, file_ext = os.path.splitext(filename)
                    if file_ext not in type_dict:
                        type_dict.append(file_ext)

                    # Update file type counts
                    file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1

                    # Update min and max file sizes
                    size_dict["min"] = min(size_dict["min"], file_size)
                    size_dict["max"] = max(size_dict["max"], file_size)

                    file_info = {
                        "file_name": os.path.basename(file_path),
                        "file_owner": "",  # Placeholder for file owner
                        "file_path": file_path,
                        "file_type": file_type,
                        "file_size": file_size,
                        "creation_date": datetime.fromtimestamp(file_stats.st_ctime),
                        "last_accessed": datetime.fromtimestamp(file_stats.st_atime),
                        "total_access": 0,  # Placeholder for total access
                        "total_downloads": 0,  # Placeholder for total downloads
                    }
                    insert_metadata(conn, file_info)
                    print("Done Common Metadata")

                    file_category = classify_file_type(file_info["file_type"])
                    if file_category == "geojson":
                        convert_to_geojson(file_path)
                        try:
                            processed_gdf = geojson_processor.process_geojson("check.geojson")
                            insert_geojson_metadata(conn, processed_gdf, file_path)
                        except Exception as e:
                            print(e)
                        
                    elif file_category == "geotiff":
                        if file_info["file_type"] in multitemporal_extensions:
                            convert_multitemporal_to_geotiff(file_path)
                        elif file_info["file_type"] in compressed_raster_extensions:
                            convert_compressed_raster_to_geotiff(file_path)
                        else:
                            convert_to_geotiff(file_path)
                        try:
                            result = geo_tiff_processor.process_file("check.tif")
                            insert_tiff_metadata(conn, file_path, result)
                        except Exception as e:
                            print(e)
                        

                    elif file_category == "las":
                        convert_lidar_to_las(file_path)
                        # Process 'check.las' and get the GeoDataFrame
                        try:
                            gdf = las_file_processor.process_las_file("check.las")
                            insert_las_metadata(conn, file_path, gdf)
                        except Exception as e:
                            print(e)
                        
                    print("Done File")
                    
                except Exception as e:                    
                    print(e)
                
                # else: Do nothing for 'others'
                # Insert metadata into the database for each file
                # insert_metadata(conn, file_info)
                
    
    with open('data_extensions.pkl', 'wb') as file:
         pickle.dump(type_dict, file)
    with open('data_size.pkl', 'wb') as file:
         pickle.dump(size_dict, file)
    # return file_type_counts, file_size_range
