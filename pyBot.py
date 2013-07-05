import traceback
import sys
import socket
import string
import urllib2
import signal
import re
import ConfigParser

from bs4 import BeautifulSoup
from time import sleep

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

def connect():
    print("Connecting to : %s on port %i" % (HOST, PORT))
    global s
    s=socket.socket()
    s.connect((HOST, PORT))

    print("Setting NICK")
    s.send("NICK %s\r\n" % NICK)

    readbuffer=s.recv(1024)
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

def read_config():
    config = ConfigParser.RawConfigParser()
    config.read('bot.cfg')

    global HOST, PORT, LOBBY, NICK, IDENT, REALNAME
    HOST=config.get('Bot', 'host')
    PORT=config.getint('Bot', 'port')
    LOBBY=config.get('Bot', 'lobby')
    NICK=config.get('Bot', 'nick')
    NICKALTER=config.get('Bot', 'nickAlternate')
    IDENT=config.get('Bot', 'ident')
    REALNAME=config.get('Bot', 'realname')

def get_commands():
    while 1:
        try:
            readbuffer=s.recv(1024)
            sBuff=string.split(readbuffer, "\n")
            readbuffer=sBuff.pop( )

            for line in sBuff:
                line=string.rstrip(line)
                line=string.split(line)
                #print(line)

                if(line[0]=="PING"):
                    print("Sending pong")
                    s.send("PONG %s\r\n" % line[1])

                if(line[1]=="PRIVMSG"):
                    # Get command string
                    command = line[3]
                    command = command.replace(":","")
                    
                    # Get nickname of user who typed the command
                    nickname = line[0]
                    nickname = nickname.replace(":", "")
                    nickname = nickname[:nickname.find("!")]
                    
                    # Get channel or username of chat in which the command was entered
                    chat = line[2]
                    
                    if(command.upper() == "~HELP"):
                        print("Help command from " + nickname + " in chat with " + chat)
                        HELP()

                    if(command.upper() == "~BI"):
                        print("BI command from " + nickname + " in chat with " + chat)
                        BI()

                    if(command.upper() == "~UD"):
                        print("UD command from " + nickname + " in chat with " + chat)
                        UD()

                    if(command.upper() == "~UDD"):
                        if(len(line) >= 5):
                            print("UDD command with arg \"" + line[4] + "\" from " + nickname + " in chat with " + chat)
                            UDD(' '.join(line[4:]).strip())
                        else:
                            print("UDD command with no arg from " + nickname + " in chat with " + chat)
                            s.send("PRIVMSG %s :No keyword entered. Try again\r\n" % chat)
                            # NOTE: Could simply merge UD and UDD user commands so that if the user puts an argument to ~UD, he gets the definition, and no argument gets a random definition.

        except SystemExit:
            sys.exit(0)

        except:
            print("Error - ", sys.exc_info()[0], sys.exc_info()[1])
            s.send("PRIVMSG %s :(eror 0x2381ff64) Look at that pipe, it's broken. Try again.\r\n" % LOBBY)

def main():   
    signal.signal(signal.SIGINT, signal_handler)
    read_config()
    connect()
    get_commands()

if __name__=="__main__":
    main()
