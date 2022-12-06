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

        self.linear_1 = nn.Linear(1600, 64)
        self.drop_1 = nn.Dropout(0.2)

        self.gru = nn.GRU(64, 32, bidirectional=True, num_layers=2, dropout=0.25)
        self.output = nn.Linear(64, num_chars + 1)
        """The Gated Recurrent Unit (GRU) is a type of Recurrent Neural Network (RNN) that, in certain cases,
         has advantages over long short term memory (LSTM). GRU uses less memory and is faster than LSTM,
          however, LSTM is more accurate when using datasets with longer sequences."""

    def forward(self, images, targets = None):
        def _lossfunction_for_len(output, targets):
            log_softmax_values = F.log_softmax(x, 2) #x = output of the model
            input_lengths = torch.full(
                size=(bs,),
                fill_value=log_softmax_values.size(0),
                dtype=torch.int32
            )
            print(input_lengths)
            target_lengths = torch.full(
                size=(bs,),
                fill_value=targets.size(0),
                dtype=torch.int32
            )
            print(target_lengths)
            loss = nn.CTCLoss(blank=0)(
                log_softmax_values,
                targets,
                input_lengths,
                target_lengths)
            return x, loss

        bs, c, h, w = images.size() #bs = barch size
        print(bs, c, h, w)
        x = F.relu(self.conv_1(images))
        print(x.size())
        x = self.max_pool_1(x)
        print(x.size())
        #next conv 2 layer
        x = F.relu(self.conv_2(x))
        print(x.size())
        x = self.max_pool_2(x) # 1, 64, 25, 75
        x = x.permute(0, 3, 1, 2) # 1, 75, 64, 25
        print(x.size())
        x = x.view(bs, x.size(1), -1)
        print(x.size())
        x = self.linear_1(x)
        x = self.drop_1(x)
        print(x.size())
        x, _ = self.gru(x)
        print(x.size())
        x = self.output(x)
        print(x.size())#75 timestamps, 20 classes
        x = x.permute(1, 0, 2) #before softmax
        print(x.size())
        if targets is not None: # loss calculation for len of the target
            return _lossfunction_for_len(x, targets,)
        return x, None

if __name__ == "__main__":
    cm = CaptchaModel(num_chars=19)
    img = torch.rand(1, 3, 100, 300)
    target = torch.randint(1,20, (1, 5))
    x, loss = cm(img, target)