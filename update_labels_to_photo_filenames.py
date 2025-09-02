import csv

# Read mapping from bowl_to_photo_mapping.txt
mapping = {}
with open('bowl_to_photo_mapping.txt', 'r') as f:
    for line in f:
        if '->' in line and not line.startswith('bowl_image'):
            bowl, photo = line.strip().split(' -> ')
            mapping[bowl] = photo

# Read and update labels.csv
rows = []
with open('labels.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows.append(header)
    for row in reader:
        filename = row[0].strip()
        # Handle possible typo in original CSV (e.g., 'bowl_002,jpg')
        if not filename.endswith('.jpg') and not filename.endswith('.jpeg') and not filename.endswith('.png'):
            filename = filename.split(',')[0] + '.jpg'
        if filename in mapping:
            row[0] = mapping[filename]
        rows.append(row)

# Write updated CSV to a new file
with open('labels_photo.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print('labels_photo.csv created with new PHOTO-... filenames.') 