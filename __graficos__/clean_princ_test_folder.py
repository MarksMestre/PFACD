import os


# def main(test_folder=None):
    # grafs_folder = os.path.dirname(os.path.abspath(__file__))
    # if test_folder is None:
    #     test_folder = os.path.join(grafs_folder, "principais", "test")
    # if os.path.exists(test_folder):
    #     for filename in os.listdir(test_folder):
    #         file_path = os.path.join(test_folder, filename)
    #         if os.path.isfile(file_path) or os.path.isdir(file_path):
    #             if os.path.isdir(file_path):
    #                 for sub_filename in os.listdir(file_path):
    #                     sub_file_path = os.path.join(file_path, sub_filename)
    #                     os.remove(sub_file_path)
    #                     print(f"Removido: {sub_file_path}")
    #                 os.rmdir(file_path)
    #                 print(f"Removido diretório: {os.path.dirname(file_path)}")
    #             else:
    #                 os.remove(file_path)
    #                 print(f"Removido: {file_path}")
    # return 0

import os
import shutil

def main(test_folder=None):
    grafs_folder = os.path.dirname(os.path.abspath(__file__))
    if test_folder is None:
        test_folder = os.path.join(grafs_folder, "principais", "test")
        
    if os.path.exists(test_folder):
        for filename in os.listdir(test_folder):
            file_path = os.path.join(test_folder, filename)
            
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Deletes folder and EVERYTHING inside it safely
                print(f"Removido diretório: {file_path}")
            else:
                os.remove(file_path)
                print(f"Removido: {file_path}")
    return 0

if __name__ == "__main__":
    main()