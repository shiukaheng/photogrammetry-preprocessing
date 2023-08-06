"""
Example Test:
python test_image.py \
    --images-dir "PATH_TO_IMAGES_DIR" \
    --result-dir "PATH_TO_RESULT_DIR" \
    --pretrained-weight ./pretrained/SGHM-ResNet50.pth

Example Evaluation:
python test_image.py \
    --images-dir "PATH_TO_IMAGES_DIR" \
    --gt-dir "PATH_TO_GT_ALPHA_DIR" \
    --result-dir "PATH_TO_RESULT_DIR" \
    --pretrained-weight ./pretrained/SGHM-ResNet50.pth

"""

import argparse
import os
import glob
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision.utils import save_image
from tqdm import tqdm

from model.model import HumanSegment, HumanMatting
import utils
import inference

# --------------- Arguments ---------------
parser = argparse.ArgumentParser(description='Test Images')
parser.add_argument('--images-dir', type=str, required=True)
parser.add_argument('--result-dir', type=str, required=True)
parser.add_argument('--gt-dir', type=str, default=None)
parser.add_argument('--pretrained-weight', type=str, required=True)
parser.add_argument('--mask-thresh', type=float, default=0.05, help='Threshold for binary masking, values between 0-1.')
parser.add_argument('--mask-radius', type=int, default=20, help='Radius for mask dilation to add safety margin.')

args = parser.parse_args()

if not os.path.exists(args.pretrained_weight):
    print('Cannot find the pretrained model: {0}'.format(args.pretrained_weight))
    exit()

# Create the model
model = HumanMatting(backbone='resnet50')

# Wrap the model with DataParallel
model = nn.DataParallel(model).eval()

# Now you can load the state_dict directly
use_cuda = torch.cuda.is_available()
model.load_state_dict(torch.load(args.pretrained_weight, map_location=('cuda' if use_cuda else 'cpu')))

print("Load checkpoint successfully ...")

def get_file_list(directory, extensions):
    """
    Recursively search for files in a directory with specific extensions.
    
    Parameters:
    - directory (str): The directory to search in.
    - extensions (list of str): List of file extensions to search for (e.g., ['jpg', 'png']).

    Returns:
    - List of file paths.
    """
    file_list = []
    for ext in extensions:
        # The glob pattern is case insensitive
        pattern = os.path.join(directory, '**', f'*.{ext}')
        file_list.extend(glob.glob(pattern, recursive=True))
        # If you want to handle case insensitivity for extensions:
        pattern_upper = os.path.join(directory, '**', f'*.{ext.upper()}')
        file_list.extend(glob.glob(pattern_upper, recursive=True))
    return sorted(file_list)

# Using the function
image_extensions = ['jpg', 'jpeg', 'png', 'tif', 'tiff']
image_list = get_file_list(args.images_dir, image_extensions)

if args.gt_dir is not None:
    gt_list = get_file_list(args.gt_dir, image_extensions)

num_image = len(image_list)
print("Found ", num_image, " images")

metric_mad = utils.MetricMAD()
metric_mse = utils.MetricMSE()
metric_grad = utils.MetricGRAD()
metric_conn = utils.MetricCONN()
metric_iou = utils.MetricIOU()

mean_mad = 0.0
mean_mse = 0.0
mean_grad = 0.0
mean_conn = 0.0
mean_iou = 0.0

# Process 
for i in tqdm(range(num_image), desc="Generating masks", ncols=100):
    image_path = image_list[i]
    image_name = image_path[image_path.rfind('/')+1:image_path.rfind('.')]
    # print(i, '/', num_image, image_name)

    with Image.open(image_path) as img:
        img = img.convert("RGB")

    if args.gt_dir is not None:
        gt_path = gt_list[i]
        gt_name = gt_path[gt_path.rfind('/')+1:gt_path.rfind('.')]
        assert image_name == gt_name
        with Image.open(gt_path) as gt_alpha:
            gt_alpha = gt_alpha.convert("L")
        gt_alpha = np.array(gt_alpha) / 255.0

    # inference
    pred_alpha, pred_mask = inference.single_inference(model, img, use_cuda)

    # Thresholding the alpha
    _, pred_alpha_thresh = cv2.threshold((pred_alpha * 255).astype(np.uint8), args.mask_thresh * 255, 255, cv2.THRESH_BINARY)
    
    # Dilation to add safety margin
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (args.mask_radius, args.mask_radius))
    pred_alpha_dilated = cv2.dilate(pred_alpha_thresh, kernel)

    # Replace the previous alpha with the new alpha for subsequent processing
    pred_alpha = pred_alpha_dilated / 255.0  # Normalize to [0, 1] scale for further processing

    # evaluation
    if args.gt_dir is not None:
        batch_mad = metric_mad(pred_alpha, gt_alpha)
        batch_mse = metric_mse(pred_alpha, gt_alpha)
        batch_grad = metric_grad(pred_alpha, gt_alpha)
        batch_conn = metric_conn(pred_alpha, gt_alpha)
        batch_iou = metric_iou(pred_alpha, gt_alpha)
        print(" mad ", batch_mad, " mse ", batch_mse, " grad ", batch_grad, " conn ", batch_conn, " iou ", batch_iou)

        mean_mad += batch_mad
        mean_mse += batch_mse
        mean_grad += batch_grad
        mean_conn += batch_conn
        mean_iou += batch_iou

    # save results
    output_dir = args.result_dir + image_path[len(args.images_dir):image_path.rfind('/')]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = output_dir + '/' + image_name + '.png'
    Image.fromarray((((1-pred_alpha) * 255).astype('uint8')), mode='L').save(save_path)

if num_image > 0:
    print("Total mean mad ", mean_mad/num_image, " mean mse ", mean_mse/num_image, " mean grad ", \
        mean_grad/num_image, " mean conn ", mean_conn/num_image, " mean iou ", mean_iou/num_image)
else:
    print("No images found in ", args.images_dir)