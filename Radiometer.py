# Radioscan - app is designed do display radioactivity interacting with arduino boards and its build in Geiger
# counter.
# features: - reading off sensor data from Geiger counter by ESP8266 board, treat and pass it to the
#             computer via pyserial having wireless bluetooth connection by using arduino bluetooth module  or via usb
#               connection.
#           - simultaneously pass data to database on cloud server to store it over there reach radioactivity data
#               from database by using request with desire time and date period
#           - hardware going to include gps module and retrieve coordinates data, pass it into database
#           - hardware is absolutely autonomic, has its own power source and needs only wi-fi connection
import asyncio
import re
import time

from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.core.text import LabelBase
import numpy as np
import pandas as pd
import serial
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager
from kivy_garden.graph import BarPlot, Graph, SmoothLinePlot, LinePlot, MeshLinePlot
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.textfield import MDTextField
from matplotlib import pyplot as plt
from numpy import random
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

LabelBase.register("TickingTimebombBB", fn_regular="C:/Users/admin/PycharmProjects/pythonProject2/ticking-timebomb-bb/TickingTimebombBB.ttf")

#class Arduino():
#	def read_data(self):
#		self.Arduino_Data = serial.Serial("com5", 9600)
#		self.read_data = self.Arduino_Data.readline()
#		self.read_data = self.read_data.decode()
#		print(self.read_data)
#		self.digits = re.findall(r"-?\d+\.\d+|-?\d+", self.read_data)
#		try:
#			self.read_data_t = self.digits[0]
#			self.read_data_t = float(self.read_data_t)
#
#			self.read_data_r = self.digits[1]
#			self.read_data_r = int(self.read_data_r)
#
#			self.read_data_lat = self.digits[2]
#			self.read_data_long = self.digits[3]
#
#		except:
#			print("error, wait...")
#		print("temp: " + str(self.read_data_t))
#		print("radiactivity: " + str(self.read_data_r))
#		print("coordinates: " + "lat: " + str(self.read_data_lat)+ "long: "+ str(self.read_data_long))
#class Arduino():
#	read_data: bytes
#
#	def __init__(self, **kwargs):
#		super(Arduino, self).__init__(**kwargs)
#
#		self.read_data()
#
#	def read_data(self):
#		self.Arduino_Data = serial.Serial("com5", 9600)
#		self.read_data = self.Arduino_Data.readline()
#		self.read_data = self.read_data.decode()
#		print(self.read_data)# ------------------------------------------------------------> to debug reading off
#		self.digits = re.findall(r"-?\d+\.\d+|-?\d+", self.read_data)
#		try:
#			self.read_data_t = self.digits[0]
#			self.read_data_t = float(self.read_data_t)
#
#			self.read_data_r = self.digits[1]
#			self.read_data_r = int(self.read_data_r)
#
#			self.read_data_lat = self.digits[2]
#			self.read_data_long = self.digits[3]
#
#		except:
#			print("error, wait...")
class Root(MDScreen):
	pass

