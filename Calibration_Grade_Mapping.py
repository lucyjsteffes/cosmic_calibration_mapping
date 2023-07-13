#Import the packages that will be needed in this script
import pickle
import numpy as np
import pandas as pd
import json

from astropy.time import Time
from tqdm import tqdm

import matplotlib.pyplot as plt

from astropy import units as u
from astropy.coordinates import SkyCoord

import seaborn as sns

#Open the two pickle files
#The first has all of the information about the observations. This includes the number of antennas, start and end times, and the coordinates in equatorial coordinates.
with open('Scans.pickle', 'rb') as f:
    scans_data = pickle.load(f) # deserialize using load()

#The second pickle file has all of the information about the calibration grade of the observations.    
with open('Calibration_Grade.pickle', 'rb') as f:
    calibration_data = pickle.load(f)
    
#Both of the pickle files have the information about the files name in the form of the data set ID and the scan ID. But for each file, there is some manipulation that must occur to access this information and match the rows of each file up with each other.

#For the scans file, all of the information is contained in just two columns. One with the start time of the observations. The second with a long string of a dictionary of the additional 31 columns compressed into one column. To access any of this, we would like to split it up.

#In this particular file, there are several rows which are fake pointings. These should not be plotted because they are not real points. This is why they are removed. In future iterations of this code, I will add in a few lines that should go through and remove that part so it will work with any data set rather than being restricted to this indexing.

start_time = np.array(scans_data["start"]) #call in the first column
time = list(np.datetime_as_string(start_time)) #convert the string to the time and then organize as a list

t = Time(time, format='isot', scale='utc') #convert the times to the modified julian date
t = list(t.mjd)

start_time = t[0:50931] + t[50979:-1] #remove the times that correspond to the fake pointings

metadata = np.array(scans_data["metadata_json"]) #call in the second column

#Set up the data frame for the dictionary in the second row. With many of these I did not know what the acronym stood for, so I just left it.
meta_data_frame = pd.DataFrame({"Data Set ID":[],
                               "Scan Number":[],
                               "Sub-Scan Number":[],
                               "Scan ID":[],
                               "Number of Antennas":[],
                               "Observation Bandwidth (MHz)":[],
                               "SSLO":[],
                               "Sideband":[],
                               "SRC":[],
                               "IFIDS":[],
                               "FCents":[],
                               "Right Ascension":[],
                               "Declination":[],
                               "Start Time":[],
                               "End Time":[],
                               "Project ID":[],
                               "Station":[],
                               "Modified Julian Date":[],
                               "FenPol":[],
                               "FenChan":[],
                               "BaseBand":[],
                               "Sample (Hz)":[],
                               "Intents":[],
                               "Number of Bits":[],
                               "TBin":[],
                               "Start Time (Unix)":[],
                               "End Time (Unix)":[],
                               "End Date and Time":[],
                               "Time Difference":[],
                               "Time Now (Unix)":[],
                               "Time Now":[]})

#Break up the dictionary
for i in tdqm(range(0,50931) + range(50979,79544)):
    metadata_1 = json.loads(np.array(scans_data["metadata_json"])[i]) #identify each of the rows and split up the dictionaries
    
    #Set up each new row to be appended
    new_row = [metadata_1['datasetid'], metadata_1['scanno'], metadata_1['subscanNo'], metadata_1['scanid'], metadata_1['nant'],
               metadata_1['obsbwmhz'], metadata_1['sslo'], metadata_1['sideband'], metadata_1['src'], metadata_1['ifids'], 
               metadata_1['fcents'], metadata_1['ra_deg'], metadata_1['dec_deg'], metadata_1['tstart'], metadata_1['tend'], 
               metadata_1['projid'], metadata_1['station'], metadata_1['mjd'], metadata_1['fenpol'], metadata_1['fenchan'], 
               metadata_1['baseband'], metadata_1['samplehz'], metadata_1['intents'], metadata_1['nbits'], metadata_1['tbin'], 
               metadata_1['tstart_unix'], metadata_1['tend_unix'], metadata_1['tend_datettime'], metadata_1['tdiff'], 
               metadata_1['tnow_unix'], metadata_1['tnow']]
    
    meta_data_frame.loc[len(meta_data_frame.index)] = new_row #append each new row to the empty data frame

#Export the intermediate data to a new pickle file
with open('scans_data.pkl', 'wb') as f:  # open a new pickle file
    pickle.dump(meta_data_frame, f) # serialize the list
f.close()

#Open the new pickle file
with open('scans_data.pkl', 'rb') as f:
    meta_data_frame = pickle.load(f)

#Now let's go back to the second pickle file that we started with and get the data set ID and the scan ID. These are embedded within the file uri, so we need to break that up.
#Set up a new data frame
new_calibration_data = pd.DataFrame({"Observation ID":[],
                                    "Overall Grade":[],
                                    "Flagged Percentage":[],
                                    "Data Set ID":[],
                                    "Scan ID":[]})

