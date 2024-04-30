import pydicom
import math
from PIL import Image
import numpy as np
import pandas as pd
import shutil
import os
import cv2
from preprocess import preprocess_scan


def import_images_blind_db():
    # Change these paths to the actual paths on your system
    xsl_file_path = 'D:\\Mammography\\blind_db\\blind_db.xlsx'
    source_files_directory = 'D:\\Mammography\\blind_db\\Imagebox'
    neg_directory = 'test_files\\neg'
    pos_directory = 'test_files\\pos'

    # Read the .xsl file
    df = pd.read_excel(xsl_file_path, engine='openpyxl')

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        birads_patient = row['birads_patient']
        birads_image = row['birads_image']
        patient = row['patient_id']
        image = row['image_id']

        path = source_files_directory + "\\" + str(patient)
        path_image = path + "\\" + str(image) + ".dcm"

        if birads_image == 2:
            shutil.copy2(path_image, neg_directory)
            print(f"Copied {path_image} to {neg_directory}")

        if birads_image in ['4a','4b',5]:
            shutil.copy2(path_image, pos_directory)
            print(f"Copied {path_image} to {pos_directory}")


def import_images_vindr():
    # Change these paths to the actual paths on your system
    xsl_file_path = 'D:\\Mammography\\VinDr\\vindr-mammo-1.0.0\\finding_annotations.csv'
    source_files_directory = 'D:\\Mammography\\VINDR\\vindr-mammo-1.0.0\\images'
    neg_directory = 'test_files\\neg'
    pos_directory = 'test_files\\pos'

    max_neg = 400000
    max_pos = 400000
    cnt_neg = 0
    cnt_pos = 0

    # Read the .xsl file
    df = pd.read_csv(xsl_file_path)

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        birads_finding = row['finding_birads']
        birads_breast = row['breast_birads']
        patient = row['study_id']
        image = row['image_id']

        path = source_files_directory + "\\" + str(patient)
        path_image = path + "\\" + str(image) + ".dicom"
        print(cnt_neg+cnt_pos)
        if cnt_pos >= max_pos and cnt_neg >= max_neg:
            break

        if birads_breast in ["BI-RADS 1", "BI-RADS 2"] and math.isnan(birads_finding) and cnt_neg <= max_neg:
            cnt_neg += 1
            # shutil.copy2(path_image, neg_directory)
            # print(f"Copied {path_image} to {neg_directory}")
            # filepath = os.path.join(neg_directory, str(image) + ".dicom")
            filepath = os.path.join(neg_directory, str(image) + ".png")
            if not os.path.isfile(filepath):
                print("yo")

        elif birads_breast in ["BI-RADS 3", "BI-RADS 4", "BI-RADS 5"] and cnt_pos <= max_pos:
            cnt_pos += 1
            # shutil.copy2(path_image, pos_directory)
            # print(f"Copied {path_image} to {pos_directory}")
            # filepath = os.path.join(pos_directory, str(image) + ".dicom")
            filepath = os.path.join(pos_directory, str(image) + ".png")
            if not os.path.isfile(filepath):
                print("yo")
        else:
            print("yo")

        # Read the DICOM file
        # dicom_image = pydicom.dcmread(filepath)
        # # Get the pixel array from the DICOM file
        # pixel_array = dicom_image.pixel_array
        # # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
        # pixel_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))) * 255.0
        # pixel_array = pixel_array.astype(np.uint8)
        #
        # # Preprocess the image (negate and flip if necessary, crop borders, etc.)
        # # pixel_array, spatial = preprocess_scan(pixel_array)
        # # Save as PNG in the same directory
        # png_filepath = filepath.replace('.dcm', '.png').replace('.dicom', '.png')
        # cv2.imwrite(png_filepath, pixel_array)
        # print(f"Converted and saved {png_filepath}")
        # os.remove(filepath)