class Real_time_activity(MDScreen):  # ------------> real time activity and displaying it on the screen

	seconds = NumericProperty(0)
	minutes = NumericProperty(0)
	hrs = NumericProperty(0)
	degr = NumericProperty(0)
	temp = NumericProperty(0)
	temperature = []
	radiation = []
	coordinates = []
	list_data = []
	angl = NumericProperty(0)
	rad_level = StringProperty(None)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.Img = Image(source="rad.png",
			pos_hint={"x": 0, "y": 0.025},
			size_hint=(0.05, 0.05))

		self.add_widget(self.Img)
		self.on_enter()
		#self.start_animation()

	def on_enter(self):
		try:
			self.Arduino_Data = serial.Serial("com5", 9600)      #com3 is used for USB connection with Arduino Mega 2560
			Clock.schedule_interval(self.reading_data, 1)
			Clock.schedule_interval(self.timer, 1)
			
			connected = True
		except serial.SerialException:
			Clock.schedule_once(self.retry_connection, 0.1)


	def retry_connection(self, dt):
		self.on_enter()

	def reading_data(self, dt):

		self.read_data = self.Arduino_Data.readline()
		self.read_data = self.read_data.decode()
		#print(self.read_data)              # ------------------------debugging  output

		self.digits = re.findall(r"-?\d+\.\d+|-?\d+", self.read_data)
		print(self.digits)
		try:
			self.read_data_t = self.digits[0]
			self.read_data_t = float(self.read_data_t)

			self.read_data_r = self.digits[1]
			self.read_data_r = int(self.read_data_r)

			self.read_data_lat = self.digits[2]
			self.read_data_long = self.digits[3]

		except:
			print("error")
		self.radiation.append(self.read_data_r)


		if len(self.radiation) > 25:
			self.radiation.pop(0)

		self.read_data_r = int(self.read_data_r)

		self.degr = self.read_data_r * 1000 / 235  # --------------> should be 100 instead

		self.ids.rad_level.text = str(self.read_data_r) + str(" Bq ")
		self.ids.temp_text.text = str(self.read_data_t) + " °C"
		rand = np.random.rand()
		rand = round(rand, 2)
		dose = sum(self.radiation)
		self.ids.radiation_dose.text = str(dose * 60)

		text_len = len(self.ids.radiation_dose.text)
		window_width = Window.width
		self.ids.grid_dose.size_hint_x = 0.2 + text_len / window_width
		self.ids.radiation_dose.size_hint_x = 0.08 + text_len * 100 / window_width

	def timer(self, dt):
		self.seconds += 1

		if self.seconds > 59:
			self.seconds = 0
			self.minutes += 1

		if self.minutes > 59:
			self.minutes = 0
			self.hrs += 1

		if self.hrs > 23:
			self.hrs = 0

		self.ids.timer.text = f'{self.hrs:02}:{self.minutes:02}:{self.seconds:02}'

	def on_leave(self):



		# time.sleep(1)
		Clock.unschedule(self.reading_data)
		Clock.unschedule(self.timer)
		time.sleep(0.25)
		self.Arduino_Data.close()


class Bar(MDScreen):  # ----------> real time plotting, bars are indicating radioactivity, as intensive it is, as higher
					# ------------>  bars are

	temperature = []
	radiation = []
	coordinates = []
	list_data = []
	hr = StringProperty(None)
	dialog = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.x_axes = []
		for i in range(24):
			self.x_axes.append(0)
		self.y_axes = []
		self.t = 0
		self.graph = Graph(xlabel='time',
			ylabel='Activity',
			border_color=(0, 0, 0, 1),
			label_options={'color': (0, 0, 0, 1)},
			x_ticks_minor=1,
			x_ticks_major=1,
			y_ticks_major=100,
			y_ticks_minor=0,
			y_grid_label=True, x_grid_label=False, padding=5,
			x_grid=False, y_grid=False, xmin=-0, xmax=20, ymin=0, ymax=1000,
			pos_hint={"x": 0, "y": 0},
			size_hint=(0.95, 0.85)
		)

		#self.plot2 = LinePlot(color=[1, 0, 0, 1], line_width=2) --------------------> line ploting interpretation
		self.plot = BarPlot(color=[0, 1, 0, 1], bar_spacing=10, bar_width=25)
		self.plot_x = self.x_axes
		self.plot_y = self.y_axes
		self.plot.color = [0, 1, 0, 1]
		#self.graph.add_plot(self.plot2)
		self.graph.add_plot(self.plot)
		self.add_widget(self.graph)

	def start_bar_plotting(self):
		try:
			self.Ard_Data = serial.Serial("com5", 9600) # com3 port for USB connection
			Clock.schedule_interval(self.on_start, 1)
			Clock.schedule_interval(self.update_axis, 1)
			Clock.schedule_interval(self.update_points, 1)

		except serial.SerialException:
			Clock.schedule_once(self.retry_connection, 0.1)

	def retry_connection(self, dt):
		self.start_bar_plotting()

	def bar_plot_stop(self):
		Clock.unschedule(self.on_start)
		Clock.unschedule(self.update_axis)
		Clock.unschedule(self.update_points)
		time.sleep(0.5)
		self.Ard_Data.close()

	def on_start(self, dt):
		self.read_data = self.Ard_Data.readline()
		self.read_data = self.read_data.decode()

		self.digits = re.findall(r"-?\d+\.\d+|-?\d+", self.read_data)
		#print(self.digits)   #-------------------> to debug output
		try:
			self.read_data_t = self.digits[0]
			self.read_data_t = float(self.read_data_t)

			self.read_data_r = self.digits[1]
			self.read_data_r = int(self.read_data_r)

			self.read_data_c = self.digits[2]

		except:
			self.read_data_r = 1
			self.read_data_t = 1
			self.read_data_c = 1

		self.radiation.append(self.read_data_r)
		# self.coordinates.append(self.read_data_c)
		# self.temperature.append(self.read_data_t)

		self.read_data_r = 60 * self.read_data_r
		self.y_axes.append(self.read_data_r)

		self.t += dt
		self.t = round(self.t)

		self.x_axes.append(self.t)

		if len(self.x_axes) > 25:
			self.x_axes.pop(0)

		#if len(self.y_axes) > 50:
		#	self.y_axes.pop(0)

		print(self.x_axes)
		print(self.y_axes)

	def update_axis(self, dt):
		self.graph.xmin = self.x_axes[0]
		self.graph.xmax = self.x_axes[-1]

	def update_points(self, args):
		self.plot.points = [(i, self.y_axes[i]) for i in range(len(self.y_axes))]
		#self.plot2.points = [(i, self.y_axes[i]) for i in range(len(self.y_axes))] -------------> line plotting
		# line above just to interpretate line ploting