for i in tqdm(range(len(file_uri))):
    data = str(np.array(calibration_data["file_uri"])[i]) #call in each row and turn it into a string
    split_data = data.split("/") #split up the string into a list, making the cuts at each of the slashes
    
    observation_id = np.array(calibration_data["observation_id"]) #call in the first column for the observation ID
    overall_grade = np.array(calibration_data["overall_grade"]) #define the second column, which is the overall calibration grade
    flagged_percentage = np.array(calibration_data["flagged_percentage"]) #define the third column, the percentage of the data which was flagged
    
    appending_data = [observation_id[i], overall_grade[i], flagged_percentage[i], split_data[5], split_data[6]] #define the new row of the data set
    new_calibration_data.loc[i] = appending_data #append the new row to the empty data frame
    
#save this new data frame to a new pickle file
with open('calibration_data.pkl', 'wb') as f:  # open a text file
    pickle.dump(new_calibration_data, f) # serialize the list
f.close()

#open up the pickle file that we just saved
with open('calibration_data.pkl', 'rb') as f:
    new_calibration_data = pickle.load(f)

#Now everything is set up to start matching up the observations. Start by defining the scan IDs and the data set IDs from both of the new pickle files  
calibration_scan_ID = np.array(new_calibration_data["Scan ID"]) #scan ID from the calibration grade file
info_scan_ID = np.array(meta_data_frame["Scan ID"]) #scan ID from the observation information file

calibration_data_set_ID = np.array(new_calibration_data["Data Set ID"]) #data set ID from the calibration grade file
info_data_set_ID = np.array(meta_data_frame["Data Set ID"]) #data set ID from the observation information file

#We are going to bring the coordinate information into the file with the calibration grade information. Before defining the new data frame, define the columns that should be carried over. Many are the same from the previous data frame.
observation_id = np.array(new_calibration_data["Observation ID"])
overall_grade = np.array(new_calibration_data["Overall Grade"])
flagged_percentage = np.array(new_calibration_data["Flagged Percentage"])

#Also define the right ascension and declination values from the observation information file so that the correct values can be carried over to the new data frame
right_ascension = np.array(meta_data_frame["Right Ascension"])
declination = np.array(meta_data_frame["Declination"])

#set up the new data frame for just the information that we would like to keep
longer_matches = pd.DataFrame({"Observation ID":[],
                              "Overall Grade":[],
                              "Flagged Percentage":[],
                              "Data Set ID":[],
                              "Scan ID":[],
                              "Right Ascension":[],
                              "Declination":[]})

#loop through all of the rows of the file with the observation information
for i in tqdm(range(len(info_scan_ID))):
    scan = matching_df.loc[np.array(matching_df["Scan ID"]) == np.unique(np.array(matching_df["Scan ID"]))[i]] #identify each row
     
    #loop through all of the rows of the calibration information    
    for j in range(len(calibration_scan_ID)):
        #find where the scan IDs match. The scan IDs are longer than the data set IDs and contain a bit more information, so those are used to find the matches
        if info_scan_ID[i] == calibration_scan_ID[j]:
            #set up the new row which will be appended to the empty data frame 
            appending_data = [observation_id[j], overall_grade[j], flagged_percentage[j], calibration_data_set_ID[j], calibration_scan_ID[j], right_ascension[i], declination[i]]
            longer_matches.loc[i] = appending_data #append each new row to the data fame
        else:
            continue
            #if there is not a match, just skip over that row and continue

#save that to a new pickle file
with open('calibration_grade_coordinates.pkl', 'wb') as f:  # open a text file
    pickle.dump(longer_matches, f) # serialize the list
f.close()

#open up the pickle file that was just created
with open('calibration_grade_coordinates.pkl', 'rb') as f:
    longer_matches = pickle.load(f)
    
#define the variables that will be needed for creating the map
right_ascension = np.array(longer_matches["Right Ascension"])
declination = np.array(longer_matches["Declination"])
calibration_grade = np.array(longer_matches["Overall Grade"])

#define the coordinates using astropy. the coordinates should already be in degrees
c_icrs = SkyCoord(ra=right_ascension*u.degree, dec=declination*u.degree, frame='icrs')

plt.figure(figsize=(8,4.2)) #set up the figure
plt.subplot(111, projection="aitoff") #use an aitoff projection so that everything is plotted on the plane of the sky using equatorial coordinates
plt.suptitle("VLASS Epoch 3 COSMIC Observations")
plt.grid(True)
plt.subplots_adjust(top=0.95,bottom=0.0)

#I prefer to use a seaborn scatterplot for a lot of the the plotting because of the ease with which you can change the size and colors of the data points based on several variables like we are trying to do here
sns.set_theme()
g = sns.scatterplot(data=longer_matches, x=right_ascension, y=declination, hue=calibration_grade, size = calibration_grade, palette = "ch:s=.25,rot=-.25")
#The calibration grade is shown in both the color of the data points and their size with the higher calibration grade having a larger data point and a darker hue
plt.show()