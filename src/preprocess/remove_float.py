import os
import re

# Path to the folder containing your text files
input_dir = "/media/Datacenter_storage/PublicDatasets/cerebral_microbleeds_VALDO/3slices_png_final/labels/val"

# Regex to capture numbers inside np.float64(...)
pattern = re.compile(r"np\.float64\((.*?)\)")

for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_dir, filename)

        with open(file_path, "r") as infile:
            content = infile.read()

        # Replace np.float64(xxx) → xxx
        cleaned = pattern.sub(r"\1", content)

        # Write back to the same file (overwrite)
        with open(file_path, "w") as outfile:
            outfile.write(cleaned)

        print(f"Modified in place: {filename}")
