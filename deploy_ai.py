import os
import glob
import torch
from torch import nn
import numpy as np

import albumentations
from sklearn import preprocessing
from sklearn import model_selection
from sklearn import metrics
from tensorflow import keras

import config
import dataset
import engine
import train
from model import CaptchaModel

def run_deployment():
    """to run the deployment of the model"""
    image_files = glob.glob(os.path.join(config.DEPLOYMENT_DATA, "*.png"))
    targets_orig = [x.split("/")[-1][9:14] for x in image_files]
    targets = [[c for c in x] for x in targets_orig]
    targets_flat = [c for clist in targets for c in clist]
    lbl_enc = preprocessing.LabelEncoder()
    lbl_enc.fit(targets_flat)
    targets_enc = [lbl_enc.transform(x) for x in targets]
    targets_enc = np.array(targets_enc)
    targets_enc = targets_enc + 1
    (
        train_imgs,
        test_imgs,
        train_targets,
        test_targets,
        _,
        test_targets_orig,
    ) = model_selection.train_test_split(
        image_files,
        targets_enc,
        targets_orig,
        test_size=0.1,
        random_state=42
    )
    deployment_dataset = dataset.ClassificationDataset(
        image_paths=train_imgs,
        targets=train_targets,
        resize=(config.IMAGE_HEIGHT, config.IMAGE_WIDTH),
    )
    deployment_loader = torch.utils.data.DataLoader(
        deployment_dataset,
        batch_size=config.BATCH_SIZE,
        num_workers=config.NUM_WORKERS,
        shuffle=False,
    )
    model = CaptchaModel(num_chars=len(lbl_enc.classes_))
    if input("[Y/N] to load model: ").upper() == "Y":
        name = input("Enter model name: ")
        model.load_state_dict(torch.load(f"{name}.pt"))
        model.eval()

    model.to(config.DEVICE)
    predictions = engine.predict_fn(model, deployment_loader)
    print(predictions)

if __name__ == "__main__":
    run_deployment()