import os
from scipy.spatial.distance import cosine
import cv2
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from preprocess import keep_only_breast, negate_if_should
import einops
import tensorflow as tf
import sys

model = tf.keras.applications.MobileNetV2(
    include_top=False, weights="imagenet", input_shape=(256, 256, 3), pooling="avg"
)

def load(path):
    for entity in os.scandir(path):
        image = pydicom.dcmread(entity.path).pixel_array 
        image = negate_if_should(image)
        image, _ = keep_only_breast(image)
        image = preprocess(image)
        yield entity.name, image

def preprocess(image):
    image = image.astype(np.float32)
    image = (image - image.min()) / (image.max() - image.min()) * 255.0
    image = einops.repeat(image, "h w -> h w c", c=3)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = cv2.resize(image, (256, 256))
    return image
        
if __name__ == "__main__":
    path = sys.argv[1] 
    avg_vector = np.load('avg_vector.npy')
    threshold = 0.25

    for name, image in load(path):
        image = einops.rearrange(image, "c h w -> 1 c h w")
        vector = model.predict(image).flatten()
        difference = cosine(vector, avg_vector)
        if difference > threshold:
            print(f'{name} is an outlier (cos diff = {difference} > {threshold}), will be removed.') 
        else:
            print(f'{name} is NOT an outlier (cos diff = {difference} < {threshold}), will NOT be removed.')
        #image = (image - image.min()) / (image.max() - image.min())
        #plt.imsave(f'{similarity}_{name}.png', image[0])

