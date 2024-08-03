import sys
sys.path.append('../')

from utils.LoadData import inference_loader
from sqlalchemy import text, create_engine
import os
from dicom_to_png import png_to_minio, write_minio, write_oracle_s3
from inference import process_img
import cv2
import concurrent.futures

def get_db_engine():
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    hostname = os.environ.get('DB_HOSTNAME')
    port = os.environ.get('DB_PORT')
    database_name = os.environ.get('DB_NAME')
    connection_string = f"postgresql://{username}:{password}@{hostname}:{port}/{database_name}"
    return create_engine(connection_string)

def write_postgres(engine, study_uid, model_1_result):
    insert_statement = text(
        f"INSERT INTO birads_results (study_uid, model_1_result)"
        f"VALUES (:study_uid, :model_1_result)"
        f"ON CONFLICT (study_uid) DO UPDATE SET model_1_result = EXCLUDED.model_1_result;"
    )

    with engine.connect() as connection:
        with connection.begin():
            connection.execute(insert_statement, {'study_uid': study_uid, 'model_1_result': model_1_result})

    print(f"Attempted to write row for {study_uid}.")

def write_heatmap(heatmap, study_uid, tmp_heatmap_folder):
    png_image = f'{study_uid}.png'
    png_filepath = f'{tmp_heatmap_folder}/{png_image}'

    heatmap_image_saved = cv2.imwrite(png_filepath, heatmap)
    write_minio('heatmaps', png_filepath, png_image)
    write_oracle_s3('bucket-aimambo-heatmaps', png_filepath)

    # Remove the locally saved .png image
    os.remove(png_filepath)

def setup_tmp_folders(tmp_png_folder, tmp_heatmap_folder):
    os.makedirs(tmp_png_folder)
    os.makedirs(tmp_heatmap_folder)

def process_and_write(img_path, img, engine, tmp_heatmap_folder):
    print(f"ai-db-writter: {img_path}")
    study_uid = img_path[0].split(os.path.sep)[-1]
    model_1_result, heatmap = process_img(img)
    try:
        write_heatmap(heatmap, study_uid, tmp_heatmap_folder)
        write_postgres(engine, study_uid, model_1_result)
    except Exception as e:
        print(f"Error while writing {img_path} to postgres/heatmap: {e}")

dicom_folder = '/iors'
tmp_png_folder = '/L-CAM/L_CAM_VGG16/tmp_png'
tmp_heatmap_folder = '/L-CAM/L_CAM_VGG16/tmp_heatmap'

def main():
    print("Start main in ai-db-writter")
    print("Setup folders")
    setup_tmp_folders(tmp_png_folder, tmp_heatmap_folder)
    engine = get_db_engine()
    print("Set engine finished")

    print("Start writing heatmaps with threads...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for img_path, img in inference_loader(dicom_folder, 1):
            futures.append(
                executor.submit(process_and_write, img_path, img, engine, tmp_heatmap_folder)
            )
        # Wait for all threads to complete
        concurrent.futures.wait(futures)

    print("Start writing png images with threads...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for filename in os.listdir(dicom_folder):
            futures.append(
                executor.submit(png_to_minio, dicom_folder, tmp_png_folder, filename)
            )
        concurrent.futures.wait(futures)

if __name__ == '__main__':
    main()
