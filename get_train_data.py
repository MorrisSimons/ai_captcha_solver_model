import os
import time
import itertools
import string
import config as config
import hashlib

def get_files(path):
    """Returns a list of files in a directory"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def send_discord_img(img, value, operation_time):
    from discord_webhook import DiscordWebhook, DiscordEmbed
    webhook = DiscordWebhook(url=config.DICSWEBHOOKAICHAT)
    with open (f"{config.DATA_DIR}/{img}", "rb") as f:
        webhook.add_file(file=f.read(), filename="filename.png")
    embed = DiscordEmbed(title=f'{value}', description=f'New data added to training data, time {operation_time:.2f} sec', color=242424)
    embed.set_thumbnail(url=f"attachment://filename.png")
    webhook.add_embed(embed)
    print(webhook.execute())

def get_train_data():
    for file in get_files(config.UNLABELD_DIR):
        """loop through the files in the captcha directory"""
        print(f"[Prossesning]: {file}")
        hash_value = file.split(".png")[0][4:] #get the hash value from file name
        start = time.perf_counter()
        for guess in itertools.product(string.ascii_lowercase + string.digits, repeat=5): #generate all possible combinations
            unhashed_guess = ''.join(guess)
            
            hashed_guess = hashlib.sha1(unhashed_guess.encode()).hexdigest()
            print(f"Guess: {unhashed_guess} Hash: {hashed_guess}")
            if hashed_guess == hash_value: #if hash values match
                os.rename(f"{config.UNLABELD_DIR}{file}", f"{config.DATA_DIR}{unhashed_guess}_{hash_value}.png") #relabel the file and move file
                print(f"[+] New data added {unhashed_guess}_{hash_value}.png")
                end = time.perf_counter() - start
                print(f"Time taken: {end:.4f}s")
                send_discord_img(f"{unhashed_guess}_{hash_value}.png", unhashed_guess, operation_time=end)
                with open("log.txt", "a") as f: #log time taken
                    f.write(f"{end:.2f},")
                break
if __name__ == "__main__":
    get_train_data()