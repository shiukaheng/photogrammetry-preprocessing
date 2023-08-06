#!/bin/bash
echo -e "\033[36m🎞️ Converting images from RAW to TIFF if required\033[0m"
python convert.py
echo -e "\033[36m🤖 Creating human masks\033[0m"
python masking/test_image.py --images-dir "./converted" --result-dir "./masks" --pretrained-weight ./masking/weights/SGHM-ResNet50.pth