import os
def get_files(path):
    """Returns a list of files in a directory"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def get_answer(file):
    hash_value = file.split(".png")[0][6:]
    answer = file.split(".png")[0][0:5]
    print(f"Hash value: {hash_value}")
    print(f"Answer: {answer}")
    return answer

def rename_file(file, answer):
    os.rename(f"./training/{file}", f"./training/{answer}.png")

def loop_through_files():
    for file in get_files('./training'):
        """loop through the files in the captcha directory"""
        print(f"[Renamed]: {file}")
        answer = get_answer(file)
        rename_file(file, answer)

loop_through_files()