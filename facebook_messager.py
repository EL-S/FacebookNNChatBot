# -*- coding: UTF-8 -*-

from fbchat import log, Client, Message, TypingStatus
from chatbotnn import *
from random import randint
import time
import threading

message_time_sent = False
time_since = 120
grace_period = True
grace_time = 0
grace_timestamp = None
c = 0
prev_time = time.time()
prev_wait_time = 0
additional_wait = 0
   

# Subclass fbchat.Client and override required methods
class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        global message_time_sent, time_since, grace_period, grace_time, grace_timestamp, c, prev_time, prev_wait_time, additional_wait
        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        
        # If you're not the author, echo
        if author_id != self.uid:
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
  
client = EchoBot("email", "password")
client.listen()
