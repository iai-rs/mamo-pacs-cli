# from torchvision import transforms
from pydicom import dcmread

from .transforms import transforms
from .mydataset import dataset as my_dataset, dataset_with_mask
import torch
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
import os
from skimage.filters import threshold_otsu
from preprocess import keep_only_breast, negate_if_should


def data_loader(args, test_path=False, segmentation=False):
    mean_vals = [0.485, 0.456, 0.406]
    std_vals = [0.229, 0.224, 0.225]

    input_size = int(args.input_size)
    crop_size = int(args.crop_size)

    tsfm_train = transforms.Compose(
        [
            transforms.Resize(input_size),  # 356
            transforms.RandomCrop(crop_size),  # 321
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            #  transforms.Normalize(mean_vals, std_vals)
        ]
    )

    tsfm_val = transforms.Compose(
        [
            transforms.Resize(input_size),  # 356
            transforms.CenterCrop(crop_size),  # 321
            transforms.ToTensor(),
            # transforms.Normalize(mean_vals, std_vals)
        ]
    )

    img_train = my_dataset(
        args.train_list, root_dir=args.img_dir, transform=tsfm_train, with_path=True
    )

    img_test = my_dataset(
        args.test_list, root_dir=args.img_dir, transform=tsfm_val, with_path=test_path
    )

    train_loader = DataLoader(
        img_train,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
    )
    val_loader = DataLoader(
        img_test,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )

    return train_loader, val_loader


def mammo_loader(txt_path, img_dir, batch_size):
    class ImageDataset(Dataset):
        def __init__(self, txt_path, img_dir):
            self.img_labels = []
            with open(txt_path, "r") as file:
                for line in file:
                    image_name, label = line.strip().split()
                    self.img_labels.append((image_name, int(label)))
            self.img_dir = img_dir

        def __len__(self):
            return len(self.img_labels)

        def __getitem__(self, idx):
            # Extract image name and label
            img_name, label = self.img_labels[idx]
            img_path = os.path.join(self.img_dir, img_name)

            # Load and preprocess the image
            image = self.read_img(img_path)
            image = self.preprocess(image)

            # Return image path, image tensor, and label
            return img_path, image, label

        def read_img(self, path):
            image = dcmread(path).pixel_array
            return image

        def preprocess(self, image):
            image = ((image - np.min(image)) / (np.max(image) - np.min(image))) * 255.0
            image = image.astype(np.uint8)
            image = cv2.resize(image, (896, 1152), interpolation=cv2.INTER_CUBIC)
            image = image.astype("float32")
            image = np.stack((image,) * 3, axis=0)  # Stack to create 3 channels
            # image = np.expand_dims(image, axis=0)  # Add batch dimension
            image = torch.Tensor(image)
            return image

    dataset = ImageDataset(txt_path=txt_path, img_dir=img_dir)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def inference_loader(img_dir, batch_size):
    class ImageDataset(Dataset):
        def __init__(self, img_dir):
            self.image_paths = [
                os.path.join(img_dir, fname) for fname in os.listdir(img_dir)
            ]

        def __len__(self):
            return len(self.image_paths)

        def __getitem__(self, idx):
            # Get image path
            img_path = self.image_paths[idx]

            # Load and preprocess the image
            original = self.read_img(img_path)
            negated = negate_if_should(original)
            only_breast_image, _ = keep_only_breast(negated)
            fully_preprocessed = self.preprocess(only_breast_image)
            original = self.preprocess(original)

            # Return image path and image tensor
            return img_path, fully_preprocessed, original

        def read_img(self, path):
            # Load the image from DICOM file
            image = dcmread(path).pixel_array
            return image

        def preprocess(self, image):
            # Normalize and resize the image
            image = ((image - np.min(image)) / (np.max(image) - np.min(image))) * 255.0
            image = image.astype(np.uint8)
            image = cv2.resize(image, (896, 1152), interpolation=cv2.INTER_CUBIC)
            image = image.astype("float32")
            image = np.stack((image,) * 3, axis=0)  # Stack to create 3 channels
            image = torch.Tensor(image)
            return image

    dataset = ImageDataset(img_dir=img_dir)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)
