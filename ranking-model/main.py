from keras.models import load_model
from dm_image import DMImageDataGenerator
from dm_keras_ext import DMAucModelCheckpoint
import os
import pydicom
import numpy as np
import cv2
import pandas as pd
from sqlalchemy import create_engine


def e2e_inference(images_dir):
    # Load pre-trained model
    model = load_model('inbreast_vgg16_512x1.h5')
    # Directory of dicom images

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
    _, dict_results = DMAucModelCheckpoint.calc_test_auc(
        test_generator, model, test_samples=test_samples)

    data = {
        'study_uid': [],
        'model_1_result': []
    }

    for key, value in dict_results.items():
        study_uid = key.replace('neg/', '')
        model_1_result = value[0]
        data['study_uid'].append(study_uid)
        data['model_1_result'].append(model_1_result)
            
    return data

def cron_job():
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    hostname = os.environ.get('DB_HOSTNAME')
    port = os.environ.get('DB_PORT')
    database_name = os.environ.get('DB_NAME')

    data = e2e_inference("data")
    df = pd.DataFrame(data)

    connection_string = f"postgresql://{username}:{password}@{hostname}:{port}/{database_name}"
    engine = create_engine(connection_string)
    df.to_sql('birads_results', con=engine, if_exists='append', index=False)
    print('Written to DB.')

if __name__ == '__main__':
    cron_job()