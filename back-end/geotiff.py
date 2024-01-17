import os
import numpy as np
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
import h3  # Import the H3 library
import rtree  # Import the R-tree library


class GeoTIFFProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        self.processor_blip = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.model_blip = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        )
        logger.add("geotiff_processing_log.log", rotation="1 day")

    def extract_geospatial_info(self, dataset):
        # (unchanged)
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
        # (unchanged)
        try:
            dataset = gdal.Open(file_path)
            if dataset is None:
                logger.warning(f"Dataset is None for file: {file_path}")
                return None

            metadata = dataset.GetMetadata()
            proj = dataset.GetProjection()
            geotransform = dataset.GetGeoTransform()

            return {"metadata": metadata, "projection": proj, "geotransform": geotransform}
        except Exception as e:
            logger.error(f"Error in extract_metadata: {e}")
            return None

    def caption_image(self, image, conditional_text=None):
        # (unchanged)
        try:
            if conditional_text:
                inputs = self.processor_blip(image, conditional_text, return_tensors="pt")
            else:
                inputs = self.processor_blip(image, return_tensors="pt")

            out = self.model_blip.generate(**inputs)
            return self.processor_blip.decode(out[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error in caption_image: {e}")
            return None

    def process_file(self, filename, file_path):
        try:
            metadata = self.extract_metadata(file_path)

            with rasterio.open(file_path) as src:
                img = src.read()
                img = np.transpose(img, (1, 2, 0))
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

    def process_single_file(self, file_name, file_path):
        result = self.process_file(file_name, file_path)

        # Saving the result to a .pkl file in the user-specified output directory
        output_file_name = result["filename"].replace('.tif', '').replace('.tiff', '') + '.pkl'
        output_file_path = os.path.join(self.output_directory, output_file_name)
        with open(output_file_path, "wb") as outfile:
            pickle.dump(result, outfile)
        return result




# class GeoTIFFProcessor:
#     def __init__(self, input_directory, output_directory):
#         self.input_directory = input_directory
#         self.output_directory = output_directory
#         if not os.path.exists(self.output_directory):
#             os.makedirs(self.output_directory)

#         self.processor_blip = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
#         self.model_blip = BlipForConditionalGeneration.from_pretrained(
#             "Salesforce/blip-image-captioning-large"
#         )
#         logger.add("geotiff_processing_log.log", rotation="1 day")

#     def extract_geospatial_info(self, dataset):
#         """Extract geospatial information from the dataset."""
#         try:
#             geotransform = dataset.GetGeoTransform()
#             projection = osr.SpatialReference(wkt=dataset.GetProjection())

#             # Get the bounding box
#             width, height = dataset.RasterXSize, dataset.RasterYSize
#             minx = geotransform[0]
#             miny = geotransform[3] + width * geotransform[4] + height * geotransform[5]
#             maxx = geotransform[0] + width * geotransform[1] + height * geotransform[2]
#             maxy = geotransform[3]

#             # Center of the bounding box
#             centerx = (minx + maxx) / 2
#             centery = (miny + maxy) / 2

#             # Convert to lat/lon if not already
#             if projection.IsProjected():
#                 ct = osr.CoordinateTransformation(projection, projection.CloneGeogCS())
#                 centerx, centery, _ = ct.TransformPoint(centerx, centery)

#             return centerx, centery, (minx, miny, maxx, maxy)
#         except Exception as e:
#             logger.error(f"Error in extract_geospatial_info: {e}")
#             return None, None, None

#     def extract_metadata(self, file_path):
#         try:
#             dataset = gdal.Open(file_path)
#             if dataset is None:
#                 logger.warning(f"Dataset is None for file: {file_path}")
#                 return None

#             metadata = dataset.GetMetadata()
#             proj = dataset.GetProjection()
#             geotransform = dataset.GetGeoTransform()

#             return {"metadata": metadata, "projection": proj, "geotransform": geotransform}
#         except Exception as e:
#             logger.error(f"Error in extract_metadata: {e}")
#             return None

#     def caption_image(self, image, conditional_text=None):
#         try:
#             if conditional_text:
#                 inputs = self.processor_blip(image, conditional_text, return_tensors="pt")
#             else:
#                 inputs = self.processor_blip(image, return_tensors="pt")

#             out = self.model_blip.generate(**inputs)
#             return self.processor_blip.decode(out[0], skip_special_tokens=True)
#         except Exception as e:
#             logger.error(f"Error in caption_image: {e}")
#             return None

#     def process_file(self, filename):
#         file_path = os.path.join(self.input_directory, filename)
#         try:
#             metadata = self.extract_metadata(file_path)

#             with rasterio.open(file_path) as src:
#                 img = src.read()
#                 img = np.transpose(img, (1, 2, 0))  # Channels last for PIL Image
#                 pil_image = Image.fromarray(img)
#                 dataset = gdal.Open(file_path)
#                 centerx, centery, bbox = self.extract_geospatial_info(dataset)

#                 if centerx is not None and centery is not None:
#                     h3_index = h3.geo_to_h3(centery, centerx, resolution=9)
#                 else:
#                     h3_index = None


#             caption_conditional = self.caption_image(pil_image, "a photograph of")
#             caption_unconditional = self.caption_image(pil_image)

#             return {
#                 "filename": filename,
#                 "metadata": metadata,
#                 "h3_index": h3_index,
#                 "caption_conditional": caption_conditional,
#                 "caption_unconditional": caption_unconditional,
#             }
#         except Exception as e:
#             logger.error(f"Error processing {filename}: {e}")
#             return {
#                 "filename": filename,
#                 "metadata": None,
#                 "h3_index": None,
#                 "caption_conditional": None,
#                 "caption_unconditional": None,
#             }

#     def process_all_files(self):
#         with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
#             futures = [
#                 executor.submit(self.process_file, filename)
#                 for filename in os.listdir(self.input_directory)
#                 if filename.endswith((".tif", ".tiff"))
#             ]
#             results = [future.result() for future in futures]

#             # Saving each result to a .pkl file in the user-specified output directory
#             for result in results:
#                 output_file_name = result["filename"].replace('.tif', '').replace('.tiff', '') + '.pkl'
#                 output_file_path = os.path.join(self.output_directory, output_file_name)
#                 with open(output_file_path, "wb") as outfile:
#                     pickle.dump(result, outfile)

# input_directory = "/path/to/your/geotiff/files"
# output_directory = "/path/to/save/pkl/files"

# # Create an instance of the GeoTIFFProcessor class
# processor = GeoTIFFProcessor(input_directory, output_directory)

# # Process all GeoTIFF files in the input directory
# processor.process_all_files()
