import pprint
import mnemonic
import time

import bip32utils
import requests
import random
import os
from colored import fg, bg, attr
from decimal import Decimal
from multiprocessing.pool import ThreadPool as Pool
import threading
from Bip39Gen import Bip39Gen
from time import sleep
import ctypes
#from notifypy import Notify



timesl = 15 # задержка между запросами
token_bot = "" # создать бота и получить токен тут @BotFather
chat_id = "" #узнать ваш id можно в боте @userinfobot



class Settings():
    save_empty = "y"
    total_count = 0
    wet_count = 0
    dry_count = 0


def makeDir():
    path = 'results'
    if not os.path.exists(path):
        os.makedirs(path)


def userInput():

    timesltime = round(((60 / timesl) * 100)*60)
    timesltimed = timesltime * 24
    print("BitGen by congrammer")
    time.sleep(2)
    print("{}Скорость генирации : ~{}/час ~{}/день{}".format(bg("#5F00FF"), timesltime, timesltimed,attr("reset")))
    start()
    time.sleep(5)


def getInternet():
    try:
        try:
            requests.get('https://www.google.com')
        except requests.ConnectTimeout:
            requests.get('http://1.1.1.1')
        return True
    except requests.ConnectionError:
        return False


lock = threading.Lock()

if getInternet() == True:
    dictionary = requests.get(
        'https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt').text.strip().split('\n')
else:
    pass


def getBalance3(addr):


    try:
        response = requests.get(
            f'https://blockchain.info/multiaddr?active={addr}&n=1')

        return (
            response.json()
        )
    except:
        print('{}У тебя походу бан по ip{}'.format(fg("#FE672A"), attr("reset")))
        time.sleep(600)
        return (getBalance3(addr))



def generateSeed():
    seed = ""
    for i in range(12):
        seed += random.choice(dictionary) if i == 0 else ' ' + \
                                                         random.choice(dictionary)
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


def generateBd():
    adrBd = {}
    for i in range(100):
        mnemonic_words = Bip39Gen(dictionary).mnemonic
        addy = bip39(mnemonic_words)
        adrBd.update([(f'{addy}', mnemonic_words)])

    return adrBd


def listToString(s):
    # initialize an empty string
    str1 = "|"

    # return string
    return (str1.join(s))


def sendBotMsg(msg):
    if token_bot != "":
        try:
            url = f"chat_id={chat_id}&text={msg}"
            requests.get(f"https://api.telegram.org/bot{token_bot}/sendMessage", url)
        except:
            pass

def check():
    while True:

        bdaddr = generateBd()
        addys = listToString(list(bdaddr))
        balances = getBalance3(addys)
        colortmp = 1
        with lock:

            for item in balances["addresses"]:

                addy = item["address"]
                balance = item["final_balance"]
                received = item["total_received"]

                mnemonic_words = bdaddr[addy]
                if balance > 0:
                    msg = 'Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}'.format(balance, received,
                                                                                                  addy,
                                                                                                  mnemonic_words)
                    sendBotMsg(msg)
                    if colortmp == 1:
                        colortmp = 0
                        print('{}Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}{}'.format(fg("#008700"), balance, received, addy, mnemonic_words, attr( "reset")))
                    else:
                        colortmp = 1
                        print('{}Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}{}'.format(bg("#008700"), balance, received, addy, mnemonic_words, attr("reset")))
                    #notification = Notify()
                    #notification.title = f"Balance: {balance}"
                    #notification.message = f"Mnemonic phrase: {mnemonic_words}"
                    #notification.send()
                else:
                    if(received > 0):
                        msg = 'Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}'.format(balance, received,
                                                                                                      addy,
                                                                                                      mnemonic_words)
                        sendBotMsg(msg)
                        if colortmp == 1:
                            colortmp = 0
                            print('{}Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}{}'.format(
                                fg("#005FFF"), balance, received, addy, mnemonic_words, attr("reset")))
                        else:
                            colortmp = 1
                            print('{}Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}{}'.format(
                                bg("#005FFF"), balance, received, addy, mnemonic_words, attr("reset")))
                    else:
                        if colortmp == 1:
                            colortmp = 0
                            print('{}Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}{}'.format(fg("#FFFFFF"), balance, received, addy, mnemonic_words, attr("reset")))
                        else:
                            colortmp = 1
                            print('{}Balance: {} | Received: {} | Address: {} | Mnemonic phrase: {}{}'.format(fg("#000000")+bg("#808080"), balance, received, addy, mnemonic_words, attr("reset")))

                Settings.total_count += 1
                if Settings.save_empty == "y":
                    ctypes.windll.kernel32.SetConsoleTitleW(
                        f"Empty: {Settings.dry_count} - Hits: {Settings.wet_count} - Total checks: {Settings.total_count}")
                else:
                    ctypes.windll.kernel32.SetConsoleTitleW(
                        f"Hits: {Settings.wet_count} - Total checks: {Settings.total_count}")

                if balance > 0:
                    with open('results/wet.txt', 'a') as w:
                        w.write(
                            f'Address: {addy} | Balance: {balance} | Mnemonic phrase: {mnemonic_words}\n')
                        Settings.wet_count += 1
                else:
                    if Settings.save_empty == "n":
                        pass
                    else:
                        with open('results/dry.txt', 'a') as w:
                            w.write(
                                f'Address: {addy} | Balance: {balance} | Mnemonic phrase: {mnemonic_words}\n')
                            Settings.dry_count += 1
        time.sleep(timesl)


def helpText():
    print("""
This program was made by Anarb and it generates Bitcoin by searching multiple possible
wallet combinations until it's finds one with over 0 BTC and saves it into
a file called "wet.txt" in the results folder.
It's recommended to leave this running for a long time to get the best resaults, It's doesn't use up
that much resources so you can leave it in the background in the chance of you hitting a jackpot.
It's like mining but with less resources

=========================================================================================

start - Starts the program

=========================================================================================

More commands will be added soon plus other cryptocurrencies.
        """)


def start():
    try:
        threads = 1
        if threads > 666:
            print("You can only run 666 threads at once")
            start()
    except ValueError:
        print("Enter an interger!")
        start()
    Settings.save_empty = "n"
    if getInternet() == True:
        #notification = Notify()
        #notification.title = "main.py"
        #notification.message = "Mnemonic brut started ."
        #notification.send()
        pool = Pool(threads)
        for _ in range(threads):
            pool.apply_async(check, ())
        pool.close()
        pool.join()
    else:
        print("Told ya")
        userInput()


if __name__ == '__main__':
    makeDir()
    getInternet()
    if getInternet() == False:
        print("You have no internet access the generator won't work.")
    else:
        pass
    userInput()
