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
import gdata.youtube # Install gdata and elementtree modules
import gdata.youtube.service

from bs4 import BeautifulSoup
from time import sleep

#
# Command definitions
#

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
    s.send("PRIVMSG %s : Returns the Urban Dictionary Definition of a specific word. %s\r\n" % (chat, command))

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

def YOUTUBE(fullLine, nickname, chat):
    print("Youtube reference from " + nickname + " in chat with " + chat)
    
    # Get starting position of the video ID
    youtubeRefPos = string.find(fullLine, "youtu.be/") # youtu.be/videoID
    if(youtubeRefPos != -1): # Found youtu.be/ link
        youtubeRefPos = youtubeRefPos + 9 # Get ID after the /
    else:
        youtubeRefPos = string.find(fullLine, "watch?v=") # youtube.com/watch?v=videoID&potential_other=stuff
        if(youtubeRefPos != -1): # Found youtube.com/ link
            youtubeRefPos = youtubeRefPos + 8 # Get ID after the watch?v=
    
    if(youtubeRefPos == -1):
        print("Youtube: couldn't find starting position of video ID. Aborting.")
        return # If we can't find the starting position of the ID, let's just abort now...
    
    # Get ending position of the video ID
    youtubeEndOfIDPos = string.find(fullLine, " ", youtubeRefPos)
    youtubeEndOfIDPosAlt = string.find(fullLine, "&", youtubeRefPos)
    if(youtubeEndOfIDPosAlt == -1): # There is no other information after watch?v=
        if(youtubeEndOfIDPos == -1):
            youtubeID = fullLine[youtubeRefPos:] # The eol delimits the video ID
        else:
            youtubeID = fullLine[youtubeRefPos:youtubeEndOfIDPos] # A space char delimits the video ID
    else:
        youtubeID = fullLine[youtubeRefPos:youtubeEndOfIDPosAlt] # A & char delimits the video ID
    
    # Retreive video information on youtube
    yt_service = gdata.youtube.service.YouTubeService()
    entry = yt_service.GetYouTubeVideoEntry(video_id=youtubeID)
    print("Youtube: reference found. Parsing video ID " + youtubeID + ".")
    
    # TODO: Error catching to display error message of invalid video ID
    
    # Print video information
    #print("Video title: %s" % entry.media.title.text)
    #print("Video length: %s" % entry.media.duration.seconds)
    #print("Video desc: %s" % entry.media.description.text[:75])
    s.send("PRIVMSG %s :Youtube: [Title] %s [Length] %ss [Desc] %s (...) \r\n" % (chat, entry.media.title.text, entry.media.duration.seconds, entry.media.description.text[:75])) # entry.media.description.text

#
# Connection definitions
#

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

def get_commands():
    while 1:
        try:
            readbuffer=s.recv(1024)
            sBuff=string.split(readbuffer, "\n")
            readbuffer=sBuff.pop( )

            for line in sBuff:
                fullLine = line # Save a copy of the full line for parsing references to things
                line=string.rstrip(line)
                line=string.split(line)
                #print(line)

                if(line[0] == "PING"):
                    print("Sending pong")
                    s.send("PONG %s\r\n" % line[1])

                if(line[1] == "PRIVMSG"):
                    # Get command string
                    command = line[3]
                    command = command.replace(":","")
                    command = command.upper()
                    
                    # Get nickname of user who typed the command
                    nickname = line[0]
                    nickname = nickname.replace(":", "")
                    nickname = nickname[:nickname.find("!")]
                    
                    # Get channel or username of chat in which the command was entered
                    chat = line[2]
                    
                    if(command == "~HELP"):
                        print("Help command from " + nickname + " in chat with " + chat)
                        HELP(chat)
                        continue

                    if(command == "~BI"):
                        print("BI command from " + nickname + " in chat with " + chat)
                        BI(chat)
                        continue

                    if(command == "~UD"):
                        print("UD command from " + nickname + " in chat with " + chat)
                        UD(chat)
                        continue

                    if(command == "~ABOUT"):
                        print("ABOUT command from " + nickname + " in chat with " + chat)
                        ABOUT(chat)
                        continue

                    if(command == "~UDD"):
                        if(len(line) >= 5):
                            print("UDD command with arg \"" + line[4] + "\" from " + nickname + " in chat with " + chat)
                            UDD(' '.join(line[4:]).strip())
                        else:
                            print("UDD command with no arg from " + nickname + " in chat with " + chat)
                            s.send("PRIVMSG %s :No keyword entered. Try again.\r\n" % chat)
                            # NOTE: Could simply merge UD and UDD user commands so that if the user puts an argument to ~UD, he gets the definition, and no argument gets a random definition.
                        continue
                    
                    if(command == "~JOIN"):
                        if(len(line) >= 5):
                            print("JOIN command with arg \"" + line[4] + "\" from " + nickname + " in chat with " + chat)
                            JOIN(' '.join(line[4:]).strip())
                        else:
                            print("JOIN command with no arg from " + nickname + " in chat with " + chat)
                            s.send("PRIVMSG %s :No channel name entered. Try again.\r\n" % chat)
                        continue
                    
                    if(command == "~PART"):
                        print("PART command from " + nickname + " in chat with " + chat)
                        PART(chat)
                        continue
                    
                    youtubeURLs = ["youtu.be/", "youtube.com/"]
                    if any(x in fullLine for x in youtubeURLs):
                        YOUTUBE(fullLine, nickname, chat)
                        continue
        
        except SystemExit:
            s.send("QUIT :(error 0xO0p51D13d) System Exit.\r\n")
            sys.exit(0)

        except:
            print("Error - ", sys.exc_info()[0], sys.exc_info()[1])
            s.send("PRIVMSG %s :(error 0x2381ff64) Look at that pipe, it's broken. Try again.\r\n" % LOBBY)

#
# Main
#

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

def main():   
    signal.signal(signal.SIGINT, signal_handler)
    read_config()
    connect()
    get_commands()

if __name__=="__main__":
    main()
	
