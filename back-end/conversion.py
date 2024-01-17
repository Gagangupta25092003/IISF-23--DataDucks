
import os
from osgeo import osr
from osgeo import ogr
from osgeo import gdal
import shutil
from geotiff import GeoTIFFProcessor
from geojson import GeoJsonProcessingAndIndexing
from lasfile import LasFileProcessor





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
    "web": [".wms", ".wfs", ".wcs", ".wmts",".pdf"],
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
   


def convert_to_geojson(input_path, output_path):
    try:
        dataSource = ogr.Open(input_path)
        if dataSource is None:
            raise IOError(f"Failed to open file {input_path}")

        inLayer = dataSource.GetLayer()

        driver = ogr.GetDriverByName("GeoJSON")
        if os.path.exists(output_path):
            driver.DeleteDataSource(output_path)
        outDataSource = driver.CreateDataSource(output_path)
        outLayer = outDataSource.CreateLayer("layer", geom_type=inLayer.GetGeomType())

        inLayerDefn = inLayer.GetLayerDefn()
        for i in range(inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)

        outLayerDefn = outLayer.GetLayerDefn()

        for inFeature in inLayer:
            geom = inFeature.GetGeometryRef()

            sourceSR = inLayer.GetSpatialRef()
            targetSR = osr.SpatialReference()
            targetSR.ImportFromEPSG(4326)  # WGS 84
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

            outFeature = None

        dataSource = None
        outDataSource = None

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")


#############################################################################################################################################################

def convert_to_geotiff(input_path, output_path):
    try:
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


#############################################################################################################################################################

def convert_multitemporal_to_geotiff(input_path, output_folder, not_processed_folder):
    try:
        hdf5_file = gdal.Open(input_path)
        if hdf5_file is None:
            raise IOError(f"Failed to open file {input_path}")

        subdatasets = hdf5_file.GetSubDatasets()
        if not subdatasets:
            not_processed_path = os.path.join(
                not_processed_folder, os.path.basename(input_path)
            )
            os.rename(input_path, not_processed_path)
            print(f"Moved {input_path} to {not_processed_path} (No subdatasets found)")
            return

        for idx, (subdataset_name, _) in enumerate(subdatasets):
            subdataset = gdal.Open(subdataset_name)
            if subdataset is None:
                print(f"Failed to open subdataset {subdataset_name}")
                continue

            output_path = os.path.join(
                output_folder, f"{os.path.basename(input_path)}_subdataset_{idx}.tif"
            )

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

            print(f"Converted {subdataset_name} to GeoTIFF at {output_path}")

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

#############################################################################################################################################################

def convert_lidar_to_las(input_path, output_folder):
    try:
        lidar_file = gdal.Open(input_path)
        if lidar_file is None:
            raise IOError(f"Failed to open file {input_path}")

        output_path = os.path.join(
            output_folder, f"{os.path.splitext(os.path.basename(input_path))[0]}.las"
        )

        driver = gdal.GetDriverByName("LAS")
        out_dataset = driver.CreateCopy(output_path, lidar_file, 0)

        lidar_file = None
        out_dataset = None

        print(f"Converted {input_path} to LAS at {output_path}")

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")


#############################################################################################################################################################

def convert_compressed_raster_to_geotiff(input_path, output_folder):
    try:
        compressed_raster = gdal.Open(input_path)
        if compressed_raster is None:
            raise IOError(f"Failed to open file {input_path}")

        output_path = os.path.join(
            output_folder, f"{os.path.splitext(os.path.basename(input_path))[0]}.tif"
        )

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

        print(f"Converted {input_path} to GeoTIFF at {output_path}")

    except Exception as e:
        print(f"Error processing file {input_path}: {e}")
        
        
  


#############################################################################################################################################################

def process_folder(filename, folder_path, output_folder, not_processed_folder, vector_extensions = vector_extensions, raster_extensions=raster_extensions, multitemporal_extensions = multitemporal_extensions, lidar_extensions = lidar_extensions, compressed_raster_extensions = compressed_raster_extensions):
    name, extension = os.path.splitext(filename)
    input_path = os.path.join(folder_path, filename)
    output_path = None
    metadata=""
    
    
    if extension.lower() in vector_extensions:
        output_path = os.path.join(output_folder, f"{name}.geojson")
        convert_to_geojson(input_path, output_path)
        processing_and_indexing = GeoJsonProcessingAndIndexing(input_folder=input_path, output_folder=output_folder)
        metadata = processing_and_indexing.process_and_index_files(file_name=filename, file_path=output_path)
        
        
        
        
    elif extension.lower() in raster_extensions:
        output_path = os.path.join(output_folder, f"{name}.tif")
        convert_to_geotiff(input_path, output_path)
        processor_GeoTiff = GeoTIFFProcessor(input_directory= "", output_directory="")
        metadata = processor_GeoTiff.process_single_file(file_name=filename, file_path=output_path)
        
    elif extension.lower() in multitemporal_extensions:
        convert_multitemporal_to_geotiff(input_path, output_folder, output_folder)
        processor_GeoTiff = GeoTIFFProcessor(input_directory= "", output_directory="")
        metadata = processor_GeoTiff.process_single_file(file_name=filename, file_path=output_path)
        
    elif extension.lower() in lidar_extensions:
        output_path = os.path.join(output_folder, f"{name}.las")
        convert_lidar_to_las(input_path, output_path)

        processor = LasFileProcessor(output_folder, output_folder)
        metadata = processor.process_single_file(output_path)
        
        
    elif extension.lower() in compressed_raster_extensions:
        output_path = os.path.join(output_folder, f"{name}.tif")
        convert_compressed_raster_to_geotiff(input_path, output_path)
        processor_GeoTiff = GeoTIFFProcessor(input_directory= "", output_directory="")
        metadata = processor_GeoTiff.process_single_file(file_name=filename, file_path=output_path)
        
        
    else:
        # Copy file to Not Processed folder
        shutil.copy(input_path, os.path.join(not_processed_folder, filename))
        print(f"Copied {filename} to {not_processed_folder}")


    if output_path:
        print(f"Processed {filename} and saved in {output_folder}")
        
    return metadata

# # Usage example
# folder_path = "/path/to/your/folder"  # Replace with your folder path
# # Define your extension lists here
# vector_extensions = ['.shp', '.geojson'] # and others
# raster_extensions = ['.tif', '.tiff'] # and others
# multitemporal_extensions = ['.hdf5', '.nc'] # and others
# lidar_extensions = ['.las', '.laz'] # and others
# compressed_raster_extensions = ['.zip', '.tar.gz'] # and others

# process_folder(folder_path, vector_extensions, raster_extensions, multitemporal_extensions, lidar_extensions, compressed_raster_extensions)
