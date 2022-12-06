import torch
from torch import nn
from torch.nn import functional as F

class CaptchaModel(nn.Module):
    def __init__(self, num_chars):
        super(CaptchaModel, self).__init__()
        self.conv_1 = nn.Conv2d(3, 128, kernel_size=(3,3), padding=(1,1))
        self.max_pool_1 = nn.MaxPool2d(kernel_size=(2,2))
        self.conv_2 = nn.Conv2d(128, 64, kernel_size=(3,3), padding=(1,1))
        self.max_pool_2 = nn.MaxPool2d(kernel_size=(2,2))

    def forward(self, images, targets = None):
        bs, c, h, w = images.size()
        print(bs, c, h, w)
        x = F.relu(self.conv_1(x))
        print(x.size())
        x = self.max_pool_1(x)
        print(x.size())
