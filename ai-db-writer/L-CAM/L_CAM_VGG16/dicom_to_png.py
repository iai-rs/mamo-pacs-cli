import os
import sys
import pydicom
import numpy as np
import cv2
from minio import Minio
from minio.error import S3Error
import re
import psycopg2
from psycopg2 import sql
import oci
import base64


db_params = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOSTNAME'),
    'port': os.environ.get('DB_PORT')
}


encoded_key_file = os.getenv("OCI_KEY_CONTENT")
decoded_key_file = base64.b64decode(encoded_key_file).decode('utf-8')

oci_config = {
    "user":os.getenv("OCI_USER"),
    "fingerprint":os.getenv("OCI_FINGERPRINT"),
    "tenancy":os.getenv("OCI_TENANCY"),
    "region":"eu-jovanovac-1",
    "key_content":decoded_key_file,
}

object_storage_client = oci.object_storage.ObjectStorageClient(oci_config)
oci_namespace = object_storage_client.get_namespace().data

# Name of postgres table for dicom metadata
table_name = 'dicom_metadata'


def get_attr(dicom, attr, default=' '):
    """ Retrieve an attribute from a DICOM image with a default if not present.
        Convert to string as database expects 'text'
    """
    value = getattr(dicom, attr, default)
    return str(value) if value != default else default


# Function to insert data into dicom_metadata table
def insert_dicom_metadata(table_name, mammography_id, patient_name, patient_id, acquisition_date, acquisition_time,
                          view, laterality, implant, manufacturer, manufacturer_model, institution):
    """ Extract dicom metadata and store to postgres database table """
    conn = None
    cursor = None

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Check if the study_id already exists
        cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM {table} WHERE mammography_id = %s)").format(
            table=sql.Identifier(table_name)), (mammography_id,))
        exists = cursor.fetchone()[0]

        if exists:
            print(f"mammography_id {mammography_id} already exists in the table {table_name}. No data inserted.")
        else:
            # Define the insert statement
            insert_query = sql.SQL("""
                INSERT INTO {table} (mammography_id, patient_name, patient_id, acquisition_date, acquisition_time,
                          view, laterality, implant, manufacturer, manufacturer_model, institution)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """).format(table=sql.Identifier(table_name))

            # Execute the insert statement
            cursor.execute(insert_query, (mammography_id, patient_name, patient_id, acquisition_date, acquisition_time,
                                          view, laterality, implant, manufacturer, manufacturer_model, institution))

            # Commit the transaction
            conn.commit()

            print(f"Data for mammography_id {mammography_id} successfully inserted into {table_name}.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def print_directory_structure(start_path, indent_level=0):
    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)
        print('    ' * indent_level + '|-- ' + item)
        if os.path.isdir(item_path):
            print_directory_structure(item_path, indent_level + 1)

def write_oracle_s3(bucket_name, png_filepath, png_image):
    # TODO: Add check if file is already uploaded
    print("************************* Print directory structure from write to s3")
    print_directory_structure(".")
    print(f"Saving to oracle s3: {png_filepath}")
    with open(png_filepath, 'rb') as file_stream:
        response = object_storage_client.put_object(
            namespace_name=oci_namespace,
            bucket_name=bucket_name,
            object_name=png_filepath,
            put_object_body=file_stream
        )
        print(f"Saved to oracle s3: {png_filepath}")
        print(response.__dict__)

def write_minio(bucket_name, png_filepath, png_image):
        print("************************* Print directory structure from write to minio")
        print_directory_structure(".")
        # Save to minio
        client = Minio(f"{os.environ.get('MINIO_HOST')}:{os.environ.get('MINIO_PORT')}",
                       access_key="minioadmin",
                       secret_key="m]7N1//[#,tj6J",
                       secure=False
                       )
        try:  # Check if .png file has already been uploaded
            # Try to get the object's metadata
            client.stat_object(bucket_name, png_image)
            print(f"Object '{png_image}' already exists in firstbucket. Skipping upload.")
        except S3Error as e:
            # If the object does not exist, an exception is thrown
            if e.code == 'NoSuchKey':
                # Object does not exist, proceed with upload
                try:
                    result = client.fput_object(bucket_name, png_image, png_filepath)
                    print(f"Uploaded object {png_image}, etag: {result.etag}")
                except S3Error as err:
                    print(f"Failed to upload object {png_image} due to: {err}")
            else:
                # Other S3 errors
                print(f"Error occurred: {e}")

        # Remove the locally saved .png image
        os.remove(png_filepath)

def png_to_minio(dicom_folder, tmp_png_folder):
    """ Load dicom image, convert to .png format and store in minio server (if it is not already there)
        Once the image is processed, add corresponding metadata to the sql table (using insert_dicom_metadata function)
    :param dicom_folder: path to dicom folder
    """

    for filename in os.listdir(dicom_folder):
        dicom_path = os.path.join(dicom_folder, filename)
        dicom_image = pydicom.dcmread(dicom_path)
        # Get the pixel array from the DICOM file
        pixel_array = dicom_image.pixel_array
        # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
        pixel_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))) * 255.0
        pixel_array = pixel_array.astype(np.uint8)
        # Define path for .png image
        png_image = os.path.basename(dicom_path)
        png_image = re.sub(r'\.(dcm|dicom)$', '', png_image)
        png_image = png_image + '.png'  # image name
        png_filepath = os.path.join(tmp_png_folder, png_image)  # image path
        # Save .png image locally
        print(f"Saving image to path: {png_filepath}")
        response = cv2.imwrite(png_filepath, pixel_array)
        print(response)

        write_oracle_s3('bucket-aimambo-images', png_filepath, pixel_array)
        write_minio('firstbucket', png_filepath, png_image)

        # Add metadata info to table. Not all dicom have all the data (default = ' ')
        dcm_study_id = re.sub(r'\.(dcm|dicom)$', '', os.path.basename(dicom_path))
        insert_dicom_metadata(
            table_name,
            dcm_study_id,
            get_attr(dicom_image, 'PatientName', None),
            get_attr(dicom_image, 'PatientID', None),
            get_attr(dicom_image, 'StudyDate', None),
            get_attr(dicom_image, 'StudyTime', None),
            get_attr(dicom_image, 'ViewPosition', None),  # Could be missing
            get_attr(dicom_image, 'ImageLaterality', None),  # Could be missing
            get_attr(dicom_image, 'BreastImplantPresent', None),  # Custom default value
            get_attr(dicom_image, 'Manufacturer', None),
            get_attr(dicom_image, 'ManufacturerModelName', None),
            get_attr(dicom_image, 'InstitutionName', None)
        )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        png_to_minio(sys.argv[1])
    else:
        print("Please provide dicom folder path.")
