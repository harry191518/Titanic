"""
Author : RLai

"""

import csv as csv
import numpy as np

csv_file_object = csv.reader(open('train.csv', 'rb'))       # Load in the csv file
header = csv_file_object.next()                             # Skip the fist line as it is a header
data=[]                                                     # Create a variable to hold the data

for row in csv_file_object:                 # Skip through each row in the csv file
    data.append(row)                        # adding each row to the data variable
data = np.array(data)                       # Then convert from a list to an array

data[ data[0::,5] == "" , 5 ] = 16
data[ data[0::,5].astype(np.float) < 16 , 5 ] = 0
data[ data[0::,5].astype(np.float) >= 16 , 5 ] = 1

fare_ceiling = 40
data[ data[0::,9].astype(np.float) >= fare_ceiling, 9 ] = fare_ceiling - 1.0

fare_bracket_size = 10
number_of_price_brackets = fare_ceiling / fare_bracket_size
number_of_classes = 3                             # I know there were 1st, 2nd and 3rd classes on board.
number_of_classes = len(np.unique(data[0::,2]))   # But it's better practice to calculate this from the Pclass directly:
                                                  # just take the length of an array of UNIQUE values in column index 2


survival_table = np.zeros([2,2,number_of_classes,number_of_price_brackets],float)

for i in xrange(number_of_classes):
	for j in xrange(number_of_price_brackets):
		for k in range(0, 2):
			
			women_only_stats = data[ (data[0::,4] == "female") \
                                 & (data[0::,5].astype(np.float) == k) \
                                 & (data[0::,2].astype(np.float) == i+1) \
                                 & (data[0:,9].astype(np.float) >= j*fare_bracket_size) \
                                 & (data[0:,9].astype(np.float) < (j+1)*fare_bracket_size), 1]

			men_only_stats = data[ (data[0::,4] != "female") \
                                 & (data[0::,5].astype(np.float) == k) \
                                 & (data[0::,2].astype(np.float) == i+1) \
                                 & (data[0:,9].astype(np.float) >= j*fare_bracket_size) \
                                 & (data[0:,9].astype(np.float) < (j+1)*fare_bracket_size), 1]

			if np.size(women_only_stats.astype(np.float)) != 0:	
				survival_table[0,k,i,j] = np.mean(women_only_stats.astype(np.float))  # Female stats
			if np.size(men_only_stats.astype(np.float)) != 0:
				survival_table[1,k,i,j] = np.mean(men_only_stats.astype(np.float))    # Male stats

survival_table[ survival_table < 0.5 ] = 0
survival_table[ survival_table >= 0.5 ] = 1

test_file = open('test.csv', 'rb')
test_file_object = csv.reader(test_file)
header = test_file_object.next()

predictions_file = open("myresult.csv", "wb")
predictions_file_object = csv.writer(predictions_file)
predictions_file_object.writerow(["PassengerId", "Survived"])

for row in test_file_object:
    for j in xrange(number_of_price_brackets):
        try:
            row[8] = float(row[8])    # No fare recorded will come up as a string so
                                      # try to make it a float
        except:                       # If fails then just bin the fare according to the class
            bin_fare = 3 - float(row[1])
            break                     # Break from the loop and move to the next row
        if row[8] > fare_ceiling:     # Otherwise now test to see if it is higher
                                      # than the fare ceiling we set earlier
            bin_fare = number_of_price_brackets - 1
            break                     # And then break to the next row

        if row[8] >= j*fare_bracket_size\
            and row[8] < (j+1)*fare_bracket_size:     # If passed these tests then loop through
                                                      # each bin until you find the right one
                                                      # append it to the bin_fare
                                                      # and move to the next loop
            bin_fare = j
            break
    try:
		row[4] = float(row[4])
    except:
		row[4] = 16

    if row[4] >= 16:
		row[4] = 1
    else:
		row[4] = 0

    if row[3] == 'female':
        predictions_file_object.writerow([row[0], "%d" % int(survival_table[ 0, row[4], float(row[1]) - 1, bin_fare ])])
    else:
        predictions_file_object.writerow([row[0], "%d" % int(survival_table[ 1, row[4], float(row[1]) - 1, bin_fare])])

test_file.close()
predictions_file.close()