def import_images_rsna_per_breast():
    # Change these paths to the actual paths on your system
    xsl_file_path = 'D:\\Mammography\\RSNA\\train.csv'
    source_files_directory = 'D:\\Mammography\\RSNA\\train_images'
    neg_directory = 'D:\\Mammography\\test_files\\neg'
    pos_directory = 'D:\\Mammography\\test_files\\pos'

    max_cnt = 15000
    cnt = 0

    # Read the .xsl file
    df = pd.read_csv(xsl_file_path)
    # filter to find occurrences of patients with exactly 2 left or 2 right scans with same birads
    filtered_df = df.groupby(['patient_id', 'BIRADS', 'laterality']).filter(lambda x: len(x) == 2)
    # save new dataframe
    filtered_df.to_csv('rsna_per_breast.csv')

    # Iterate over the rows of the DataFrame
    for index, row in filtered_df.iterrows():
        patient = row['patient_id']
        image = row['image_id']
        cancer = row['cancer']

        path = source_files_directory + "\\" + str(patient)
        path_image = path + "\\" + str(image) + ".dcm"

        if cnt >= max_cnt:
            break

        cnt += 1
        if cancer == 0:
            shutil.copy2(path_image, neg_directory)
            print(f"Copied {path_image} to {neg_directory}")
        else:
            shutil.copy2(path_image, pos_directory)
            print(f"Copied {path_image} to {pos_directory}")


def import_images_rsna():
    # Change these paths to the actual paths on your system
    xsl_file_path = 'rsna_train.csv'
    source_files_directory = 'D:\\Mammography\\RSNA\\train_images'
    neg_directory = 'D:\\Mammography\\test_files\\neg'
    pos_directory = 'D:\\Mammography\\test_files\\pos'

    max_neg = 300
    max_pos = 300
    cnt_neg = 0
    cnt_pos = 0

    # Read the .xsl file
    df = pd.read_csv(xsl_file_path)

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        biopsy = int(row['biopsy'])
        cancer = int(row['cancer'])
        birads = row['BIRADS']
        patient = row['patient_id']
        image = row['image_id']

        path = source_files_directory + "\\" + str(patient)
        path_image = path + "\\" + str(image) + ".dcm"

        # if cnt_pos >= max_pos and cnt_neg >= max_neg:
        #     break
        shutil.copy2(path_image, neg_directory)
        print(f"Copied {path_image} to {neg_directory}")

        # Read the DICOM file
        filepath = os.path.join(neg_directory, str(image)+".dcm")
        dicom_image = pydicom.dcmread(filepath)

        # Get the pixel array from the DICOM file
        pixel_array = dicom_image.pixel_array

        # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
        pixel_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))) * 255.0
        pixel_array = pixel_array.astype(np.uint8)

        # Preprocess the image (negate and flip if necessary, crop borders, etc.)
        # pixel_array, spatial = preprocess_scan(pixel_array)

        # Save as PNG in the same directory
        png_filepath = filepath.replace('.dcm', '.png').replace('.dicom', '.png')
        cv2.imwrite(png_filepath, pixel_array)
        print(f"Converted and saved {png_filepath}")

        os.remove(filepath)


        # if biopsy == 1 and cancer == 0 and cnt_neg <= max_neg:
        #     cnt_neg += 1
        #     shutil.copy2(path_image, neg_directory)
        #     print(f"Copied {path_image} to {neg_directory}")
        #
        # elif biopsy == 1 and cancer == 1 and cnt_pos <= max_pos:
        #     cnt_pos += 1
        #     shutil.copy2(path_image, pos_directory)
        #     print(f"Copied {path_image} to {pos_directory}")

        # if biopsy == 1 and cancer == 0:
        #     for item in os.listdir(path):
        #         path_file = os.path.join(path, item)
        #         shutil.copy2(path_file, neg_directory)
        #         print(f"Copied {path_file} to {neg_directory}")
        # elif biopsy == 1 and cancer == 1:
        #     for item in os.listdir(path):
        #         path_file = os.path.join(path, item)
        #         shutil.copy2(path_file, pos_directory)
        #         print(f"Copied {path_file} to {pos_directory}")


