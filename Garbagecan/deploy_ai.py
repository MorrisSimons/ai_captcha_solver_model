import os
import glob
import torch
import numpy as np
from PIL import Image

import config as config
from model import CaptchaModel
import dataset

def remove_duplicates(x):
    if len(x) < 2:
        return x
    fin = ""
    for j in x:
        if fin == "":
            fin = j
        else:
            if j == fin[-1]:
                continue
            else:
                fin = fin + j
    return fin

def decode_predictions(preds, encoder):
    preds = preds.permute(1, 0, 2)
    preds = torch.softmax(preds, 2)
    preds = torch.argmax(preds, 2)
    preds = preds.detach().cpu().numpy()
    cap_preds = []
    for j in range(preds.shape[0]):
        temp = []
        for k in preds[j, :]:
            k = k - 1
            if k == -1:
                temp.append("§")
            else:
                p = encoder.inverse_transform([k])[0]
                temp.append(p)
        tp = "".join(temp).replace("§", "")
        cap_preds.append(remove_duplicates(tp))
    return cap_preds

def deploy_ai():
    image_folder = "./test_data"
    model = CaptchaModel(num_chars=config.NUM_CHARACTERS)
    # Load the model's state dict and set it to eval mode
    model.load_state_dict(torch.load('model_1_50.pt'))
    model.eval()
    # Get a list of image files in the image folder
    image_files = glob.glob(os.path.join(image_folder, "*.png"))
    # Load and preprocess the images

    data_set = dataset.ClassificationDataset(
        image_paths=image_files,
        targets=[1]*len(image_files),
        resize=(config.IMAGE_HEIGHT, config.IMAGE_WIDTH)
    )
    images = []
    for image_data in data_set:
        image_file = image_data["images"]
        image = image_data["targets"]

    for image_file, image in data_set:
        images.append(image)
    print(images)
    images = torch.stack(images).to(config.DEVICE)

    outputs = model(images)
    for image_file, output in zip(image_files, outputs):
        output_str = decode_predictions(output)
        print(f"Prediction for {image_file}: {output_str}")
deploy_ai()