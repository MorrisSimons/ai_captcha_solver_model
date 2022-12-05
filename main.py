import hashlib
import os

def get_files(path):
    """Returns a list of files in a directory"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def get_sha1_value(data):
    """Returns a SHA1 hash of the data"""
    encoded_data = data.encode()
    return hashlib.sha1(encoded_data).hexdigest()

def get_ai_guess(filename):
    """Returns a string of 5 characters"""
    from PIL import Image
    im = Image.open(f"./captcha/{filename}", "r")
    pix_val = list(im.getdata())
    print(pix_val)

def get_captcha():
    for file in get_files('./training'):
        """loop through the files in the captcha directory"""
        print(f"Processing {file}")
        hash_value = file.split(".png")[0][6:]
        answer = file.split(".png")[0][0:5]
        print(f"Hash value: {hash_value}")
        is_vaild = True
        while is_vaild:
            ai_guess = get_ai_guess(file)
            ai_guess_sha1 = get_sha1_value(ai_guess)
            if ai_guess == hash_value:
                """if the ai guess is correct, relabel and move the file to the training directory"""
                print("Correct!")
                is_vaild = False
        print(f"right value: {answer}")
        print(f"ai guess: {ai_guess}")
        print(f"SHA1 value: {ai_guess_sha1}")
        print("Hashvalue: ", hash_value)

if __name__ == "__main__":
    get_captcha()
