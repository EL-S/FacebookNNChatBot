# -*- coding: UTF-8 -*-

from fbchat import log, Client, Message, TypingStatus
from chatbotnn import *
from random import randint
import time
import threading
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from collections import OrderedDict

resumed_id, paused_id = [], []
paused = False
prev_time = time.time()
prev_wait_time = 0
time_since = 120
typing_time = 0
message_time_sent = False
grace_period = True
grace_timestamp = None
additional_wait = 0
grace_time = 0
c = 0
recent_message_time = {}
recent_message_wait_time = {}

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
            self.send_async_message(author_id, message_object, thread_id, thread_type, reply, typing_time, **kwargs)
        elif (not is_command):
            neuralnetworkresponse(self, author_id, message_object, thread_id, thread_type, admin, **kwargs)
            print("not a command, handle it as a message instead")
        else:
            print("it was a command and handled already")
            self.read_message_function(author_id, message_object, thread_id, thread_type, reply, admin, **kwargs)

    def read_message_function(self, author_id, message_object, thread_id, thread_type, reply, admin, **kwargs):
        self.markAsRead(thread_id)

    def send_async_message(self, author_id, message_object, thread_id, thread_type, reply, typing_time=0, **kwargs):
        # Will set the typing status of the thread to `TYPING`
        client.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
        time.sleep(typing_time) #type for a realistic time, if it types for too long, I need to recall it because it times out
        self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)

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
                    value = func(self, author_id, message_object, thread_id, thread_type, arguments, admin) #evaluates function called by sring and stores its return value
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
        prefix = "Status:\n"
        self.send(Message(text=prefix+resumed_list+paused_list+suffix), thread_id=thread_id, thread_type=thread_type)
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
    c = 0
    youtube_videos = []
    for i in youtube_vids: # super inefficient but I'm lazy
        if (i.get("href")[:9] == "/watch?v="):
            if c == 0:
                first_video = "https://www.youtube.com"+i.get("href")
            else:
                youtube_videos.append("https://www.youtube.com"+i.get("href"))
            c += 1
    c = 0
    youtube_videos = list(set(youtube_videos))
    for i in youtube_videos:
        if c == 0:
            youtube_vid_message = "First Result:\n\n"+first_video+"\n\nMore Results:\n\n"+i+"\n\n"
        elif c < 5:
            youtube_vid_message += i+"\n\n"
        c += 1
    client.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
    self.send(Message(text=youtube_vid_message), thread_id=thread_id, thread_type=thread_type)

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

def neuralnetworkresponse(self, author_id, message_object, thread_id, thread_type, admin, **kwargs):
    global paused_id, resumed_id, paused, recent_message_time, recent_message_wait_time
    if (thread_id in paused_id) or ((paused == True) and (thread_id not in resumed_id)):
        status = False
    else: #if it's not in paused or if it is globally paused and this thread is resumed
        status = True #send message confirmed
    
    if (author_id != self.uid) and (status == True): #only processes the messages if not paused
        current_time = time.time()
        #if time_since < prev_wait_time: #handle all these variables on a user by user basic in a dict maybe
        #    additional_wait = prev_wait_time - time_since + typing_time
        print("H:",message_object.text)
        reply = chatbot_recieve(message_object.text)
        try:
            time_since = current_time - recent_message_time[thread_id]
            min_wait_time = recent_message_wait_time[thread_id]
        except Exception as e:
            #there is no current previous message
            time_since = -1*randint(3,4)
            min_wait_time = randint(10,13) #this is first messaged recieved, so wait a bit
        if time_since < 0:
            wait_for = int(-1*time_since)
        else:
            wait_for = int(min_wait_time)
        print(min_wait_time,time_since)
        if wait_for < 0:
            #print(wait_for) #message already sent
            wait_for = 0
        #fine so far
        lower_bound_sleep = len(reply)*139 #139 ms between each character on avg
        upper_bound_sleep = int(lower_bound_sleep * 1.5) #gives the upper value for a slower type
        typing_time = int(randint(lower_bound_sleep,upper_bound_sleep)/1000)
        if typing_time > 30:
            typing_time = typing_time/2
        if typing_time > 60:
            typing_time = typing_time/2
        #problem?
        if time_since < 0: #problem
            time_since = 0
        wait_time = randint(int(wait_for),int(wait_for+10+(time_since/2))) #calculates a random wait time based on how long since the last message was recieved
        recent_message_wait_time[thread_id] = wait_time + typing_time #how long this message will take to send
        new_wait_for = wait_time + typing_time
        recent_message_time[thread_id] = current_time + new_wait_for #when the message should have been recieved
        t = threading.Timer(wait_time, ChatBot.send_async_message, [self, author_id, message_object, thread_id, thread_type, reply, typing_time])
        t.start()  # after wait_for seconds, the message will be sent
        read_wait = int(wait_time/2)
        print("Wait For:", wait_for, "Wait Time:", wait_time,"Seen wait:",read_wait, "Type Time:", typing_time)
        read_message = threading.Timer(read_wait, ChatBot.read_message_function, [self, author_id, message_object, thread_id, thread_type, reply, admin])
        read_message.start()

client = ChatBot("", "")
client.listen()
