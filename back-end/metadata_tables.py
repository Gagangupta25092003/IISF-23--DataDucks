from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Common_Metadata(db.Model):
    __tablename__ = 'common_metadata'
    file_location = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(255))
    file_size = db.Column(db.String(50))
    file_type = db.Column(db.String(50))
    creation_date = db.Column(db.String(50))
    source = db.Column(db.String(50))
    description = db.Column(db.String(255))
    additional_info = db.Column(db.String(50))
    
    def __init__(self, name, file_size, file_location, creation_date, file_type, source, description, additional_info):
        self.name = name
        self.file_size = file_size
        self.file_location = file_location
        self.creation_date = creation_date
        self.file_type = file_type
        self.source = source
        self.description = description 
        self.additional_info = additional_info
        
class Geojson_Metadata(db.Model):
    __tablename__ = 'geojson_metadata'
    file_location = db.Column(db.String(100), primary_key=True)
    area = db.Column(db.String(255))
    length = db.Column(db.String(50))
    bounding_box = db.Column(db.String(50))
    h3_index = db.Column(db.String(50))
    
    def __init__(self, file_location, area, length, bounding_box, h3_index):
        self.file_location = file_location
        self.area = area
        self.length = length
        self.bounding_box = bounding_box
        self.h3_index = h3_index 
   
class Tiff_Metadata(db.Model):
    __tablename__ = 'tiff_metadata'
    file_location = db.Column(db.String(100), primary_key=True)
    projection = db.Column(db.String(255))
    geotransform = db.Column(db.String(50))
    centerx = db.Column(db.String(50))
    centery = db.Column(db.String(50))
    bounding_box = db.Column(db.String(50))
    caption_conditional = db.Column(db.String(255))
    caption_unconditional = db.Column(db.String(50))
    
    def __init__(self, geotransform, projection, file_location, centerx, centery, caption_conditional, caption_unconditional, bounding_box):
        self.geotransform = geotransform
        self.projection = projection
        self.file_location = file_location
        self.centerx = centerx
        self.centery = centery
        self.bounding_box = bounding_box
        self.caption_conditional = caption_conditional 
        self.caption_unconditional = caption_unconditional     

class Las_Metadata(db.Model):
    __tablename__ = 'las_metadata'
    file_location = db.Column(db.String(100), primary_key=True)
    point_format = db.Column(db.String(255))
    number_of_points = db.Column(db.String(50))
    scale_factors = db.Column(db.String(50))
    offsets = db.Column(db.String(50))
    min_bounds = db.Column(db.String(50))
    max_bounds = db.Column(db.String(50))
    
    def __init__(self, file_location, area, number_of_points, offsets, min_bounds, scale_factors, max_bounds):
        self.file_location = file_location
        self.area = area
        self.number_of_points = number_of_points
        self.scale_factors = scale_factors
        self.offsets = offsets 
        self.min_bounds = min_bounds 
        self.max_bounds = max_bounds 
        
  