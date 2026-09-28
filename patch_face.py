import re

with open('backend/app/services/face/face_service.py', 'r') as f:
    content = f.read()

old_multiple = '''        if len(faces) > 1:
            status = FaceVerificationStatus.MULTIPLE_FACES_DOCUMENT if source_name == "document" else FaceVerificationStatus.MULTIPLE_FACES_REFERENCE
            return None, status, f"Multiple faces detected in {source_name}. Exactly one face is required."'''

new_multiple = '''        if len(faces) > 1:
            # Pick the largest face (by bounding box area) when multiple are detected
            # faces object is a numpy array in newer OpenCV versions, but can be a list of arrays.
            # Convert to list and use max on the bounding box area (w * h)
            faces = [max(list(faces), key=lambda f: f[2] * f[3])]'''

if old_multiple in content:
    content = content.replace(old_multiple, new_multiple)
    with open('backend/app/services/face/face_service.py', 'w') as f:
        f.write(content)
    print("Patched face_service.py")
else:
    print("Could not find old_multiple in face_service.py")
