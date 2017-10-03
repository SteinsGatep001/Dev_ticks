#coding:utf-8

import optparse
from socket import *
from threading import *

screenLock = Semaphore(value=1)
def connScan(tgtHost, tgtPort):
    try:
        connSkt = socket(AF_INET, SOCK_STREAM)
        connSkt.connect((tgtHost, tgtPort))
        connSkt.send('deadfish')
        results = connSkt.recv(100)
        # lock print
        screenLock.acquire()
        # print received data
        print '[+]%d/tcp open' % tgtPort
        print '[+] ' + str(results) + '\n'
    except:
        print '\n[-]%d/tcp closed' % tgtPort
    finally:
        # unlock print
        screenLock.release()
        connSkt.close()


def portScan(tgtHost, tgtPorts):
    try:
        tgtIp = gethostbyname(tgtHost)
    except:
        print "[-]Cannot resolve '%s': Unknown host"%tgtHost
        return
    try:
        tgtName = gethostbyaddr(tgtIp)
        print '\n[+] Scan Results for: ' + tgtName[0] + '\n'
    except:
        print '\n[+] Scan Results for: ' + tgtIp + '\n'
    setdefaulttimeout(1)
    for tgtPort in tgtPorts:
        # create thread to scan
        t = Thread(target=connScan, args=(tgtHost, int(tgtPort)))
        t.start()

def main():
    # args security check
    parser = optparse.OptionParser('usage %prog -H <target host> -p <target port>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-p', dest='tgtPort', type='string', help='specify port[s] by comma')
    (options, args) = parser.parse_args()
    tgtHost = options.tgtHost
    tgtPorts = (str(options.tgtPort).split(',', -1))
    if (tgtHost == None) | (tgtPorts[0] == None):
        print parser.usage
        exit(0)
    portScan(tgtHost, tgtPorts)

if __name__ == '__main__':
    main()