import sqlite3 as sqlite
import telebot
from multiprocessing import Process
from time import sleep
import re
from datetime import datetime, date, time, timedelta
from telebot import types
from peewee import *
import config as cfg 
import strings as s
from models import User, Schedule
from functions import analyze
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

bot = telebot.TeleBot(cfg.token)


sid = lambda m: m.chat.id # лямбды для определения адреса ответа
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id



# messages

# def send_stat()

def stat_for_chat(m):
	today = date.today()
	monday = today  + timedelta(days = - today.weekday())
	response = ''
	users = Schedule.select(fn.Distinct(Schedule.user_id), User).join(User, on=(Schedule.user_id == User.user_id).alias('user')).where(Schedule.day >= monday)
	for u in users:
		response += "\n*{}* @{} *{}* работал на этой неделе:\n".format(u.user.first_name, u.user.username, u.user.last_name)
		for s in Schedule.select().where(Schedule.user_id == u.user_id, Schedule.day >= monday):
			response += "{} {} {}".format(s.day.strftime("%A, "), s.arrival_time.strftime("c %H:%M"), s.departure_time.strftime(" до %H:%M \n"))

	bot.send_message(sid(m), response, parse_mode='Markdown')



def stat_for_user(m):
	today = date.today()
	monday = today  + timedelta(days = - today.weekday())
	response = 'На этой неделе Вы работали: \n\n'
	schedule = Schedule.select().where(Schedule.user_id == uid(m), Schedule.day >= monday)
	if not schedule:
		response = 'На этой неделе Вы не работали'
	for s in schedule:
		response += "{} {} {}".format(s.day.strftime("%A, "), s.arrival_time.strftime("c %H:%M"), s.departure_time.strftime(" до %H:%M \n"))
	bot.send_message(uid(m), response)


# ________


@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)
	Schedule.create_table(fail_silently = True)


@bot.message_handler(commands = ['ping'])
def ping(m):
	bot.send_message(sid(m), "I'm alive")


@bot.message_handler(commands = ['gen'])
def gen(m):
	Schedule.gen_schedule(uid(m))


@bot.message_handler(commands = ['start'])
def start(m):
	User.cog(m)



@bot.message_handler(commands = ['stat'])
def stat(m=None):
	if m.chat.type == 'private':
		stat_for_user(m)
	else:
		stat_for_chat(m)


@bot.message_handler(content_types = ['text'])
def reply(m):
	u = User.cog(m)
	action = analyze(m.text)
	if action == 'stat':
		stat(m)
	elif action == 'arrival':
		if u.arrive():
			bot.send_message(sid(m), 'Привет, {}!'.format(m.from_user.first_name))
	elif action == 'departure':
		if u.depart():
			bot.send_message(sid(m), 'Пока, {}!'.format(m.from_user.first_name))



class Watcher:
	def __call__(self):
		check_time = time(21, 0)
		while True:
			if datetime.today().weekday() == 4:
				now = datetime.now().time()
				now = now.replace(microsecond = 0)
				if now == check_time:
					stat()
			sleep(1)




if __name__ == '__main__':
	watcher = Watcher()
	w = Process(target = watcher)
	w.start()

	bot.polling(none_stop=True)