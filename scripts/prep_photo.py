import os

import cv2
import numpy as np
from PIL import Image
from rembg import remove


# -------------------------------------------------------
# Ansif profile photo
# -------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))

INPUT_IMAGE = os.path.join(HERE, "..", "image.png")
OUTPUT_IMAGE = os.path.join(HERE, "..", "source-prepped.png")


# -------------------------------------------------------
# 1. Load photo and remove background
# -------------------------------------------------------

original = Image.open(INPUT_IMAGE).convert("RGBA")

cutout = remove(original)

rgb = np.array(cutout.convert("RGB"))
alpha = np.array(cutout.getchannel("A"))


# -------------------------------------------------------
# 2. Convert subject to grayscale
# -------------------------------------------------------

gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)


# -------------------------------------------------------
# 3. Improve LOCAL facial contrast
#    This is the important part used by the reference.
# -------------------------------------------------------

clahe = cv2.createCLAHE(
    clipLimit=2.6,
    tileGridSize=(8, 8)
)

gray = clahe.apply(gray)


# -------------------------------------------------------
# 4. Slightly brighten the portrait
#    Keeps the ASCII cleaner and less dense.
# -------------------------------------------------------

gray = cv2.convertScaleAbs(
    gray,
    alpha=1.05,
    beta=18
)


# -------------------------------------------------------
# 5. Feather subject edges slightly
# -------------------------------------------------------

mask = alpha.astype(np.float32) / 255.0

mask = cv2.GaussianBlur(
    mask,
    (0, 0),
    1.0
)


# -------------------------------------------------------
# 6. Put the subject onto a PURE WHITE background
#
# White becomes empty spaces when converted to ASCII.
# This is what creates the clean portrait style.
# -------------------------------------------------------

prepared = (
    gray.astype(np.float32) * mask
    + 255.0 * (1.0 - mask)
)

prepared = np.clip(
    prepared,
    0,
    255
).astype(np.uint8)


# -------------------------------------------------------
# 7. Save prepared portrait
# -------------------------------------------------------

Image.fromarray(
    prepared,
    mode="L"
).save(OUTPUT_IMAGE)


print("Prepared portrait created:")
print(OUTPUT_IMAGE)
