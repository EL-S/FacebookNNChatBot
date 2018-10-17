# -*- coding: UTF-8 -*-

from fbchat import log, Client, Message, TypingStatus
from chatbotnn import *
from random import randint
import time
import threading
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote_plus

resumed_id, paused_id = [], []
paused = False

# Subclass fbchat.Client and override required methods
class ChatBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        
        # If you're the user, grant admin
        if author_id == self.uid:
            admin = True
        else:
            admin = False

        #time.sleep(1) #there needs to be some delay otherwise it doesn't "seen" it
        is_command, reply = self.check_for_command(author_id, message_object, thread_id, thread_type, admin, **kwargs)
        if (is_command) and (reply != ""):
            print(reply)
        elif (not is_command):
            print("not a command, handle it as a message instead")
        else:
            print("it was a command and handled already")
        self.read_message_function(thread_id, **kwargs)

    def read_message_function(self, thread_id, **kwargs):
        self.markAsRead(thread_id)

    def send_async_message(self, author_id, message_object, thread_id, thread_type, reply, typing_time, **kwargs):
        # Will set the typing status of the thread to `TYPING`
        client.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
        time.sleep(typing_time) #type for a realistic time, if it types for too long, I need to recall it because it times out
        self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)
        message_time_sent = time.time()

    def check_for_command(self, author_id, message_object, thread_id, thread_type, admin, **kwargs):
        commands = ["status","test","yt", "pause", "resume"]
        message = message_object.text.lower()
        if message[0] == "!": #it's a command
            command = message.split(" ")[0][1:]
            arguments = message.split(" ")[1:]
            print(arguments)
            if command in commands:
                try:
                    func = eval(command) # Get the function using a string name, Make sure the function is defined globally!!
                    value = func(self, author_id, message_object, thread_id, thread_type, admin, arguments) #evaluates function called by sring and stores its return value
                    return [True, ""]
                except Exception as e:
                    print(e)
                    reply = "ono there was a wiw fuckie wuckie executing the command uwu"
                    return [True, reply] #either the function doesn't exist or something went wrong handling the function
            else:
                reply = "That command doesn't exist"
                return [True, reply] #the command doesn't exist
        else:
            return [False,""] #it's not a command
    def grace_period_counter():
        global grace_period, grace_timestamp, grace_time, c
        if (time.time() - grace_timestamp) >= grace_time and c == 0:
            print("Grace time over")
            grace_period = True
            c += 1
def test(self, author_id, message_object, thread_id, thread_type, arguments, admin, **kwargs):
    print("lmao")

def status(self, author_id, message_object, thread_id, thread_type, arguments, admin, **kwargs):
    global resumed_id, paused_id, paused
    if admin:
        resumed_list = ""
        paused_list = ""
        for x in resumed_id:
            thread_name = client.fetchThreadInfo(x)[x].name
            resumed_list += thread_name+"\n"
        for y in paused_id:
            thread_name = client.fetchThreadInfo(y)[y].name
            paused_list += thread_name+"\n"
        if resumed_list != "":
            resumed_list = "Resumed: " + resumed_list
        if paused_list != "":
            paused_list = "Paused: " + paused_list
        if paused == True:
            suffix = "\nGlobally Paused"
        else:
            suffix = "\nGlobally Resumed"
        self.send(Message(text=resumed_list+paused_list+suffix), thread_id=thread_id, thread_type=thread_type)
    else:
        self.send(Message(text="You're not admin!"), thread_id=thread_id, thread_type=thread_type)

def yt(self, author_id, message_object, thread_id, thread_type, arguments, admin, **kwargs):
    youtube_link = "https://www.youtube.com/results?search_query="
    suffix = ""
    for x in arguments:
        suffix += "+"+x
    suffix = suffix[1:]
    url = quote_plus(youtube_link+suffix,"/:+?=")
    print(url)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    youtube_vids = soup.findAll('a')
    first = True
    for i in youtube_vids: # super inefficient but I'm lazy
        if (i.get("href")[:9] == "/watch?v=") and (first != False):
            youtube_vid = "https://www.youtube.com"+i.get("href")
            first = False
    client.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
    self.send(Message(text=youtube_vid), thread_id=thread_id, thread_type=thread_type)

def pause(self, author_id, message_object, thread_id, thread_type, arguments, admin, **kwargs):
    global paused_id, resumed_id, paused
    if admin:
        try:
            if arguments[0] == "all":
                try:
                    if arguments[1] == "f":
                        paused = True
                        resumed_id = []
                        paused_id = []
                        self.send(Message(text="force paused all!"), thread_id=thread_id, thread_type=thread_type)
                except:
                    paused = True
                    self.send(Message(text="paused all!"), thread_id=thread_id, thread_type=thread_type)
        except:
            if thread_id not in paused_id:
                if thread_id in resumed_id:
                    resumed_id.remove(thread_id)
                paused_id.append(thread_id)
                self.send(Message(text="paused!"), thread_id=thread_id, thread_type=thread_type)
    else:
        self.send(Message(text="You're not admin!"), thread_id=thread_id, thread_type=thread_type)
    
def resume(self, author_id, message_object, thread_id, thread_type, arguments, admin, **kwargs):
    global paused_id, resumed_id, paused
    if admin:
        try:
            if arguments[0] == "all":
                try:
                    if arguments[1] == "f":
                        paused = False
                        resumed_id = []
                        paused_id = []
                        self.send(Message(text="force resumed all!"), thread_id=thread_id, thread_type=thread_type)
                except:
                    paused = False
                    self.send(Message(text="resumed all!"), thread_id=thread_id, thread_type=thread_type)
        except:
            if thread_id not in resumed_id:
                if thread_id in paused_id:
                    paused_id.remove(thread_id)
                resumed_id.append(thread_id)
                self.send(Message(text="resumed!"), thread_id=thread_id, thread_type=thread_type)
    else:
        self.send(Message(text="You're not admin!"), thread_id=thread_id, thread_type=thread_type)

client = ChatBot("", "")
client.listen()
