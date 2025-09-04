import os

# Folders
bowl_folder = 'Images'
photo_folder = 'ExtraImages'
output_file = 'bowl_to_photo_mapping.txt'

# Get sorted list of bowl images
bowl_files = sorted([f for f in os.listdir(bowl_folder) if f.lower().startswith('bowl_') and f.lower().endswith(('.jpg', '.jpeg', '.png'))])

# Get sorted list of PHOTO images
photo_files = sorted([f for f in os.listdir(photo_folder) if f.startswith('PHOTO-') and f.lower().endswith(('.jpg', '.jpeg', '.png'))])

# Map bowls to photos by order
mapping = list(zip(bowl_files, photo_files))

# Write mapping to txt file
with open(output_file, 'w') as f:
    f.write('bowl_image -> photo_image\n')
    f.write('='*40 + '\n')
    for bowl, photo in mapping:
        f.write(f'{bowl} -> {photo}\n')

print(f'Mapping written to {output_file} ({len(mapping)} pairs).') 