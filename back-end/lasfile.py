import os
import laspy
import numpy as np
import geopandas as gpd
import h3
from shapely.geometry import Point
from rtree import index as rtree_index
import pickle
from concurrent.futures import ProcessPoolExecutor

# class LasFileProcessor:
    # def __init__(self, las_files_directory, output_directory):
    #     self.las_files_directory = las_files_directory
    #     self.output_directory = output_directory

    # def extract_metadata(self, las):
    #     metadata = {
    #         "point_format": las.header.point_format.id,
    #         "number_of_points": las.header.point_count,
    #         "scale_factors": las.header.scale,
    #         "offsets": las.header.offset,
    #         "min_bounds": las.header.min,
    #         "max_bounds": las.header.max,
    #     }
    #     return metadata

    # def read_las_file(self, las_file_path):
    #     try:
    #         las = laspy.read(las_file_path)
    #         coords = np.vstack((las.x, las.y, las.z)).transpose()
    #         attributes = {"intensity": las.intensity, "classification": las.classification}
    #         metadata = self.extract_metadata(las)
    #         return coords, attributes, metadata, True
    #     except Exception as e:
    #         print(f"Error reading {las_file_path}: {e}")
    #         return None, None, None, False

    # def create_geospatial_index(self, coords, attributes, metadata):
    #     gdf = gpd.GeoDataFrame(attributes, geometry=[Point(xyz) for xyz in coords])
    #     for key, value in metadata.items():
    #         gdf[key] = value

    #     gdf["h3_index"] = gdf.apply(
    #         lambda row: h3.geo_to_h3(row.geometry.y, row.geometry.x, 7), axis=1
    #     )

    #     # Create R-tree index
    #     rtree_idx = rtree_index.Index()
    #     for idx, row in gdf.iterrows():
    #         rtree_idx.insert(idx, row.geometry.bounds)

    #     return gdf, rtree_idx

    # def process_las_file(self, las_file_path):
    #     coords, attributes, metadata, success = self.read_las_file(las_file_path)
    #     if success:
    #         geospatial_index, rtree_idx = self.create_geospatial_index(coords, attributes, metadata)
    #         return las_file_path, geospatial_index, rtree_idx
    #     else:
    #         return las_file_path, None, None

#     def process_all_files(self):
#         las_files = [
#             os.path.join(self.las_files_directory, f)
#             for f in os.listdir(self.las_files_directory)
#             if f.endswith(".las")
#         ]

#         with ProcessPoolExecutor() as executor:
#             results = executor.map(self.process_las_file, las_files)

#         for las_file, geospatial_index, rtree_idx in results:
#             if geospatial_index is not None and rtree_idx is not None:
#                 output_file = os.path.join(
#                     self.output_directory, os.path.basename(las_file).replace('.las', '') + ".pkl"
#                 )
#                 with open(output_file, "wb") as outfile:
#                     pickle.dump((geospatial_index, rtree_idx), outfile)
#                 print(f"Processed and saved {las_file} as {output_file}.")
#             else:
#                 print(f"Failed to process {las_file}.")



# # las_files_directory = "path/to/your/las/files"  # Update this path
# # output_directory = "path/to/save/output"  # Update this path
# # processor = LasFileProcessor(las_files_directory, output_directory)
# # processor.process_all_files()


class LasFileProcessor:
    # (unchanged)
    def __init__(self, las_files_directory, output_directory):
        self.las_files_directory = las_files_directory
        self.output_directory = output_directory

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
            attributes = {"intensity": las.intensity, "classification": las.classification}
            metadata = self.extract_metadata(las)
            return coords, attributes, metadata, True
        except Exception as e:
            print(f"Error reading {las_file_path}: {e}")
            return None, None, None, False

    def create_geospatial_index(self, coords, attributes, metadata):
        gdf = gpd.GeoDataFrame(attributes, geometry=[Point(xyz) for xyz in coords])
        for key, value in metadata.items():
            gdf[key] = value

        gdf["h3_index"] = gdf.apply(
            lambda row: h3.geo_to_h3(row.geometry.y, row.geometry.x, 7), axis=1
        )

        # Create R-tree index
        rtree_idx = rtree_index.Index()
        for idx, row in gdf.iterrows():
            rtree_idx.insert(idx, row.geometry.bounds)

        return gdf, rtree_idx

    def process_las_file(self, las_file_path):
        coords, attributes, metadata, success = self.read_las_file(las_file_path)
        if success:
            geospatial_index, rtree_idx = self.create_geospatial_index(coords, attributes, metadata)
            return las_file_path, geospatial_index, rtree_idx
        else:
            return las_file_path, None, None

    def process_single_file(self, las_file_path):
        las_file = os.path.basename(las_file_path)
        geospatial_index, rtree_idx = self.process_las_file(las_file_path)
        if geospatial_index is not None and rtree_idx is not None:
            output_file = os.path.join(
                self.output_directory, las_file.replace('.las', '') + ".pkl"
            )
            return (geospatial_index, rtree_idx)
            with open(output_file, "wb") as outfile:
                pickle.dump((geospatial_index, rtree_idx), outfile)
            print(f"Processed and saved {las_file} as {output_file}.")
        else:
            print(f"Failed to process {las_file}.")

# # Example usage for processing a single LAS file
# las_files_directory = "path/to/your/las/files"  # Update this path
# output_directory = "path/to/save/output"  # Update this path
# processor = LasFileProcessor(las_files_directory, output_directory)

# # Specify the LAS file you want to process
# las_file_to_process = "your_specific_file.las"  # Update this filename
# processor.process_single_file(os.path.join(las_files_directory, las_file_to_process))
