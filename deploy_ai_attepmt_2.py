import os
import glob
import torch
import numpy as np
from PIL import Image
from sklearn import preprocessing
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
    from tqdm import tqdm
    #get images
    image_files = glob.glob(os.path.join(config.DEPLOYMENT_DATA, "*.png"))
    targets_orig = [x.split("/")[-1][9:14] for x in image_files]
    targets = [[c for c in x] for x in targets_orig]
    targets_flat = [c for clist in targets for c in clist]
    lbl_enc = preprocessing.LabelEncoder()
    lbl_enc.fit(targets_flat)
    targets_enc = [lbl_enc.transform(x) for x in targets]
    targets_enc = np.array(targets_enc)
    targets_enc = targets_enc + 1

    #get model and load it
    model = CaptchaModel(num_chars=config.NUM_CHARACTERS)
    model.load_state_dict(torch.load('model_1_50.pt'))
    model.eval()
    model.to(config.DEVICE)

    # Create an instance of the ClassificationDataset class
    live_dataset = dataset.ClassificationDataset(image_files, targets = targets_enc, resize=(config.IMAGE_HEIGHT, config.IMAGE_WIDTH))
    live_loader = torch.utils.data.DataLoader(
        live_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=config.NUM_WORKERS
    )
    # Loop through the images in the dataset
    fin_preds = []
    tk0 = tqdm(live_loader, total=len(live_loader))
    for data in tk0:
        for key, value in data.items():
            data[key] = value.to(config.DEVICE)
        batch_preds, _ = model(**data)
        fin_preds.append(batch_preds)
    valid_capthca_preds = []
    for vp in fin_preds:
        current_preds = decode_predictions(vp, lbl_enc)
        valid_capthca_preds.extend(current_preds)
    #print(valid_capthca_preds)
    combined = list(zip(targets_orig, valid_capthca_preds))
    print(combined)

if __name__ == "__main__":
    deploy_ai()