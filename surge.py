import pandas as pd
from predictor import Predictor

class Surge(object):
	def __init__(self):
		#Self explanatory
		self.from_area_count = pd.read_excel('fin.xlsx')
		self.g_surge = self.from_area_count.groupby(['week', 'from_area', 'start_hour'])
		self.g_surge_week = self.from_area_count.groupby(['week', 'from_area'])

	def calculate_surge(self, start_date, area, user_id):
		#This function is used as the main function by the object to calculate surge
		start_date = pd.to_datetime(start_date)
		#calculating week of year
		week_no = int(start_date.date().strftime("%V"))
		hour = start_date.hour

		hour_val = self.previous_hours_ride_count(hour, week_no, area) #Stores the value of the number of rides from this hour in past 4 weeks
		week_val = self.previous_weeks_ride_count(week_no, area)  #Stores the value of the avg. rides from this location past 4 weeks

		clf = Predictor()
		result = clf.predict(user_id, start_date, area)

		surge_price = self.surge_algorithm(hour_val, week_val, result)

		return round(surge_price, 2)

	def previous_hours_ride_count(self, hour, week, area):
		#Used to calculate avg number of rides from this location in this hour for the past four weeks
	    ride_weekly = []
	    previous_weeks = [week-i for i in range(1,5)]
	    
	    #3 values are calculated for this location.
	    #For example if hour of ride is 15. The algorithm will also take 14 and 16 but will only give weightege of 0.5.
	    #In the end, the sum of all three will be divided by 2 cuz 0.5(x-1) + x + 0.5(x+1)
	    for i in previous_weeks:
	        ride_count = []
	        try:
	            ride_count.append(self.g_surge.get_group((i, area, hour-1))['count'].count())
	        except KeyError:
	            ride_count.append(0)
	        
	        try:
	            ride_count.append(self.g_surge.get_group((i, area, hour))['count'].count())
	        except KeyError:
	            ride_count.append(0)
	            
	        try:            
	            ride_count.append(self.g_surge.get_group((i, area, hour+1))['count'].count())
	        except KeyError:
	            ride_count.append(0)
	        
	        total_rides = (0.5*ride_count[0] + ride_count[1] + 0.5*ride_count[2])/2
	        ride_weekly.append(total_rides)
	        
	        
	    ride_avg = sum(ride_weekly) / len(ride_weekly)
	    
	    return ride_avg

	def previous_weeks_ride_count(self, week, area):
		#Same as above function but calculates average rides from the week. Gets average number of rides in each week
	    ride_weekly = []
	    previous_weeks = [week-i for i in range(1,5)]
	    
	    for i in previous_weeks:
	        try:
	            ride_value = self.g_surge_week.get_group((i, area))['count'].count()
	        except KeyError:
	            ride_value = 0
	            
	        ride_weekly.append(ride_value/24)
	        
	        
	    ride_avg = sum(ride_weekly) / len(ride_weekly)
	    
	    return ride_avg

	def surge_algorithm(self, hour_ride_ct, week_ride_ct, cancel=None):
	    surge_multiplier = hour_ride_ct/week_ride_ct
	    
	    if surge_multiplier <= 1:
	        return 1
	    
	    else:
	        #6 is chosen after careful consideration since it does not give a value  very large and neither
	        #does it give a value very small
	        surge = surge_multiplier/6
	        if cancel:
	        	#Based on prediction model, we can find if they might cancel the ride. If yes, reduce the surge by half
	            surge_cancel = surge/2
	            return 1+surge_cancel
	        return 1+surge

'''
#Remove the comments and run to test it on a this data
s
start_date = pd.to_datetime('2013-03-22 20:00:00')
week_no = int(start_date.date().strftime("%V"))
area = 393
hour = start_date.hour


obj = Surge()
print(obj.calculate_surge(start_date, area, 4))
'''