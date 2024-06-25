import torch
import torch.nn.functional as F
import numpy as np
import torch.nn as nn
import sys

sys.path.append('../')
from utils import Metrics
from conv_model import CustomCNN, Model1

lishen_model = torch.load('/L-CAM/models/inbreast_vgg16_512x1.pth')
lishen_model.eval()

class AttentionMechanismM(nn.Module):
    def __init__(self, in_features):
        super(AttentionMechanismM, self).__init__()
        self.op = nn.Conv2d(in_channels=in_features, out_channels=2, kernel_size=1, padding=0, bias=True)

    def forward(self, l):
        N, C, W, H = l.size()
        c = self.op(l)
        a = torch.sigmoid(c)
        return a, c


class MammoVGG16(nn.Module):
    def __init__(self):
        super(MammoVGG16, self).__init__()
        self.features = self.get_features()
        self.classifier = self.get_classifier()
        self.adapPool = nn.AdaptiveAvgPool2d((1, 1))
        self.attnM = AttentionMechanismM(in_features=512)
        self.loss_cross_entropy = nn.CrossEntropyLoss()
        self.max_pool = nn.MaxPool2d(kernel_size=2, stride=2)

        self.area_loss_coef = 2
        self.smoothness_loss_coef = 0.01
        self.ce_coef = 1.5
        self.area_loss_power = 0.3

    def get_features(self):
        return lishen_model.features

    def get_classifier(self):
        return lishen_model.classifier

    def forward(self, x, label, isTrain=True):
        # FMs
        l = self.features(x)
        # Attention
        a1, c1 = self.attnM(l)
        self.a = a1
        self.c = c1
        x_norm = x

        if isTrain == True:
            N, C, W, H = a1.size()
            temp = torch.arange(0, N) * 2  # a vector [0,...,1000*Ν]
            t = label.long() + temp  # multiply label(etc [9,2,5,....,9]) with vector [0,...,Ν] find index
            a1 = torch.reshape(a1, (N * C, W, H))
            a2 = a1[t.long(), :, :]  # #Take indeces
            a2 = torch.unsqueeze(a2, 1)
            self.a2 = a2
            a2 = F.interpolate(a2, size=(1152, 896), mode='bilinear')
            x_masked = torch.mul(a2, x)
            x_norm = ((x_masked - torch.min(x_masked)) / (torch.max(x_masked) - torch.min(x_masked))) * 255.0
            x_norm = x_norm.float()  # Ensuring the tensor is of type float32

        y = self.features(x_norm)
        y = self.adapPool(y)
        y = y.view(y.size(0), -1)
        y = self.classifier(y)
        return [y, ]

    def get_loss(self, logits, gt_labels, masks):
        gt = gt_labels.long()
        cross_entr = self.loss_cross_entropy(logits[0], gt) * self.ce_coef
        area_loss = self.area_loss_coef * self.area_loss(masks)
        varation_loss = self.smoothness_loss_coef * self.smoothness_loss(masks)
        loss = cross_entr + area_loss + varation_loss
        # print('loss',loss)
        # print('ce',cross_entr)
        # print('arealoss',area_loss)
        # print('var_loss',varation_loss)
        return [loss, cross_entr, area_loss, varation_loss]

    def area_loss(self, masks):
        if self.area_loss_power != 1:
            masks = (masks + 0.0005) ** self.area_loss_power  # prevent nan (derivative of sqrt at 0 is inf)
        return torch.mean(masks)

    def smoothness_loss(self, masks, power=2, border_penalty=0.3):
        return 0
        # x_loss = torch.sum((torch.abs(masks[:, :, 1:, :] - masks[:, :, :-1, :])) ** power)
        # y_loss = torch.sum((torch.abs(masks[:, :, :, 1:] - masks[:, :, :, :-1])) ** power)
        # if border_penalty > 0:
        #     border = float(border_penalty) * torch.sum(
        #         masks[:, :, -1, :] ** power + masks[:, :, 0, :] ** power + masks[:, :, :, -1] ** power + masks[:, :, :,
        #                                                                                                  0] ** power)
        # else:
        #     border = 0.
        # return (x_loss + y_loss + border) / float(power * masks.size(0))  # watch out, normalised by the batch size!

    def get_c(self, gt_label):
        map1 = self.c
        map1 = map1[:, gt_label, :, :]
        return [map1, ]

    def get_a(self, gt_label):
        map1 = self.a
        map1 = map1[:, gt_label, :, :]
        return [map1, ]


def model(pretrained=True, **kwargs):
    model = MammoVGG16()
    return model

if __name__ == "__main__":
    # image = cv2.imread(r"C:\Users\Korisnik\Documents\GitHub\mammography\data\INBREAST\all_lesions\images\22613822.png")
    # image = cv2.resize(image, (896, 1152))
    # image = np.transpose(image, (2, 0, 1))
    # image = np.expand_dims(image, axis=0)
    image = np.random.random((1, 3, 1152, 896))
    image = torch.Tensor(image)

    model = MammoVGG16()
    model.forward(image, torch.Tensor(np.asarray([0])))

# from torchsummary import summary
# net = models.vgg16(pretrained=True)
# print(net)
# net = net.cuda()
# summary(net, input_size=(3, 224, 224))
# params = list(net.parameters())
# weight_softmax = np.squeeze(params[-12].data.cpu().numpy())
# print(weight_softmax.shape)
# print(net)


