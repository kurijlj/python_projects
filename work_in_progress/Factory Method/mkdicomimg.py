import datetime

import pydicom
import pydicom.uid as uid
from pydicom.dataset import FileDataset, FileMetaDataset

import numpy as np
from skimage.draw import disk, ellipse

# Constants --------------------------------------------------------------------
HU = {
    "AIR": -1000,
    "BLOOD": 30,
    "BONE": 1000,
    "BRAIN": 30,
    "CS_FLUID": 15,  # Cerebrospinal fluid
    "DERMIS": 37,
    "FAT": -100,
    "FIDUCIAL": 1000,  # Fiducial marker
    "GREY_MATTER": 43,
    "KIDNEY": 30,
    "LIVER": 50,
    "LUNG": -500,
    "MUSCLE": 40,
    "SC_FAT": -100,  # Subcutaneous fat
    "SKIN": 37,
    "WATER": 0,
    "WHITE_MATTER": 46
}

# Phantom structures -----------------------------------------------------------
# Phantom structures are defined as a list of tuples. Each tuple contains the
# following elements:
#   1. The name of the structure
#   4. The dimensions of the structure in mm (width, height, length)
#   5. The location of the structure regarding to the FoV center in mm (x, y, z)
#   6. The orientation of the structure in degrees
#   7. The material of the structure
PHANTOM = {
    "FOV": (256.0, 256.0, 256.0, 0.0, 0.0, 0.0, 0.0, "air"),
    "DERMIS": (160.0, 200.0, 230.0,
               0.0, 0.0, 0.0, 0.0, "dermis"),  # 4.0 mm
    "SC_FAT": (156.0, 196.0, 230.0,
               0.0, 0.0, 0.0, 0.0, "subcutaneous fat"),  # 6.0 mm
    "SKULL_BONE": (150.0, 190.0, 230.0,
                   0.0, 0.0, 0.0, 0.0, "bone"),  # 8.0 mm
    "GREY_MATTER": (142.0, 182.0, 230.0,
                    0.0, 0.0, 0.0, 0.0, "grey matter"),  # 2.5 mm
    "WHITE_MATTER": (139.5, 179.5, 230.0, 0.0, 0.0, 0.0, 0.0, "white matter"),
    "RIGHT_VENTRICLE": (35.0, 80.0, 230.0,
                        -20.0, -20.0, 0.0, 20.0, "cerebrospinal fluid"),
    "LEFT_VENTRICLE": (30.0, 70.0, 230.0,
                       -20.0, 20.0, 0.0, -20.0, "cerebrospinal fluid"),
    "BRAIN_STEM": (40.0, 40.0, 230.0, 40.0, 0.0, 0.0, 0.0, "grey matter"),
    "FIDUCIAL_SUP": (1.0, 1.0, 2.0, 0.0, 0.0, 117.0, 0.0, "fiducial superior"),
    "FIDUCIAL_INF": (1.0, 1.0, 2.0, 0.0, 0.0, -117.0, 0.0, "fiducial inferior"),
    "FIDUCIAL_R": (1.0, 1.0, 2.0, 0.0, -82.0, 0.0, 0.0, "fiducial right"),
    "FIDUCIAL_L": (1.0, 1.0, 2.0, 0.0, 82.0, 0.0, 0.0, "fiducial left"),
    "FIDUCIAL_ANT": (1.0, 1.0, 2.0, 102.0, 0.0, 0.0, 0.0, "fiducial anterior"),
    "FIDUCIAL_POST": (1.0, 1.0, 2.0,
                      -102.0, 0.0, 0.0, 0.0, "fiducial posterior")
}

def struct_to_pixelmap(
        rows: int,
        cols: int,
        strct: tuple[float, float, float, float, float, float, float, str],
        ps: tuple[float, float],
        st: float,
        sl: float
        ) -> np.ndarray[int]:
    if(strct[5] - strct[2]/2 <= sl*st and sl*st <= strct[5] + strct[2]/2):
        rr, cc = ellipse(
            round((rows / 2) + (strct[3] / ps[0])),  # Center row
            round((cols / 2) + (strct[4] / ps[1])),  # Center column
            round(strct[1] / (2 * ps[1])),  # Radius row
            round(strct[0] / (2 * ps[0])),  # Radius column
            shape=(rows, cols),
            rotation=np.deg2rad(strct[6])
            )
        return rr, cc

    else:
        return None, None

# Input data -------------------------------------------------------------------

# Depends on the Institution
manufacturer = "GammaPhysics"
institution_name = "University Clinical Center of Serbia NSC"
institution_address = "Dr Koste Todorovica 4, Belgrade, Serbia"
station_name = "G15 Dosimetry"
institutional_department_name = "Gamma Knife"

# Depends on the software
software_versions = "0.1.0"

# Depends on the study
study_accession_number = "1"
study_description = "Image Registration QC Synthetic CT"

# Depends on the modality
frame_of_reference_uid = uid.PYDICOM_IMPLEMENTATION_UID + ".101"
pixel_spacing = (0.5, 0.5)
photometric_interpretation = "MONOCHROME2"
rows = 512
columns = 512

# Depends on the series
series_number = 1
series_description = "Reference Series"
position_reference_indicator = "PHANTOM_CENTER"
image_type = "ORIGINAL\\PRIMARY\\AXIAL"
images_in_acquisition = 1
slice_thickness = 1.0

# Calculate slice locations ----------------------------------------------------
slice_locations = np.arange(
    round(-128.0 / slice_thickness) * slice_thickness,
    round(128.0 / slice_thickness) * slice_thickness + slice_thickness,
    slice_thickness
    )

# Depends on the image
instance_number = 1
slice_location = 119.0
filename = "test6.dcm"

