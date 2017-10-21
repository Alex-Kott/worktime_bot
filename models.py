from peewee import *
from datetime import datetime, date, timedelta, time
import strings as s
from random import randint as rnd


sid = lambda m: m.chat.id # лямбды для определения адреса ответа
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id

db = SqliteDatabase('db.sqlite3')

class BaseModel(Model):
	class Meta:
		database = db


class User(BaseModel):
	user_id		= IntegerField(primary_key = True)
	username 	= TextField(null = True)
	first_name 	= TextField()
	last_name	= TextField(null = True)

	def cog(m):
		try:
			with db.atomic():
				return User.create(user_id = uid(m), username = m.from_user.username, first_name = m.from_user.first_name, last_name = m.from_user.last_name)
		except Exception as e:
			return User.select().where(User.user_id == uid(m)).get()

	def arrive(self):
		now = datetime.now()
		today = Schedule.get_today(self.user_id)
		if today.arrival_time == None:
			today.arrival_time = now.time()
			today.save()
			return True
		else:
			return False

	def depart(self):
		now = datetime.now()
		today = Schedule.get_today(self.user_id)
		if today.departure_time == None:
			today.departure_time = now.time()
			today.save()
			return True
		else:
			return False



	
class Schedule(BaseModel):
	user_id 		= IntegerField()
	day 			= DateField()
	arrival_time	= TimeField(null = True) 
	departure_time	= TimeField(null = True) 

	@staticmethod
	def get_today(user_id):
		today = date.today()
		try:
			with db.atomic():
				return Schedule.create(user_id = user_id, day = today)
		except Exception as e:
			return Schedule.select().where(Schedule.user_id == user_id, Schedule.day == today).get()

	
	@staticmethod
	def gen_schedule(user_id):
		today = date.today()
		day = today  + timedelta(days = - today.weekday())
		u = User.select().where(User.user_id == user_id).get()
		for i in range(6):
			try:
				Schedule.create(user_id = user_id, day = day, arrival_time = time(rnd(7, 14), rnd(0, 59)), departure_time = time(rnd(15, 21), rnd(0, 59)))
			except:
				return Schedule.select().where(Schedule.user_id == user_id, Schedule.day == day).get()
			day += timedelta(days = 1)



	class Meta:
		primary_key = CompositeKey('user_id', 'day')


