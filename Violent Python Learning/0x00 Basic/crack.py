#!/usr/bin/python
#*- coding:utf-8 -*
#crypt must be run on linux or unix#

import crypt
import os

def testPass(salt,cryptPass):
    dictFile = open('dictionary.txt')
    for word in dictFile.readlines():
        word = word.strip('\n')
        dicPasswd = crypt.crypt(word,'$6$%s$' % salt)
        if(dicPasswd == cryptPass):
            print "[+] Found Password: "+word+"\n"
            return
    print "[-] Password Not Found.\n"
    return


def main():
    passFile = open(os.path.expanduser("/etc/shadow"))
    for line in passFile.readlines():
        if "$" in line:
            user = line.split(":")[0]
            cryptPass = line.split(":")[1].strip(' ')
            salt = cryptPass.split('$')[-2]
            print "[*] Cracking Password For: "+user
            testPass(salt,cryptPass)
if __name__ == "__main__":
    main()
