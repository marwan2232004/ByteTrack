import os
import shutil
import argparse
import json

def extract_crowdhuman_subset(dataset_path, output_path, num_train_images, num_val_images, shift=0):
    """
    Extracts a specified number of images from train and val sets of the CrowdHuman dataset along with their bounding boxes
    and stores them in a new directory with a corresponding .odgt file.

    Parameters:
    - dataset_path (str): Path to the root folder containing 'train' and 'val' subfolders.
    - output_path (str): Path to save the extracted dataset.
    - num_train_images (int): Number of images to extract from the training set.
    - num_val_images (int): Number of images to extract from the validation set.
    - shift (int): Offset for starting index (default is 0).
    """
    
    output_path = os.path.join(output_path,'crowdhuman')

    if os.path.exists(output_path):
        shutil.rmtree(output_path)
        
    os.makedirs(output_path, exist_ok=True)  # Ensure output directory exists

    # Define paths for original and new .odgt files
    train_odgt = os.path.join(dataset_path, "annotation_train.odgt")
    val_odgt = os.path.join(dataset_path, "annotation_val.odgt")
    new_train_odgt = os.path.join(output_path, "annotation_train.odgt")
    new_val_odgt = os.path.join(output_path, "annotation_val.odgt")

    # Function to process images and annotations
    def process_subset(image_dir, odgt_file, output_dir, new_odgt_file):
        if not os.path.exists(odgt_file):
            print(f"Annotation file {odgt_file} not found!")
            return

        os.makedirs(output_dir, exist_ok=True)

        # Read annotations
        with open(odgt_file, 'r') as f:
            annotations = [json.loads(line) for line in f]
        
        amount = num_val_images if 'val' in image_dir else num_train_images

        start = shift * amount
        # Select the specified number of images with `shift`
        selected_annotations = annotations[start:start + amount]
        
        # Copy images and save new annotations
        with open(new_odgt_file, 'w') as new_f:
            for ann in selected_annotations:
                img_name = ann['ID'] + ".jpg"
                src_img_path = os.path.join(image_dir, img_name)
                dst_img_path = os.path.join(output_dir, img_name)

                if os.path.exists(src_img_path):
                    shutil.copyfile(src_img_path, dst_img_path)
                    new_f.write(json.dumps(ann) + "\n")
                else:
                    print(f"Image {src_img_path} not found, skipping...")

        print(f"Processed {len(selected_annotations)} images from {odgt_file}")

    # Process train and val sets
    process_subset(os.path.join(dataset_path, "Images"), train_odgt, os.path.join(output_path, "CrowdHuman_train"), new_train_odgt)
    process_subset(os.path.join(dataset_path, "Images_val"), val_odgt, os.path.join(output_path, "CrowdHuman_val"), new_val_odgt)

    print(f"Subset saved in {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract a subset of the CrowdHuman dataset.")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to the CrowdHuman dataset.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the extracted subset.")
    parser.add_argument("--num_train_images", type=int, required=True, help="Number of images to extract from the training set.")
    parser.add_argument("--num_val_images", type=int, required=True, help="Number of images to extract from the validation set.")
    parser.add_argument("--shift", type=int, default=0, help="Shift value for the starting index (default is 0).")

    args = parser.parse_args()

    extract_crowdhuman_subset(args.dataset_path, args.output_path, args.num_train_images, args.num_val_images, args.shift)