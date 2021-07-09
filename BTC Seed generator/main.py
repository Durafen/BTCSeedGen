import pprint
import binascii
import mnemonic
import bip32utils
import requests
import random
import os
from lmao import Bip39Gen
from decimal import Decimal
from multiprocessing.pool import ThreadPool as Pool
import threading
import time

lock = threading.Lock()

dictionary = requests.get('https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt').text.strip().split('\n')

addresses = {}
with open("btc_base58.txt") as file:
    for line in file:
        line = line.rstrip('\n')
        addresses[line] = 1
    file.close()

proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050',

}


def getBalance(addr):

    got_balance = False

    while not got_balance:
        try:
            response = requests.get(f'https://api.smartbit.com.au/v1/blockchain/address/{addr}', proxies=proxies)
            got_balance = True
            return (
                Decimal(response.json()["address"]["total"]["received"])
                / 100000000
            )
        except Exception as e:
            print(e)


def generateSeed():
    seed = ""
    for i in range(12):
        seed += random.choice(dictionary) if i == 0 else ' ' + random.choice(dictionary)
    return seed


def bip39(mnemonic_words):
    mobj = mnemonic.Mnemonic("english")
    seed = mobj.to_seed(mnemonic_words)

    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(
        44 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(0).ChildKey(0)

    return bip32_child_key_obj.Address()


def check():

#    count = 0
#    startTime = time.time()

    while True:
        mnemonic_words = Bip39Gen(dictionary).mnemonic
        addy = bip39(mnemonic_words)

#       count = count + 1
#        if count == 500:
#            executionTime = (time.time() - startTime)
#            print('Execution time in seconds: ' + str(executionTime))

#            os._exit(os.EX_OK)
#            print (f'exit')

        with lock:
            print(f'{addy} - {mnemonic_words}')

            if addresses.get(addy) == 1:
                print(f'Found!!!')
                print(f'\a')
                os._exit(os.EX_OK)


def start():
    threads = 1
    pool = Pool(threads)
    for _ in range(threads):
        pool.apply_async(check, ())
    pool.close()
    pool.join()


if __name__ == '__main__':
    start()