# Popultae SOP Common attributes -----------------------------------------------
file_meta = FileMetaDataset()
file_meta.MediaStorageSOPClassUID = uid.UID(uid.CTImageStorage)
file_meta.MediaStorageSOPInstanceUID = uid.UID(uid.generate_uid())
file_meta.ImplementationClassUID = uid.UID(uid.PYDICOM_IMPLEMENTATION_UID)
# file_meta.TransferSyntaxUID = uid.ExplicitVRLittleEndian

# Create the FileDataset instance (initially no data elements, but file_meta
# supplied)
ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)

# Populate Patient attributes --------------------------------------------------
ds.PatientName = "Synthetic^Phantom"
ds.PatientID = "123456"
ds.TypeOfPatientID = "TEXT"
ds.PatientSpeciesDescription = "PHANTOM"
ds.PatientBirthDate = "19000101"
ds.PatientSex = "O"
ds.QualityControlSubject = "YES"

# Populate General Study attributes --------------------------------------------
ds.StudyInstanceUID = uid.generate_uid()
dt = datetime.datetime.now()
ds.StudyDate = dt.strftime('%Y%m%d')
ds.StudyTime = dt.strftime('%H%M%S.%f')
ds.ReferringPhysicianName = "Dr. Who"
ds.StudyID = dt.strftime("%Y%m%d%H%M%S")  # Use the current date/time as
                                          # the study ID
ds.AccessionNumber = study_accession_number
ds.StudyDescription = study_description

# Populate General Series attributes -------------------------------------------
ds.Modality = "CT"
ds.SeriesInstanceUID = uid.generate_uid()
ds.SeriesNumber = series_number
dt = datetime.datetime.now()  # Update to current time
ds.SeriesDate = dt.strftime('%Y%m%d')
ds.SeriesTime = dt.strftime('%H%M%S.%f')
ds.SeriesDescription = series_description
ds.BodyPartExamined = "HEAD"
ds.PatientPosition = "HFS"

# Populate Frame of Reference attributes ---------------------------------------
ds.FrameOfReferenceUID = frame_of_reference_uid
ds.PositionReferenceIndicator = position_reference_indicator

# Populate General Equipment attributes ----------------------------------------
ds.Manufacturer = manufacturer
ds.InstitutionName = institution_name
ds.InstitutionAddress = institution_address
ds.StationName = station_name
ds.InstitutionalDepartmentName = institutional_department_name
ds.SoftwareVersions = software_versions

# Populate General Image attributes --------------------------------------------
ds.InstanceNumber = instance_number
ds.PatientOrientation = "L\\P"
dt = datetime.datetime.now()
ds.ContentDate = dt.strftime('%Y%m%d')
ds.ContentTime = dt.strftime('%H%M%S.%f')  # long format with micro seconds
ds.ImageType = image_type
ds.AcquisitionNumber = ds.InstanceNumber
ds.AcquisitionDate = ds.ContentDate
ds.AcquisitionTime = ds.ContentTime
ds.ImagesInAcquisition = images_in_acquisition

# Populate Image Plane attributes ----------------------------------------------
ds.PixelSpacing = "{0}\\{1}".format(pixel_spacing[0], pixel_spacing[1])
ds.ImageOrientationPatient = "1.0\\0.0\\0.0\\0.0\\1.0\\0.0"  # NOTE: ?
ds.ImagePositionPatient = "-256.0\\-256.0\\000.0"  # NOTE: Changes with
                                                   #       each image
ds.ImagePositionPatient = "{0}\\{1}\\{2}".format(
    -columns * pixel_spacing[0] / 2,
    -rows * pixel_spacing[1] / 2,
    slice_location * slice_thickness
    )
ds.SliceThickness = "{0}".format(slice_thickness)
ds.SliceLocation = "{0}".format(slice_location)

# Populate Image Pixel attributes ----------------------------------------------
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = photometric_interpretation
ds.Rows = rows
ds.Columns = columns
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0

# Populate CT Image attributes -------------------------------------------------
ds.RescaleIntercept = "-1000"
ds.RescaleSlope = "1"
ds.RescaleType = "HU"
ds.ConvolutionKernel = "STANDARD"
ds.WindowCenter = "40"
ds.WindowWidth = "400"

# Populate pixel data elements -------------------------------------------------
pixel_data = np.zeros((columns, rows), dtype=np.uint16)

# Draw the outer phantom contour (simulate dermis)
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["DERMIS"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["DERMIS"] + 1000
# Draw the subcutaneous fat
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["SC_FAT"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["SC_FAT"] + 1000
# Draw the skull bone
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["SKULL_BONE"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["BONE"] + 1000
# Draw the grey matter
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["GREY_MATTER"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["GREY_MATTER"] + 1000
# Draw the white matter
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["WHITE_MATTER"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["WHITE_MATTER"] + 1000
# Draw the right ventricle
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["RIGHT_VENTRICLE"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["CS_FLUID"] + 1000
# Draw the left ventricle
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["LEFT_VENTRICLE"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["CS_FLUID"] + 1000
# Draw the brain stem
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["BRAIN_STEM"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr, cc] = HU["GREY_MATTER"] + 1000
# Draw the fiducial superior
rr, cc = struct_to_pixelmap(
                            rows,
                            columns,
                            PHANTOM["FIDUCIAL_SUP"],
                            pixel_spacing,
                            slice_thickness,
                            slice_location
                           )
if(rr is not None and cc is not None):
    pixel_data[rr[0], cc[0]] = HU["BONE"] + 1000

ds.PixelData = pixel_data.tobytes()

# Set the transfer syntax ------------------------------------------------------
ds.is_little_endian = True
ds.is_implicit_VR = True

print("Writing test file", filename)
ds.save_as(filename, write_like_original=False)
print("File saved.")