def import_images_inbreast():
    # Change these paths to the actual paths on your system
    xsl_file_path = 'C:\\Users\\Korisnik\\Documents\\IVI\\Mamografija\\INbreast_Release_1.0\\INbreast.xls'
    source_files_directory = 'C:\\Users\\Korisnik\\Documents\\IVI\\Mamografija\\INbreast_Release_1.0\\AllDICOMs'
    neg_directory = 'test_files\\neg'
    pos_directory = 'test_files\\pos'

    # Read the .xsl file
    df = pd.read_excel(xsl_file_path)

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        bi_rads = row['Bi-Rads']
        file_name_partial = int(row['File Name'])

        # Find all files in the source directory that start with file_name_partial
        matching_files = [f for f in os.listdir(source_files_directory) if f.startswith(str(file_name_partial))]

        for file_name in matching_files:
            source_file_path = os.path.join(source_files_directory, file_name)

            # Check if the file exists in the source directory
            if not os.path.exists(source_file_path):
                print(f"File not found: {source_file_path}")
                continue

            # Copy files based on BI-rads value
            if bi_rads in [1]:
                shutil.copy(source_file_path, neg_directory)
                print(f"Copied {file_name} to {neg_directory}")
            elif bi_rads in [5, 6]:
                shutil.copy(source_file_path, pos_directory)
                print(f"Copied {file_name} to {pos_directory}")


def convert_dcm_to_png(directory):
    for filename in os.listdir(directory):
        if filename.endswith(('.dcm', '.dicom')):
            # Read the DICOM file
            filepath = os.path.join(directory, filename)
            dicom_image = pydicom.dcmread(filepath)

            # Get the pixel array from the DICOM file
            pixel_array = dicom_image.pixel_array

            # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
            pixel_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))) * 255.0
            pixel_array = pixel_array.astype(np.uint8)

            # Preprocess the image (negate and flip if necessary, crop borders, etc.)
            # pixel_array, spatial = preprocess_scan(pixel_array)

            # Save as PNG in the same directory
            png_filepath = filepath.replace('.dcm', '.png').replace('.dicom', '.png')
            cv2.imwrite(png_filepath, pixel_array)
            print(f"Converted and saved {png_filepath}")


def calc_mean_std():
    image_directories = ["test_files/neg", "test_files/pos"]
    image_files = []

    # Collect all image files from each directory
    for directory in image_directories:
        image_files.extend([os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.png')])

    # List to store all image data
    image_data = []
    target_size = (1152, 896)

    for image_file in image_files:
        try:
            with Image.open(image_file) as img:
                # Resize image
                img_resized = img.resize(target_size)
                img_array = np.array(img_resized)
                image_data.append(img_array)
        except Exception as e:
            print(f"Error loading image {image_file}: {e}")

    if image_data:
        all_images = np.stack(image_data)

        mean = np.mean(all_images)
        std = np.std(all_images)

        print("Mean: ", mean)
        print("Standard Deviation: ", std)
    else:
        print("No images were loaded successfully.")


def examine_csv(csv):
    df = pd.read_csv(csv)
    # Task 1: Number of unique patients
    unique_patient_ids = df['patient_id'].nunique()
    print(f"Number of patients (unique patient_id values): {unique_patient_ids}")

    # Task 2: Count the occurrences of each unique value in the 'patient_id' column
    patient_id_counts = df['patient_id'].value_counts()
    occurrence_counts = patient_id_counts.value_counts().sort_index()
    print("\nNumber of images per patient:")
    print(occurrence_counts)

    # Task 3: Count the number of patients with unique BIRADS
    df_filtered = df.groupby('patient_id').filter(
        lambda x: (x['BIRADS'].notna().any()))  # identify patient_ids with all BIRADS = NaN and exclude them
    unique_patients_birads = df.drop_duplicates(subset=['patient_id', 'BIRADS'])
    num_unique_patients = unique_patients_birads['patient_id'].nunique()  # count unique patients
    print("\nNumber of patients with single BIRADS (excluding nan):")
    print(num_unique_patients)

    # Task 4: Patients with 4 images and unique BIRADS
    grouped = df_filtered.groupby('patient_id')
    valid_patient_ids = grouped.filter(lambda x: (len(x) == 4) and (x['BIRADS'].nunique() == 1))
    valid_patient_count = valid_patient_ids['patient_id'].nunique()
    print("\nNumber of patients with 4 images and unique, non-NaN, BIRADS:")
    print(valid_patient_count)

    # Task 5: Patients with two images for left/right breast with unique BIRADS
    filtered_groups = df.groupby(['patient_id', 'BIRADS', 'laterality']).filter(
        lambda x: len(x) == 2)  # filter to find patients with exactly 2 left or 2 right occurrences with same birads
    number_of_occurrences = len(filtered_groups.groupby(['patient_id', 'BIRADS', 'laterality']))
    print("\nNumber of left/right patient breast screenings with two images and unique, non-NaN, BIRADS:")
    print(number_of_occurrences)
