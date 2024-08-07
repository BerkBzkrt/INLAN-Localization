This repository contains the RSS measurements obtained by mounting 4 receivers on the ceiling of the warehouse (or on tables for newer data). The corresponding dataset can be found at RSS_data.csv (RSS_data_cross and RSS_data_square for channel switched data) and the average noise floor measurement for each channel is given in avg_noise.csv. 

The features in the dataset are as follows:

Pyn: y channel signal strength read by receiver n.

Pzn: z channel signal strength read by receiver n.

time: time elapsed after the start of the measurements (separate for each line).

tag_height: height of the tag from the ground in meters.

frequency: frequency of the transmitted signal in MHz.

tx_x: x coordinate of the transmitter in meters.

tx_y: y coordinate of the transmitter in meters.

rxn_x: x coordinate of receiver n in meters.

rxn_y: y coordinate of receiver n in meters.


x: x coordinate of the tag in meters.

y: y coordinate of the tag in meters.

distance: distance of the tag in meters (separate for each line).

Different experiment configurations and their corresponding data can be found in the related folders. Non-maxed versions consist of the measurements that are collected after switching the channel at the transmitter (refer to the channel column of the dataset). Regular versions (RSS_data_cross.csv etc.) treat measurements coming out of two switched channels as one measurement by taking the maximum

Rooms setup for cross configuration:
------------------------------------------------------------------------------------------------------------------------------------
![alt text](https://github.com/BerkBzkrt/INLAN-Localization/blob/main/Cross%20configuration/cross_configuration.png)

Room setup for square configuration:
------------------------------------------------------------------------------------------------------------------------------------
![alt text](https://github.com/BerkBzkrt/INLAN-Localization/blob/main/Square%20configuration/square_configuration.png)
