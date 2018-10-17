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
        global message_time_sent
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

def neuralnetworkresponse(self, author_id, message_object, thread_id, thread_type, admin, **kwargs):
    global paused_id, resumed_id, paused, prev_time, prev_wait_time, time_since, typing_time, message_time_sent, grace_period, grace_timestamp, additional_wait, wait_for
    if (thread_id in paused_id) or ((paused == True) and (thread_id not in resumed_id)):
        status = False
    else: #if it's not in paused or if it is globally paused and this thread is resumed
        status = True #send message confirmed
    
    if (author_id != self.uid) and (status == True): #only processes the messages if not paused
        current_time = time.time()
        if time_since < prev_wait_time: #handle all these variables on a user by user basic in a dict maybe
            additional_wait = prev_wait_time - time_since + typing_time
        print("H:",message_object.text)
        reply = chatbot_recieve(message_object.text)
        lower_bound_sleep = len(reply)*139 #ms between each character on avg
        upper_bound_sleep = int(lower_bound_sleep * 1.5)
        typing_time = randint(lower_bound_sleep,upper_bound_sleep)/1000
        if message_time_sent:
            time_since = current_time - message_time_sent
            print(time_since)
        if grace_period == False:
            wait_for = randint(1,2) + additional_wait
            print(wait_for)
            t = threading.Timer(wait_for, ChatBot.send_async_message, [self, author_id, message_object, thread_id, thread_type, reply, typing_time])
            t.start()  # after wait_for seconds, the message will begin to be sent
        elif time_since < 60:
            wait_for = randint(3,5) + additional_wait
            print(wait_for)
            t = threading.Timer(wait_for, ChatBot.send_async_message, [self, author_id, message_object, thread_id, thread_type, reply, typing_time])
            t.start()  # after wait_for seconds, the message will begin to be sent
        else:
            wait_for = randint(5,8) + additional_wait
            print(wait_for)
            t = threading.Timer(wait_for, ChatBot.send_async_message, [self, author_id, message_object, thread_id, thread_type, reply, typing_time])
            t.start()  # after wait_for seconds, the message will begin to be sent
        read_message = threading.Timer(int(wait_for/2), ChatBot.read_message_function, [self, author_id, message_object, thread_id, thread_type, reply, admin])
        print("Seen wait:",int(wait_for/2))
        read_message.start()
        grace_period = False
        grace_time = randint(12,30)
        grace_timestamp = time.time()
        print("Grace_time:",grace_time)
        count_down = threading.Timer(grace_time, ChatBot.grace_period_counter)
        count_down.start()
        c = 0
        prev_time = time.time()
        prev_wait_time = wait_for

client = ChatBot("", "")
client.listen()
