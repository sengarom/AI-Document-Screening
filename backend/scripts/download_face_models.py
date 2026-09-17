import os
import hashlib
import urllib.request
from pathlib import Path

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    {
        "name": "face_detection_yunet_2023mar.onnx",
        "url": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "license": "MIT License (Shiqi Yu et al.)",
        "version": "2023 March"
    },
    {
        "name": "face_recognition_sface_2021dec.onnx",
        "url": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
        "license": "Apache-2.0 License",
        "version": "2021 December"
    }
]

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    readme_path = MODELS_DIR / "README.md"
    readme_content = "# OpenCV Zoo Face Models Provenance\n\n"
    
    for model in MODELS:
        filepath = MODELS_DIR / model["name"]
        if not filepath.exists():
            print(f"Downloading {model['name']}...")
            urllib.request.urlretrieve(model["url"], filepath)
        else:
            print(f"{model['name']} already exists.")
            
        sha256 = compute_sha256(filepath)
        print(f"SHA-256: {sha256}")
        
        readme_content += f"## {model['name']}\n"
        readme_content += f"- **Official Source URL**: {model['url']}\n"
        readme_content += f"- **Model Version/Date**: {model['version']}\n"
        readme_content += f"- **SHA-256 Checksum**: `{sha256}`\n"
        readme_content += f"- **License**: {model['license']}\n"
        readme_content += "- **Attribution Requirements**: Must retain copyright notices as per respective licenses.\n\n"
        
    with open(readme_path, "w") as f:
        f.write(readme_content)
        
    print("Done. Wrote models/README.md.")

if __name__ == "__main__":
    main()
