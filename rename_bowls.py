import os

folder = 'Images'
files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

for idx, filename in enumerate(files, 1):
    ext = os.path.splitext(filename)[1]
    new_name = f"bowl_{idx:03d}{ext}"
    src = os.path.join(folder, filename)
    dst = os.path.join(folder, new_name)
    print(f"Renaming {filename} -> {new_name}")
    os.rename(src, dst) 