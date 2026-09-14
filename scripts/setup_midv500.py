import sys
import os
import urllib.request
import zipfile
from pathlib import Path

def download_midv500_sample():
    """
    Downloads the official MIDV-500 dataset.
    Since we cannot assume a small arbitrary sample is available via official sources,
    and the full dataset is ~3.5GB, we provide the official FTP link.
    """
    print("============================================================")
    print(" MIDV-500 Dataset Setup")
    print("============================================================")
    print("The official MIDV-500 dataset is hosted by Smart Engines at:")
    print("ftp://smartengines.com/midv-500/")
    print("\nThis FTP server allows anonymous access without registration or passwords.")
    print("However, the dataset is very large (~3.5 GB for the main images.zip).")
    print("\nIf you only need a sample for benchmarking, please manually download")
    print("a subset of the dataset from the official FTP and place it in:")
    print("E:\\AI-Document-Screening\\datasets\\MIDV-500\\")
    print("============================================================")
    
    # We will create the directory to guide the user
    dataset_dir = Path("E:/AI-Document-Screening/datasets/MIDV-500")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nAction Required:")
    print(f"Please place your extracted test images in: {dataset_dir}")
    print("Once placed, you can run 'test_ocr_dataset.py' to benchmark the OCR engine.")

if __name__ == "__main__":
    download_midv500_sample()
