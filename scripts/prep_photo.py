from PIL import Image, ImageEnhance, ImageOps

# Load Ansif's original profile photo
img = Image.open("image.png").convert("RGB")

# Convert to grayscale
img = ImageOps.grayscale(img)

# Improve contrast for the ASCII portrait
img = ImageEnhance.Contrast(img).enhance(1.8)

# Improve sharpness
img = ImageEnhance.Sharpness(img).enhance(1.5)

# Resize while keeping portrait proportions
img.thumbnail((700, 700))

# Save prepared image
img.save("source-prepped.png")

print("Prepared image saved as source-prepped.png")
