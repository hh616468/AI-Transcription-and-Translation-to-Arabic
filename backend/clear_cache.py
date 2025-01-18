import os
import shutil

def delete_files_in_directory(directory_path):
    """Deletes all files within a directory and its subdirectories, while keeping the directory structure."""
    try:
      for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
            print(f"Deleted {file_path}")
      print(f"Successfully cleared all files from {directory_path}")
    except Exception as e:
        print(f"Error deleting files in {directory_path}: {e}")

if __name__ == '__main__':
    target_directory = "storage"  # Replace with the directory you want to clean

    # Create a test directory with subfolders and files:
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        os.makedirs(os.path.join(target_directory, "subdir1"))
        os.makedirs(os.path.join(target_directory, "subdir2"))
        open(os.path.join(target_directory, "test1.txt"), "w").close()
        open(os.path.join(target_directory, "subdir1", "test2.txt"), "w").close()
        open(os.path.join(target_directory, "subdir2", "test3.txt"), "w").close()

    delete_files_in_directory(target_directory)

    # check if files have been removed
    print ("files after deletion:")
    for root, dirs, files in os.walk(target_directory):
       for file in files:
           print (file)