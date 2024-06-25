import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init
import numpy as np


class Model1(nn.Module):
    def __init__(self):
        super(Model1, self).__init__()
        # First block
        self.conv1_1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv1_1.weight, mode='fan_in', nonlinearity='relu')
        self.conv1_2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv1_2.weight, mode='fan_in', nonlinearity='relu')
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Second block
        self.conv2_1 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv2_1.weight, mode='fan_in', nonlinearity='relu')
        self.conv2_2 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv2_2.weight, mode='fan_in', nonlinearity='relu')
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Third block
        self.conv3_1 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv3_1.weight, mode='fan_in', nonlinearity='relu')
        self.conv3_2 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv3_2.weight, mode='fan_in', nonlinearity='relu')
        self.conv3_3 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv3_3.weight, mode='fan_in', nonlinearity='relu')
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Fourth block
        self.conv4_1 = nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv4_1.weight, mode='fan_in', nonlinearity='relu')
        self.conv4_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv4_2.weight, mode='fan_in', nonlinearity='relu')
        self.conv4_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv4_3.weight, mode='fan_in', nonlinearity='relu')
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Fifth block
        self.conv5_1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv5_1.weight, mode='fan_in', nonlinearity='relu')
        self.conv5_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv5_2.weight, mode='fan_in', nonlinearity='relu')
        self.conv5_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        init.kaiming_normal_(self.conv5_3.weight, mode='fan_in', nonlinearity='relu')
        self.pool5 = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        # Applying layers
        x = F.relu(self.conv1_1(x))
        x = F.relu(self.conv1_2(x))
        x = self.pool1(x)

        x = F.relu(self.conv2_1(x))
        x = F.relu(self.conv2_2(x))
        x = self.pool2(x)

        x = F.relu(self.conv3_1(x))
        x = F.relu(self.conv3_2(x))
        x = F.relu(self.conv3_3(x))
        x = self.pool3(x)

        x = F.relu(self.conv4_1(x))
        x = F.relu(self.conv4_2(x))
        x = F.relu(self.conv4_3(x))
        x = self.pool4(x)

        x = F.relu(self.conv5_1(x))
        x = F.relu(self.conv5_2(x))
        x = F.relu(self.conv5_3(x))
        x = self.pool5(x)
        return x


class CustomCNN(nn.Module):
    def __init__(self):
        super(CustomCNN, self).__init__()
        # Initialize model_1
        self.model1 = Model1()

        # First convolution block
        self.conv1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv1.weight, mode='fan_in', nonlinearity='linear')
        self.bn1 = nn.BatchNorm2d(512, eps=0.001, momentum=0.99)
        self.activation1 = nn.ReLU()  # ReLU activation
        self.dropout1 = nn.Dropout(0.0)  # Drop rate 0

        # Max Pooling
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Second convolution block
        self.conv2 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        init.kaiming_normal_(self.conv2.weight, mode='fan_in', nonlinearity='linear')
        self.bn2 = nn.BatchNorm2d(512, eps=0.001, momentum=0.99)
        self.activation2 = nn.ReLU()  # ReLU activation
        self.dropout2 = nn.Dropout(0.0)  # Drop rate 0

        # Max Pooling
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Global Average Pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout3 = nn.Dropout(0.0)  # Drop rate 0

        # Dense Layer
        self.fc = nn.Linear(512, 2)

    def features(self, x):
        # Model1
        x = self.model1(x)

        # First block
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.activation1(x)
        x = self.dropout1(x)
        x = self.pool1(x)

        # Second block
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.activation2(x)
        x = self.dropout2(x)
        x = self.pool2(x)
        return x

    def classifier(self, x):
        x = self.fc(x)
        x = F.softmax(x, dim=1)  # Apply softmax to the output
        return x
    def forward(self, x):
        x = self.features(x)

        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)  # Flatten the output

        x = self.classifier(x)
        return x