import os


def main():
    grafs_folder = os.path.dirname(os.path.abspath(__file__))
    test_folder = os.path.join(grafs_folder, "principais", "test")
    if os.path.exists(test_folder):
        for filename in os.listdir(test_folder):
            file_path = os.path.join(test_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removido: {file_path}")
    return 0

if __name__ == "__main__":
    main()