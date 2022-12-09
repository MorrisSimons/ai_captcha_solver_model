import os
import time
import random
import string
import config
PROCESSFILEPATH = "./worker_data/processing"

def get_files(path):
    """Returns a list of files in a directory"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def get_sha1_value(data):
    """Returns a SHA1 hash of the data"""
    import hashlib
    encoded_data = data.encode()
    return hashlib.sha1(encoded_data).hexdigest()

def label_data(file, slow_value,hashvalue,worker):
    """labels the the files in the captcha directory"""
    print("Labeling data...")
    os.rename(f"{PROCESSFILEPATH}{worker}/{file}", f"{PROCESSFILEPATH}{slow_value}_{hashvalue}.png")
    return f"{slow_value}_{hashvalue}.png"

def move_to_training_file(file,worker):
    """moves the files to the training directory"""
    print("Moving to training directory...")
    parent_path= os.path.dirname(os.getcwd())
    os.rename(f"{PROCESSFILEPATH}{worker}/{file}", f"{parent_path}/training/{file}")

def move_to_processing_file(file,worker):
    """moves the files to the processing directory"""
    print(f"Moving to processing directory for worker[{worker}]...")
    os.rename(f"./captcha/{file}", f"{PROCESSFILEPATH}{worker}/{file}")

def send_discord_img(img, value, operation_time):
    from discord_webhook import DiscordWebhook, DiscordEmbed
    webhook = DiscordWebhook(url=config.discord_webhookurl)
    with open (f"./training/{img}", "rb") as f:
        webhook.add_file(file=f.read(), filename="filename.png")
    embed = DiscordEmbed(title=f'{value}', description=f'New data added to training data, time {operation_time:.2f} sec', color=242424)
    embed.set_thumbnail(url=f"attachment://filename.png")
    webhook.add_embed(embed)
    print(webhook.execute())

def send_discord_message(message):
    import requests
    import json
    """Sends a discord message"""
    url = config.discord_webhookurl
    payload = json.dumps({"content": f"{message}"})
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text.encode('utf8'))

def get_train_data(worker):
    try:
        print(f"worker {worker} started")
        if not os.path.exists(f"{PROCESSFILEPATH}{worker}"):
            print(f"Creating processing directory for worker: {worker}...")
            os.makedirs(f"{PROCESSFILEPATH}{worker}")
        for file in get_files('./captcha'):
            move_to_processing_file(file,worker)
            for file in get_files(f'{PROCESSFILEPATH}{worker}'):
                """loop through the files in the captcha directory"""
                print(f"Processing {file}")
                hash_value = file.split(".png")[0][4:]
                print(f"Hash value: {hash_value}")
                is_vaild = True
                start = time.perf_counter()
                while is_vaild:
                    slow_value = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
                    #slow_value = input("Enter the value: ") #for testing
                    ai_guess = get_sha1_value(slow_value)
                    if ai_guess == hash_value:
                        """if the ai guess is correct, relabel and move the file to the training directory"""
                        print("AI guess is correct!")
                        move_to_training_file(label_data(file, slow_value, hash_value,worker),worker)
                        print(f"[+] New data added {slow_value}_{hash_value}.png")
                        is_vaild = False
                        end = time.perf_counter() - start
                        print(f"Time taken: {end:.4f}s")
                        send_discord_img(f"{slow_value}_{hash_value}.png", slow_value, operation_time=end)
    except Exception as e:
        msg = "ERROR OCCURED: " + str(e)
        send_discord_message(msg)
        
def multi_threading():
    import threading
    threads = []
    for worker in range(os.cpu_count()):
        thread = threading.Thread(target=get_train_data, args=(worker,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

if not os.path.exists(f"./worker_data"):
    print(f"Creating workspace for worekers...")
    os.makedirs(f"./worker_data")


multi_threading()