class Time_picker(MDBoxLayout):
	pass


class Data_base(MDScreen):  # ----------> retrieving  data from web server, which are stored in database
	hr = StringProperty(None)
	dialog = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.url = 'http://radioscan.atwebpages.com/index.php'
		self.read_url = pd.read_html(self.url)
		self.radiation = self.read_url[0].Radiation
		self.time = self.read_url[0].Date
		# self.id = self.read_url[0].id
		self.temp = self.read_url[0].Temperature
		self.df = pd.DataFrame(self.read_url[0])  # ----------> extract table from url

	def load_data(self):  # ------------------> getting data from server
		self.df['Date'] = pd.to_datetime(self.df['Date'])
		self.start = str(self.start_time + self.begining)
		self.end = str(self.end_time + self.finish)
		start_date = pd.Timestamp(self.start)  # 2023-06-18 07:00
		end_date = pd.Timestamp(self.end)  # 2023-06-18 08:00
		#
		## Create a boolean mask to filter rows within the specified timestamp range
		self.mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
		#
		# Apply the mask to the DataFrame to retrieve the rows within the range
		filtered_df = self.df[self.mask]

		# plt.plot(filtered_df["Date"], filtered_df["Radiation"], label = "Radiation")
		x = np.array(filtered_df["Date"])
		y = np.array(filtered_df["Radiation"])
		z = np.array(filtered_df["Temperature"])

		fig, ax1 = plt.subplots(figsize=(7, 4))
		color = "tab:green"
		ax1.plot(x, y, 'r-', label="Radiation")
		# ax1.set_xlabel('time (s)')
		ax1.set_ylabel('Activity 1/h', color='g')
		ax1.set_ylim(500, 2200)
		ax1.tick_params(axis='y', labelcolor=color)
		ax1.tick_params(axis="x", rotation=75)

		ax2 = ax1.twinx()
		color = "tab:blue"
		ax2.plot(x, z, 'b-', label="Temperature °C")
		ax2.set_ylabel('t °C', color='b')

		# Adjust the y-axis label colors
		fig.tight_layout()
		ax2.tick_params(axis='y', colors=color)
		ax2.set_ylim(0, 50)
		legend1 = ax1.legend(loc="upper left")
		legend2 = ax2.legend(loc="upper right")

		fig.legend(handles=[legend1, legend2])
		plt.xticks(rotation=75)

		plt.title('Radioactivty and temperature')

		self.ids.main_box.clear_widgets()
		self.ids.main_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

	# ------------------------------------------- > date picker
	def reset(self):
		self.ids.main_box.clear_widgets()
		self.ids.time.text = "time: "
		self.ids.dates.text = "date: "
		plt.clf()

	def call_dialog(self):
		dialog = MDDatePicker(mode="range")
		dialog.open()
		dialog.bind(on_save=self.get_days)

	def get_days(self, instance, value, date_range):
		first_day = date_range[0]
		last_day = date_range[-1]
		first_day = str(first_day)
		last_day = str(last_day)
		self.start_time = first_day  # .replace('2023-',"")
		self.end_time = last_day  # .#replace("2023-","")

		self.ids.dates.text = "from " + str(self.start_time) + " to " + str(self.end_time)
		# print(date_range)
		print(self.start_time)
		print(self.end_time)

	def on_date_selected(self, instance, date):
		# This method is called when a date is selected in the MDDatePicker
		self.selected_date = date

	def print_selected_date(self, instance, value, date_range):
		# This method is called when the "Print Selected Date" button is pressed
		if hasattr(self, "selected_date"):
			print(str("Selected Date:"), self.selected_date)

	# ------------------------------------------- > time picker

	def show_time_picker(self):
		self.content = Time_picker()
		self.dialog = MDDialog(


			size_hint=(0.6, 0.3),
			type='custom',
			text="to display activity in this time range",
			content_cls=self.content,
			buttons=[  # MDFlatButton(text="CANCEL",
				# pos_hint={"x": 0, "y": -0.25}),
				MDFlatButton(text="OK", pos_hint={"x": 0, "y": -0.25},
					on_press=self.send_date)])
		self.dialog.open()

	def send_date(self, arg):
		start_hr = self.content.ids.start_hr.text
		start_min = self.content.ids.start_min.text
		end_hr = self.content.ids.end_hr.text
		end_min = self.content.ids.end_min.text
		self.begining = " " + str(start_hr) + ':' + str(start_min)
		self.finish = " " + str(end_hr) + ':' + str(end_min)
		self.value = 'from ' + self.begining + ' to ' + self.finish
		self.ids.time.text = self.value
		self.dialog.dismiss()


