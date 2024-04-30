import pandas as pd
import numpy as np
import os.path
import pydicom
from PIL import Image
from keras import Input
from keras.models import Model, Sequential, load_model
from keras.layers import Dense, Dropout, Concatenate
from keras.optimizers import Adam
from keras.utils import Sequence
from keras.preprocessing.image import load_img, img_to_array
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# ------------ Parameter setup ------------
initial_model = load_model('inbreast_vgg16_512x1.h5')
patient_df = pd.read_csv('updated_rsna_per_breast.csv')
image_dir = 'D:\\Mammography\\RSNA\\train_images'  # path to image directory
image_height = 1152
image_width = 896
channels = 3
images_per_entry = 4

# ------------ Model ------------
# Create base model
first_to_last_layer = initial_model.layers[-2].name
base_model = Model(inputs=initial_model.input,
                   outputs=initial_model.get_layer(first_to_last_layer).output)
print("Base model:")
base_model.summary()

# for layer in base_model.layers:
#     layer.trainable = False

# Create small output model
inputs = []
features = []
for i in range(images_per_entry):
    input_layer = Input(shape=(image_height, image_width, channels))
    feature_layer = base_model(input_layer)
    inputs.append(input_layer)
    features.append(feature_layer)

concatenated_features = Concatenate(axis=-1)(features)

output_model = Sequential([
    Dense(256, activation='relu', input_shape=(int(concatenated_features.shape[1]),)),
    Dropout(0.2),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(3, activation='softmax')
])

classification_output = output_model(concatenated_features)

# Create and compile full model
model = Model(inputs=inputs, outputs=classification_output)

optimizer = Adam(lr=0.00001)
model.compile(optimizer=optimizer,
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])


# ------------ Custom data generator ------------
class PatientDataGenerator(Sequence):
    def __init__(self, dataframe, img_dir, images_per_patient, batch_size=4,
                 target_size=(image_height, image_width),
                 shuffle=True):
        self.dataframe = dataframe
        self.image_dir = img_dir
        self.images_per_patient = images_per_patient
        self.batch_size = batch_size
        self.target_size = target_size
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        number_of_batches = int(np.floor(len(self.dataframe) / self.batch_size))  # complete batch
        if (len(self.dataframe) % self.batch_size) != 0:
            number_of_batches += 1  # additional partial batch
        return number_of_batches

    def __getitem__(self, index):
        # Generate indexes of the batch (index is the batch number provided by Keras)
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        # Find list of IDs
        patient_ids_batch = [self.dataframe['patient_id'].iloc[k] for k in indexes]

        # Generate data
        X, y = self.__data_generation(patient_ids_batch)

        return X, y

    def on_epoch_end(self):
        # Updates indexes after each epoch
        self.indexes = np.arange(len(self.dataframe))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, patient_ids_batch):
        # Initialize lists to hold the batches for each input tensor
        X = [[] for _ in range(self.images_per_patient)]  # Create a list for each input tensor
        y = []

        for patient_id in patient_ids_batch:
            # Retrieve all image IDs for this patient
            patient_df = self.dataframe[self.dataframe['patient_id'] == patient_id]
            image_ids = patient_df['image_id'].tolist()
            patient_images = []
            # Load each image, up to the specified number of images per patient
            for i in range(self.images_per_patient):
                if i < len(image_ids):
                    img_id = image_ids[i]
                else:
                    # If the patient has fewer images than required, cycle through the available images
                    img_id = image_ids[i % len(image_ids)]
                if os.path.isfile(f'{self.image_dir}\\{patient_id}\\{img_id}.dcm'):
                    img_path = f'{self.image_dir}\\{patient_id}\\{img_id}.dcm'  # Ensure this path format matches your dataset
                else:
                    raise ValueError(f'Cannot locate image {img_id}')
                # .dcm format
                dicom_image = pydicom.dcmread(img_path)
                # Get the pixel array from the DICOM file
                pixel_array = dicom_image.pixel_array
                # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
                pixel_array = ((pixel_array - np.min(pixel_array)) / (
                            np.max(pixel_array) - np.min(pixel_array))) * 255.0
                pixel_array = pixel_array.astype(np.uint8)
                # Convert to RGB if it's a single channel image
                if len(pixel_array.shape) == 2:
                    pixel_array = np.stack((pixel_array,) * 3, axis=-1)
                img = Image.fromarray(pixel_array).resize((self.target_size[1],self.target_size[0]))
                # .png format
                # img = load_img(img_path, target_size=self.target_size)

                img_array = img_to_array(img).astype(np.uint8)
                patient_images.append(img_array)

            # Split the images for this patient across the inputs
            for i in range(self.images_per_patient):
                X[i].append(patient_images[i])
            # Assuming the label for each patient is the same across all images
            label = patient_df['BIRADS'].iloc[0]  # Grabbing the label from the first entry
            y.append(label)

        X = [np.array(x) for x in X]

        return X, np.array(y)


# ------------ Train the model ------------
# Splitting the dataframe into training and validation sets
patients_df = patient_df.groupby('patient_id').agg({'BIRADS': 'first'}).reset_index()
train_patients, test_patients = train_test_split(patients_df, test_size=0.2, random_state=42,
                                                 stratify=patients_df['BIRADS'])
train_images = patient_df[patient_df['patient_id'].isin(train_patients['patient_id'])]
test_images = patient_df[patient_df['patient_id'].isin(test_patients['patient_id'])]

# Creating instances of the data generator for training and validation
train_generator = PatientDataGenerator(train_images, image_dir, images_per_entry, batch_size=4,
                                       target_size=(image_height, image_width), shuffle=True)
test_generator = PatientDataGenerator(test_images, image_dir, images_per_entry, batch_size=4,
                                      target_size=(image_height, image_width), shuffle=False)

# Training the model
history = model.fit_generator(
    train_generator,
    epochs=10,  # Specify the number of epochs
    steps_per_epoch=len(train_generator),
)
