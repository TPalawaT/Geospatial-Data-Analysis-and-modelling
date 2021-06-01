import pandas as pd
import joblib
import numpy as np

class Predictor(object):
	def __init__(self):
		self.df = pd.read_excel('data.xlsx')
		#Prediciton is made for point due to availability of data
		self.df2 = self.df[self.df['travel_type_id'] == 2]
		self.df2['booking_hour'] = self.df2['booking_created'].apply(self.strip_hour)

	def predict(self, user, date, area):
		#getting the user's data of rides less than the date rider is booking a cab
		model_df = self.df2[(self.df2['user_id'] == user) & (self.df2['from_date'] < date)]

		#Previous 5 cancellation values
		cancel = list(model_df['Car_Cancellation'].values[-5:])

		#Previous 5 hours of booking. +1 is done since 0 is reserved for timings when there was no previous ride for the user
		booking_hour = list(model_df['booking_hour'].values[-5:])
		booking_hour = [i+1 for i in booking_hour]

		#If the user hasn't taken even 5 rides yet, we put dummy data
		if len(booking_hour) != 5:
			unfilled_length = 5 -len(booking_hour)
			filler_value = [0] * unfilled_length

			cancel.extend(filler_value)
			booking_hour.extend(filler_value)

		#Calculating the number of rides from a particular location
		area_count = self.df2[self.df2['from_area_id'] == area]['id'].count()

		#Making a list same as what was used on training data.
		model_array = [area]
		model_array.extend(cancel)
		model_array.extend(booking_hour)
		model_array.append(area_count)

		prediction = self.cancellation_indicator(model_array)

		return prediction

	def cancellation_indicator(self, arr):
		#The function is self explanatory. Loads the model and preicts a value.
		model = joblib.load('cancellation_model.sav')
		arr = np.array(arr).reshape(1,-1)
		result = model.predict(arr)

		return result

	#This function returns only hour form datetime format
	def strip_hour(self, h):
		return h.hour



'''
#Remove the comments and run to test it on a this data

start_date = pd.to_datetime('2013-03-22 20:00:00')
week_no = int(start_date.date().strftime("%V"))
area = 393
hour = start_date.hour


obj = Predictor()
print(obj.predict(22177, start_date, area))
'''