class Map(MDScreen): #------------------------------> imbeding Map
	lat = NumericProperty(0)
	lon = NumericProperty(0)

	def __init__(self, **kwargs):
		super(Map, self).__init__(**kwargs)
		self.url = 'http://radioscan.atwebpages.com/index.php'  # parsing web page with stored data we can retrieve
		self.read_url = pd.read_html(self.url)                  # desired data and treat as we wish: count average value
		self.radiation = self.read_url[0].Radiation             #
		self.time = self.read_url[0].Date                       #
		# self.id = self.read_url[0].id                         #
		self.temp = self.read_url[0].Temperature                #
		self.coordinates = self.read_url[0].coordinates         #
		self.df = pd.DataFrame(self.read_url[0])


	def begin(self):
		try:
			self.Data = serial.Serial("com5", 9600)
			Clock.schedule_interval(self.reading_data, 0.5)
		except serial.SerialException:
			Clock.schedule_once(self.retry_load_map, 0.1)

	def retry_load_map(self,dt):
		self.begin()

	def reading_data(self, dt):
		self.read_data = self.Data.readline()
		self.read_data = self.read_data.decode()

		self.digits = re.findall(r"-?\d+\.\d+|-?\d+", self.read_data)

		self.lat = self.digits[2]
		self.lon = self.digits[3]


		self.ids.map.center_on(self.lat, self.lon)
		self.ids.lat.text = "latitude:   " + str(round(self.lat, 6))
		self.ids.lon.text = "longitude: " + str(round(self.lon, 6))

		self.df['Date'] = pd.to_datetime(self.df['Date'])
		self.df['Radiation'] = pd.to_numeric(self.df['Radiation'])
		date = str(self.df['Date'].tail(1))
		date = date.split(" ")
		date = date[3]

		self.average = self.df['Radiation'].tail(24).sum() / (24 * 60 * 60)  # to show average data of radiation activity
		self.average = round(2)                                              # within last 24 hrs in context menu of the
																			# map marker

		print("average: " + str(self.average))

		self.ids.average_rad.text = str("Activity, Bq: ") + str(self.average) + str("/s")
		self.ids.date.text = str("Date:   ") + str(date)
		self.ids.date.font_style = "Caption"

	def map_close(self):

		Clock.unschedule(self.reading_data)
		time.sleep(0.1)
		self.Data.close()

class HourTextField(MDTextField):


	def insert_text(self, substring, from_undo=False):
		# Combine the current text with the new substring
		new_text = self.text + substring

		# Check if the new text is a valid hour format
		if self.is_valid_hour(new_text):
			# Call the parent's insert_text() to update the text
			super().insert_text(substring, from_undo=from_undo)
		print("Input text:", new_text, substring)

	@staticmethod
	def is_valid_hour(text):
		# Use regular expression to match numbers from 0 to 24
		pattern = r'^(?:2[0-4]|[01]?[0-9])$'
		return bool(re.match(pattern, text))


class MinuteTextField(MDTextField):
	def insert_text(self, substring, from_undo=False):
		# Combine the current text with the new substring
		new_text = self.text + substring

		# Check if the new text is a valid minute format
		if self.is_valid_minute(new_text):
			# Call the parent's insert_text() to update the text
			super(MinuteTextField, self).insert_text(substring, from_undo=from_undo)

	@staticmethod
	def is_valid_minute(text):
		# Use regular expression to match numbers from 0 to 59
		pattern = r'^(?:[0-5]?[0-9])$'
		return bool(re.match(pattern, text))


class BottomBar(MDBottomNavigation):
	pass

class RadioScan(MDApp):
	pass


RadioScan().run()

