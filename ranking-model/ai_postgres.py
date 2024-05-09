from keras.models import load_model
from dm_image import DMImageDataGenerator
from dm_keras_ext import DMAucModelCheckpoint
import os
import pydicom
import numpy as np
import cv2
import pandas as pd
from sqlalchemy import create_engine, text


def e2e_inference(images_dir):
    # Load pre-trained model
    print('Loading model...')
    model = load_model('inbreast_vgg16_512x1.h5')
    # Directory of dicom images
    print('Model loaded.')
    tmp_dir = 'tmp_png'

    # Read the DICOM file into png format
    for filename in os.listdir(images_dir):
        filepath = os.path.join(images_dir, filename)
        dicom_image = pydicom.dcmread(filepath)
        # Get the pixel array from the DICOM file
        pixel_array = dicom_image.pixel_array
        # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
        pixel_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))) * 255.0
        pixel_array = pixel_array.astype(np.uint8)
        # Save as PNG in the same directory
        png_filepath = os.path.join(tmp_dir, 'neg', filename + '.png')
        cv2.imwrite(png_filepath, pixel_array)

    test_imgen = DMImageDataGenerator(featurewise_center=True)

    print("\n==== Predicting on test set ====")
    test_generator = test_imgen.flow_from_directory(
        tmp_dir, target_size=[1152, 896], target_scale=None,
        rescale_factor=1,
        equalize_hist=False, dup_3_channels=True,
        classes=['neg', 'pos'], class_mode='categorical', batch_size=64,
        shuffle=False)
    test_samples = test_generator.nb_sample

    print('Starting processing...')
    for fnames, pred in DMAucModelCheckpoint.process_batch(test_generator, model, batch_size=64, test_samples=test_samples):
        dict_results = dict(zip(fnames, pred))
        data = {
        'study_uid': [],
        'model_1_result': [],
        'patient_name': []
        }
        for key, value in dict_results.items():
            study_uid = key.replace('neg/', '').replace('.png', '')

            dcm = pydicom.dcmread(os.path.join(images_dir, study_uid))
            print('Patient name:')
            print(dcm.PatientName)
            data['patient_name'].append(str(dcm.PatientName))

            os.remove(os.path.join(tmp_dir, 'neg', study_uid + '.png'))
            model_1_result = value[0]
            data['study_uid'].append(study_uid)
            data['model_1_result'].append(model_1_result)
        yield pd.DataFrame(data)

def get_db_engine():
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    hostname = os.environ.get('DB_HOSTNAME')
    port = os.environ.get('DB_PORT')
    database_name = os.environ.get('DB_NAME')
    connection_string = f"postgresql://{username}:{password}@{hostname}:{port}/{database_name}"
    return create_engine(connection_string)

def write_batch(df):
    engine = get_db_engine()
    primary_key_column = 'study_uid'
    primary_key_values = df[primary_key_column]

    print('Primary key values: ')
    print(primary_key_values)

    query = text(
        f"SELECT {primary_key_column} FROM birads_results WHERE {primary_key_column} IN :pk_values"
    )

    with engine.connect() as connection:
        existing_df = pd.read_sql(query, connection, params={'pk_values': tuple(primary_key_values)})

    new_rows = df.merge(existing_df, on=primary_key_column, how='left', indicator=True)
    new_rows_to_insert = new_rows[new_rows['_merge'] == 'left_only'].drop(columns=['_merge'])
    
    print('New rows: ')
    print(new_rows_to_insert)

    columns = list(new_rows_to_insert.columns)
    columns_str = ', '.join(columns)
    values_str = ', '.join([f":{col}" for col in columns])

    # Construct the native SQL insert statement
    insert_statement = text(
        f"INSERT INTO birads_results ({columns_str}) VALUES ({values_str})"
    )

    # Use native SQL to insert new rows into the database
    with engine.connect() as connection:
        with connection.begin():
            for index, row in new_rows_to_insert.iterrows():
                connection.execute(insert_statement, row.to_dict())
    print('Batch written.')    

def cron_job():
    for batch in e2e_inference("test_data"):
        write_batch(batch)

if __name__ == '__main__':
    cron_job()