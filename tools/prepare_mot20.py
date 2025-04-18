import os
import configparser
import shutil
import argparse

def parse_mot20_gt(gt_folder):
    """
    Parses the MOT20 ground truth (GT) folder and organizes lines by frame_id.

    Parameters:
        gt_folder (str): Path to the GT folder containing gt.txt files.

    Returns:
        dict: A dictionary where keys are frame IDs and values are lists of lines corresponding to each frame.
    """
    gt_file_path = os.path.join(gt_folder, "gt.txt")
    
    if not os.path.exists(gt_file_path):
        raise FileNotFoundError(f"GT file not found at {gt_file_path}")

    frame_dict = {}

    with open(gt_file_path, "r") as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue  # Skip malformed lines
            
            frame_id = int(parts[0])  # First column is the frame ID
            
            if frame_id not in frame_dict:
                frame_dict[frame_id] = []
            
            frame_dict[frame_id].append(line.strip())

    return frame_dict

def mot20_partition(mot20_path:str, output_path:str, amount:int, shift:int):
    splits =  ['train']
    # create the parent folder of output
    output_root:str = os.path.join(output_path,'MOT20')
    
    if  os.path.exists(output_root):
        shutil.rmtree(output_root)
        
    os.mkdir(output_root)
    for split in splits:
        
        out_split:str = os.path.join(output_root,split) 
        os.mkdir(out_split)

        out_data_folder = os.path.join(out_split,'MOT20-02') 
        os.mkdir(out_data_folder)

        out_gt = os.path.join(out_data_folder,'gt')
        os.mkdir(out_gt)
        
        out_gt_file = os.path.join(out_gt,'gt.txt')
        with open(out_gt_file, "w", encoding="utf-8") as file:
            file.write("")

        out_frames = os.path.join(out_data_folder,'img1')
        os.mkdir(out_frames)

        frame_count:int = 0
        start_frame:int = shift * amount + 1
        
        # get split folder
        train_data:str = os.path.join(mot20_path,split) 
        # get list of subfolders
        videos: str = os.listdir(train_data)

        # loop over the videos 
        for folder in videos:
            if frame_count >= amount: break
            
            current_dir:str = os.path.join(train_data,folder)
            frames:str = os.path.join(current_dir,'img1')
            gt:str =  os.path.join(current_dir,'gt')
            info_path:str = os.path.join(current_dir, 'seqinfo.ini')
            config = configparser.ConfigParser()
            config.read(info_path)
            seq_length:int = int(config['Sequence']['seqLength'])
            imExt:str = config['Sequence']['imExt'] 

            # If the current seq length is smaller than the start_frame
            # This means the we will leave this one a take from next
   
            if seq_length < start_frame: 
                start_frame -= seq_length
                continue
            
            print(f"Processing {folder} with {min(seq_length - start_frame , amount - frame_count)} frames")

            frames_dict = parse_mot20_gt(gt)
            
            # Loop over amount and take from the seq untill the amount ends or seq ends
            with open(out_gt_file, "a", encoding="utf-8") as file:
                for i in range(amount):
                    frame_count += 1
                    source = os.path.join(frames,f"{start_frame:06d}{imExt}")
                    dest =  os.path.join(out_frames,f"{frame_count:06d}{imExt}")
                    if frames_dict.get(start_frame) is None:
                        start_frame += 1
                        continue
                    shutil.copyfile(source, dest)
                    lines = frames_dict[start_frame]
                    for line in lines:
                        line = line.split(',')
                        line[0] = frame_count
                        line = ','.join(map(str, line))
                        file.write(f"{line}\n")
                        
                    start_frame += 1
                    if start_frame > seq_length or frame_count >= amount: 
                        start_frame = 1
                        break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare MOT20 dataset partition.")
    parser.add_argument("--mot20_path", type=str, required=True, help="Path to the MOT20 dataset.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the output partition.")
    parser.add_argument("--amount", type=int, required=True, help="Number of frames to partition.")
    parser.add_argument("--shift", type=int, required=True, help="Shift value for the partition.")

    args = parser.parse_args()

    mot20_partition(args.mot20_path, args.output_path, args.amount, args.shift)