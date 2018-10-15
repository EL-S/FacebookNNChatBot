# -*- coding: UTF-8 -*-

from fbchat import log, Client, Message, TypingStatus
from chatbotnn import *
from random import randint
import time
import threading
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

message_time_sent = False
time_since = 120
grace_period = True
grace_time = 0
grace_timestamp = None
c = 0
prev_time = time.time()
prev_wait_time = 0
additional_wait = 0
paused = False
paused_id = []
resumed_id = []
paused_thread = False
status = False


# Subclass fbchat.Client and override required methods
class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        global message_time_sent, time_since, grace_period, grace_time, grace_timestamp, c, prev_time, prev_wait_time, additional_wait, paused, resumed_id, paused_id
        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        
        # If you're not the author, echo
        if author_id == self.uid:
            if (message_object.text.lower() == "!pause"):
                if thread_id not in paused_id:
                    if thread_id in resumed_id:
                        resumed_id.remove(thread_id)
                    paused_id.append(thread_id)
                    self.send(Message(text="paused!"), thread_id=thread_id, thread_type=thread_type)
            elif (message_object.text.lower() == "!resume"):
                if thread_id not in resumed_id:
                    if thread_id in paused_id:
                        paused_id.remove(thread_id)
                    resumed_id.append(thread_id)
                    self.send(Message(text="resumed!"), thread_id=thread_id, thread_type=thread_type)
            elif (message_object.text.lower() == "!pause all"):
                paused = True
                self.send(Message(text="paused all!"), thread_id=thread_id, thread_type=thread_type)
            elif (message_object.text.lower() == "!resume all"):
                paused = False
                self.send(Message(text="resumed all!"), thread_id=thread_id, thread_type=thread_type)
            elif (message_object.text.lower() == "!resume all f"):
                paused = False
                paused_id = []
                self.send(Message(text="force resumed all!"), thread_id=thread_id, thread_type=thread_type)
            elif (message_object.text.lower() == "!pause all f"):
                paused = True
                resumed_id = []
                self.send(Message(text="force paused all!"), thread_id=thread_id, thread_type=thread_type)
            elif (message_object.text.lower() == "!status"):
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
            try:
                if (message_object.text.lower().split(" ")[0] == "!yt"):
                    youtube_link = "https://www.youtube.com/results?search_query="
                    suffix = ""
                    for x in message_object.text.lower().split(" "):
                        if x != "!yt":
                            suffix += "+"+x
                    suffix = suffix[1:]
                    url = youtube_link+suffix
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
            except:
                self.send(Message(text="ono there was a wiw fuckie wuckie uwu!!"), thread_id=thread_id, thread_type=thread_type)

        if (thread_id in paused_id) or ((paused == True) and (thread_id not in resumed_id)):
            status = False
        else: #if it's not in paused or if it is globally paused and this thread is resumed
            status = True #send message confirmed
        
        print(paused, paused_thread, status)
        if (author_id != self.uid) and (status == True): #only processes the messages if not paused
            current_time = time.time()
            if time_since < prev_wait_time:
                additional_wait = prev_wait_time - time_since
            print("H:",message_object.text)
            reply = chatbot_recieve(message_object.text)
            if message_time_sent:
                time_since = current_time - message_time_sent
                print(time_since)
            if grace_period == False:
                wait_for = randint(1,2) + additional_wait
                print(wait_for)
                t = threading.Timer(wait_for, send_async_message, [self, author_id, message_object, thread_id, thread_type, reply])
                t.start()  # after wait_for seconds, the message will begin to be sent
            elif time_since < 60:
                wait_for = randint(3,5) + additional_wait
                print(wait_for)
                t = threading.Timer(wait_for, send_async_message, [self, author_id, message_object, thread_id, thread_type, reply])
                t.start()  # after wait_for seconds, the message will begin to be sent
            else:
                wait_for = randint(5,8) + additional_wait
                print(wait_for)
                t = threading.Timer(wait_for, send_async_message, [self, author_id, message_object, thread_id, thread_type, reply])
                t.start()  # after wait_for seconds, the message will begin to be sent
            read_message = threading.Timer(int(wait_for/2), read_message_function, [self, author_id, message_object, thread_id, thread_type, reply])
            print("Seen wait:",int(wait_for/2))
            read_message.start()
            grace_period = False
            grace_time = randint(12,30)
            grace_timestamp = time.time()
            print("Grace_time:",grace_time)
            count_down = threading.Timer(grace_time, grace_period_counter)
            count_down.start()
            c = 0
            prev_time = time.time()
            prev_wait_time = wait_for

def read_message_function(self, author_id, message_object, thread_id, thread_type, reply, **kwargs):
    self.markAsRead(thread_id)

def send_async_message(self, author_id, message_object, thread_id, thread_type, reply, **kwargs):
    # Will set the typing status of the thread to `TYPING`
    client.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
    lower_bound_sleep = len(reply)*139 #ms between each character on avg
    upper_bound_sleep = int(lower_bound_sleep * 1.5)
    time.sleep(randint(lower_bound_sleep,upper_bound_sleep)/1000) #type for a realistic time
    self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)
    message_time_sent = time.time()

def grace_period_counter():
    global grace_period, grace_timestamp, grace_time, c
    if (time.time() - grace_timestamp) >= grace_time and c == 0:
        print("Grace time over")
        grace_period = True
        c += 1

client = EchoBot("", "")
client.listen()
