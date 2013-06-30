import traceback
import sys
import socket
import string
import urllib2
import signal
import re

from bs4 import BeautifulSoup

def BI():
    url = "http://www.businessinsider.com"
    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data)
    stories = bs.find("div", {"class": "river"})
    titles = stories.find_all("a", {"class": "title"})

    print("Sending BI top stories.")
    for index, title in enumerate(titles):
        if index >= 5:
                break
        s.send("PRIVMSG %s :%s\r\n" %  (LOBBY, (title.get_text()).encode('ascii', 'ignore')))

def UD():
    url = "http://www.urbandictionary.com/random.php"
    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data)

    body = bs.find("td", {"id": "middle_column"})
    word = body.find("td", {"class": "word"})
    word = word.find("span").get_text()
    definition = body.find("div",{"class": "definition"}).get_text()

    word = word.strip()
    definition = definition.strip()
    s.send("PRIVMSG %s :%s : %s\r\n" % (LOBBY, word, definition))

def UDD(keyword):
    if(str(keyword) is None):
        keyword = "pwned"
    if(str(keyword) == "pag"):
        keyword = "pwned"

    keyword = keyword.replace(" ", "+")
    url = "http://www.urbandictionary.com/define.php?term=" + str(keyword)
    print(url) #temp log
    data = urllib2.urlopen(url, timeout=3).read()
    bs = BeautifulSoup(data)

    body = bs.find("td", {"id": "middle_column"})
    word = body.find("td", {"class": "word"})

    if word is None:
        s.send("PRIVMSG %s :No definition found.\r\n" % LOBBY)
        return
    else:
        word = word.find("span").get_text()
        definition = body.find("div",{"class": "definition"}).get_text()

        word = word.strip()
        definition = definition.strip()
        s.send("PRIVMSG %s :%s : %s\r\n" % (LOBBY, word, definition))

def HELP():
    #BI
    command = "~BI"
    s.send("PRIVMSG %s : Top Business Insider Story %s\r\n" % (LOBBY, command))

    #UD
    command = "~UD"
    s.send("PRIVMSG %s : Gives a random Urban Dictionary definition %s\r\n" % (LOBBY, command))

    #UDD
    command = "~UDD _keyword_"
    s.send("PRIVMSG %s : Returns the Urban Dictionnary Definition of a specific word %s\r\n" % (LOBBY, command))

def signal_handler(signal, frame):
    print("ByeBye")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
HOST="localhost"
LOBBY="#step"
PORT=6667
NICK="PyPag"
IDENT="PyPag"
REALNAME="PyPag"
readbuffer=""

print("Connecting to : %s" % HOST)
s=socket.socket()
s.connect((HOST, PORT))

print("Setting NICK")
s.send("NICK %s\r\n" % NICK)

readbuffer=readbuffer+s.recv(1024)
sBuff=string.split(readbuffer, "\n")
readbuffer=sBuff.pop( )

for line in sBuff:
    line=string.rstrip(line)
    line=string.split(line)
    if(line[0]=="PING"):
        s.send("PONG %s\r\n" % line[1])
        print("Sending initial pong")

print("Setting USER")
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))

print("Joining: %s" % LOBBY)
s.send("JOIN %s\r\n" % LOBBY)

while 1:
    try:
        readbuffer=s.recv(1024)
        sBuff=string.split(readbuffer, "\n")
        readbuffer=sBuff.pop( )

        for line in sBuff:
            line=string.rstrip(line)
            line=string.split(line)

            if(line[0]=="PING"):
                print("Sending pong")
                s.send("PONG %s\r\n" % line[1])

            if(line[1]=="PRIVMSG"):
                command = line[3]
                command = command.replace(":","")
                if(command == "~HELP"):
                    print("Help")
                    HELP()

                if(command == "~BI"):
                    print("BI")
                    BI()

                if(command == "~UD"):
                    print("UD")
                    UD()

                if(command == "~UDD"):
                    print("UDD")
                    if(line[4] != None):
                        UDD(' '.join(line[4:]).strip())
                    else:
                        s.send("PRIVMSG %s : Non keyword. Try again" % LOBBY)

    except SystemExit:
        sys.exit(0)

    except:
        print("Error - ",sys.exc_info()[0], sys.exc_info()[1])
        s.send("PRIVMSG #step : (eror 0x2381ff64) Look at that pipe, it's broken. Try again.")
