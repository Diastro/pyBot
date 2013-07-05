import traceback
import sys
import socket
import string
import urllib2
import signal
import re
import ConfigParser
import os
#import psutil
import platform

from bs4 import BeautifulSoup
from time import sleep

def BI(keyword):
    chat = str(keyword)
    
    url = "http://www.businessinsider.com"
    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data)
    stories = bs.find("div", {"class": "river"})
    titles = stories.find_all("a", {"class": "title"})

    print("Sending BI top stories.")
    for index, title in enumerate(titles):
        if index >= 5:
                break
        s.send("PRIVMSG %s :%s\r\n" %  (chat, (title.get_text()).encode('ascii', 'ignore')))

def UD(keyword):
    chat = str(keyword)
    
    url = "http://www.urbandictionary.com/random.php"
    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data)

    body = bs.find("td", {"id": "middle_column"})
    word = body.find("td", {"class": "word"})
    word = word.find("span").get_text()
    definition = body.find("div",{"class": "definition"}).get_text()

    word = word.strip()
    definition = definition.strip()
    s.send("PRIVMSG %s :%s : %s\r\n" % (chat, word, definition))

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

def ABOUT(keyword):
    chat = str(keyword)
    
    #pid = os.getpid()
    #p = psutil.Process(pid)
    #cpu = p.get_cpu_percent(interval=1.0)
    #mem = p.get_memory_percent()
    sys = platform.system()
    #ver = platform.version()
    layout = platform.machine()
    s.send("PRIVMSG %s : %s v%s\r\n" % (chat, NICK, VERSION))
    s.send("PRIVMSG %s : I'm running on %s (%s).\r\n" % (chat, sys, layout))
    #s.send("PRIVMSG %s : Currently using %0.2f%% of the CPU and %0.2f%% of RAM.\r\n" % (LOBBY, cpu, mem))


def HELP(keyword):
    chat = str(keyword)
    
    #BI
    command = "~BI"
    s.send("PRIVMSG %s : Top Business Insider Stories. %s\r\n" % (chat, command))

    #UD
    command = "~UD"
    s.send("PRIVMSG %s : Gives a random Urban Dictionary definition. %s\r\n" % (chat, command))

    #UDD
    command = "~UDD _keyword_"
    s.send("PRIVMSG %s : Returns the Urban Dictionnary Definition of a specific word. %s\r\n" % (chat, command))

    #JOIN
    command = "~JOIN"
    s.send("PRIVMSG %s : Joins the specified channel. %s\r\n" % (chat, command))
    
    #PART
    command = "~PART"
    s.send("PRIVMSG %s : Parts the channel in which the command was typed. %s\r\n" % (chat, command))
    

def JOIN(keyword): # Join a channel
    if(str(keyword) is None):
        keyword = LOBBY
    
    # Join lobby
    print("Joining: %s" % keyword)
    s.send("JOIN %s\r\n" % keyword)

def PART(keyword): # Join a channel
    # TODO: Do nothing if keyword is empty.. but this should never happen.
    
    # Part channel where command was typed. Unless it's the lobby or a user chat.
    if(str(keyword)!=LOBBY):
        print("Parting: %s" % keyword)
        s.send("PART %s\r\n" % keyword)

def signal_handler(signal, frame):
    print("ByeBye")
    sys.exit(0)

def connect():
    print("Connecting to : %s on port %i" % (HOST, PORT))
    global s
    s=socket.socket()
    s.connect((HOST, PORT))
    
    print("Setting USER")
    s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
    
    print("Setting NICK")
    s.send("NICK %s\r\n" % NICK)

    # Check incoming socket buffer to see if the nickname has already been used.
    readbuffer=s.recv(1024)
    sBuff=string.split(readbuffer, "\n")
    readbuffer=sBuff.pop( )
    
    for line in sBuff:
        line=string.rstrip(line)
        line=string.split(line)
        print("LINE: " + line[0] + " " + line[1] + " " + line[2] + " " + line[3] + " " + line[4])
        if(line[0]=="PING"):
            s.send("PONG %s\r\n" % line[1])
            print("Sending initial pong")
        if(len(line) >= 5):
            if(line[4]==":Nickname"):
                s.send("NICK %s\r\n" % NICKALTER)
                print("Nickname " + NICK + " already taken. Trying alternate nickname " + NICKALTER + ".")

    # Re-Check the buffer for a new ping and an answer from our potential NICK change
    readbuffer=s.recv(1024)
    sBuff=string.split(readbuffer, "\n")
    readbuffer=sBuff.pop( )
    
    for line in sBuff:
        line=string.rstrip(line)
        line=string.split(line)
        if(line[0]=="PING"):
            s.send("PONG %s\r\n" % line[1])
            print("Sending initial pong")
    
    # Join lobby
    print("Joining: %s" % LOBBY)
    s.send("JOIN %s\r\n" % LOBBY)

def read_config():
    config = ConfigParser.RawConfigParser()
    config.read('bot.cfg')

    global HOST, PORT, LOBBY, NICK, NICKALTER, IDENT, REALNAME, VERSION
    HOST=config.get('Bot', 'host')
    PORT=config.getint('Bot', 'port')
    LOBBY=config.get('Bot', 'lobby')
    NICK=config.get('Bot', 'nick')
    NICKALTER=config.get('Bot', 'nickAlternate')
    IDENT=config.get('Bot', 'ident')
    REALNAME=config.get('Bot', 'realname')
    VERSION=config.get('Bot', 'version')

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
                        HELP(chat)

                    if(command.upper() == "~BI"):
                        print("BI command from " + nickname + " in chat with " + chat)
                        BI(chat)

                    if(command.upper() == "~UD"):
                        print("UD command from " + nickname + " in chat with " + chat)
                        UD(chat)

                    if(command.upper() == "~ABOUT"):
                        print("ABOUT command from " + nickname + " in chat with " + chat)
                        ABOUT(chat)

                    if(command.upper() == "~UDD"):
                        if(len(line) >= 5):
                            print("UDD command with arg \"" + line[4] + "\" from " + nickname + " in chat with " + chat)
                            UDD(' '.join(line[4:]).strip())
                        else:
                            print("UDD command with no arg from " + nickname + " in chat with " + chat)
                            s.send("PRIVMSG %s :No keyword entered. Try again\r\n" % chat)
                            # NOTE: Could simply merge UD and UDD user commands so that if the user puts an argument to ~UD, he gets the definition, and no argument gets a random definition.
                    
                    if(command.upper() == "~JOIN"):
                        if(len(line) >= 5):
                            print("JOIN command with arg \"" + line[4] + "\" from " + nickname + " in chat with " + chat)
                            JOIN(' '.join(line[4:]).strip())
                        else:
                            print("JOIN command with no arg from " + nickname + " in chat with " + chat)
                            s.send("PRIVMSG %s :No channel name entered. Try again\r\n" % chat)
                    
                    if(command.upper() == "~PART"):
                        print("PART command from " + nickname + " in chat with " + chat)
                        PART(chat)
        
        except SystemExit:
            sys.exit(0)

        except:
            print("Error - ", sys.exc_info()[0], sys.exc_info()[1])
            s.send("PRIVMSG %s :(error 0x2381ff64) Look at that pipe, it's broken. Try again.\r\n" % LOBBY)

def main():   
    signal.signal(signal.SIGINT, signal_handler)
    read_config()
    connect()
    get_commands()

if __name__=="__main__":
    main()
