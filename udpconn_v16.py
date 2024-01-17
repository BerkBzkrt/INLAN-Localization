# Author: Berk Bozkurt
# Date: January 16, 2024

import numpy as np
import pandas as pd
import cmd
import socket
import os
import sys
import threading
import time
from tkinter import *
from Receiver_v5 import *
from Tag_v2 import *

# #Global vars
DIST_X = 10
DIST_Y = 15
HEIGHT = 750
WIDTH = 500
L = DIST_Y * 4
R = 5

class UDPConn(cmd.Cmd):
    prompt = '' 

    def __init__(self, s, destination, num_rx = 2, window_size = 25, use_lookup = False, n = 1):
        cmd.Cmd.__init__(self)
        self.s = s
        self.destination = destination
        self.minus_found = False
        self.str = "" 
        self.window_size = window_size
        self.current_size = 0
        self.num_rx = num_rx #change this later on
        self.buffer = np.zeros((2*self.num_rx,self.window_size))
        self.estimates = [(SIDE/2,SIDE/2)]
        self.lookup = use_lookup
        self.n = n
        self.table = np.zeros((50,num_rx + 2))

    def do_EOF(self, line):
        return True

    def precmd(self, line):
        line = line.strip()
        if not line:
            line = '\n'
        elif line == 'EOF':
            return line
        else:
            line = line + '\n'
        self.s.sendto(line.encode(), self.destination)
        return ""
#Returns the list of receivers that are currently on
def working_receivers(rx_list):
    working_rx = []
    for rx in rx_list:
        if rx.on:
            working_rx.append(rx)
    return working_rx

def find_intersect(m1,b1,m2,b2):
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    return x,y
    
"""""
Returns the list of intersection points for a given list of receivers
The current implementation only calculates the intersections of adjacent
receivers. Commented-out part can be used the calculate all possible intersections
Parameters:
    rx_list: list of receiver objects
    x0: x coordinate of the tag
    y0: y coordinate of the tag
Returns:
    intersects: list of (x,y) pairs for the intersections
"""""
def all_intersects(rx_list):
    intersects = []
    for i in range(len(rx_list)):
        for j in range(i):
            if rx_list[i].x == rx_list[j].x or rx_list[i].y == rx_list[j].y: #only take the adjacent intersections 
                point = find_intersect(rx_list[i].slope,rx_list[i].intersect,rx_list[j].slope,rx_list[j].intersect)
                # point = find_intersect(rx_list[i],rx_list[j],x0,y0)
                if not(point in intersects):
                    intersects.append(point)
    return intersects
    # comb_list = list(itertools.combinations(rx_list, 2))
    # for comb in comb_list:
    #     point = find_intersect(comb[0],comb[1],x0,y0)
    #     if point[0]>= 0 and point[0] <= B and point[1]>= 0 and point[1] <= B:
    #         intersects.append(point)
    # return intersects

"""""
Returns the list of intersection points for a given list of receivers
The current implementation only calculates the intersections of adjacent
receivers. Commented-out part can be used the calculate all possible intersections
Parameters:
    rx_list: list of receiver objects
    x0: x coordinate of the tag
    y0: y coordinate of the tag
Returns:
    (x,y): average of all the intersection points
"""""
def find_estimate(udp,rx_list):
    #Only takes the average of the points for now
    intersects = all_intersects(rx_list)
    num_points = len(intersects)
    if num_points == 0:
        #use the previous estimate if there is no intersection
        # print(udp.estimates[-1])
        return udp.estimates[-1]
    else:
        sum_x, sum_y =  0,0 
        for point in intersects:
            sum_x += point[0]
            sum_y += point[1]
        return sum_x / num_points, sum_y / num_points
    

def estimate_location(udp, amps_avg, rx_list):
    #Convert this part into a function as it is used multiple times (in setup and update)
    angle_str = ""
    for i,rx in enumerate(rx_list):
        x_mag = amps_avg[2*i]
        z_mag = amps_avg[2*i + 1]

        if x_mag < rx.x_floor or z_mag < rx.z_floor:
            rx.set_on(False)
        else:
            rx.set_on(True)

        if rx.x == DIST_X and rx.y == 0:
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x - L * np.cos(acute_angle)
            y1 = rx.y + L * np.sin(acute_angle)
            angle_str += ' angle 1 = ' + str(np.round(np.rad2deg(angle),2))
        elif rx.x == 0 and rx.y == 0:
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x + L * np.cos(acute_angle)
            y1 = rx.y + L * np.sin(acute_angle)
            angle_str += ' angle 0 = ' + str(np.round(np.rad2deg(angle),2))
        elif rx.x == DIST_X and rx.y == DIST_Y:
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x - L * np.cos(acute_angle)
            y1 = rx.y - L * np.sin(acute_angle)
            angle_str += ' angle 2 = ' + str(np.round(np.rad2deg(angle),2))
        else:
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x + L * np.cos(acute_angle)
            y1 = rx.y - L * np.sin(acute_angle)
            angle_str += ' angle 3 = ' + str(np.round(np.rad2deg(angle),2))

        m = (y1 - rx.y) / (x1 - rx.x)
        b = rx.y - m * rx.x
        rx.set_mb(m,b)
        rx.set_line(x1,y1,HEIGHT,WIDTH,DIST_X,DIST_Y)
        # y1 = SIDE - y1 #for displaying purposes
        # coord_update = [rx.x,SIDE - rx.y,x1,y1]
        # canvas.coords(lines[i],coord_update) 
    working_list = working_receivers(rx_list)
    x_est,y_est = find_estimate(udp,working_list)

    return x_est, y_est, angle_str

def estimate_lookup(amps_avg,table,n):   
    num_data, num_features = table.shape
    num_cols = len(amps_avg)
    X = table[:,:num_cols]
    Y = table[:,num_cols:]
    row = amps_avg.reshape((1,num_cols))
    ind = np.argsort(np.sum((X - row)**2, axis = 1))[:n]
    est_x,est_y = np.sum(Y[ind], axis = 0) / num_data
    return est_x, est_y

def setup_environment(udp,amps_avg,rx_info, csv_path = 'location_data.csv'):
    rx_list = []
    lines = []
    window = Tk()
    angle_str = ""
    window.geometry("800x800")
    canvas = Canvas(window,width=WIDTH,height=HEIGHT)
    canvas.pack(padx= 1,pady=1) 

    num_rx = len(rx_info)
    for i in range(num_rx):
        x,y = rx_info[i]['location']
        color = rx_info[i]['color']
        x_floor,z_floor = rx_info[i]['noise floors']
        rx = Receiver(x,y,0,canvas,height = HEIGHT, width = WIDTH, dist_x = DIST_X, dist_y = DIST_Y,color = color)
        # (self,x,y,sigma,canvas,height = 500, width = 500, dist_x = 10, dist_y = 10,color = 'green',slope = 1, intersect = 0, x_floor_db = -140, z_floor_db = -140)
        rx.set_floor(x_floor,z_floor)
        
        x_mag = amps_avg[2*i]
        z_mag = amps_avg[2*i + 1]
        rx.set_amps(x_mag,z_mag)

        if x_mag < rx.x_floor or z_mag < rx.z_floor:
            rx.set_on(False)
        else:
            rx.set_on(True)

        rx_list.append(rx) 
        if rx.x == DIST_X and rx.y == 0: #Rx1
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x - L * np.cos(acute_angle)
            y1 = rx.y + L * np.sin(acute_angle)
            angle_str += ' angle 1 = ' + str(np.rad2deg(angle))
        elif rx.x == 0 and rx.y == 0: #Rx0
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x + L * np.cos(acute_angle)
            y1 = rx.y + L * np.sin(acute_angle)
            angle_str += ' angle 0 = ' + str(np.rad2deg(angle))
        elif rx.x == DIST_X and rx.y == DIST_Y: #Rx2
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x - L * np.cos(acute_angle)
            y1 = rx.y - L * np.sin(acute_angle)
            angle_str += ' angle 2 = ' + str(np.rad2deg(angle))
        else:                           #Rx3
            angle = np.arctan(np.sqrt(z_mag/x_mag))
            acute_angle = np.pi/2 - angle
            x1 = rx.x + L * np.cos(acute_angle)
            y1 = rx.y - L * np.sin(acute_angle)
            angle_str += ' angle 3 = ' + str(np.rad2deg(angle))

        angle_deg = np.rad2deg(angle)
        m = (y1 - rx.y) / (x1 - rx.x)
        b = rx.y - m * rx.x
        rx.set_mb(m,b)
        rx.set_line(x1,y1,HEIGHT,WIDTH,DIST_X,DIST_Y) #new implementation (each receiver has its own line object)

        #Delete the lines and read from the csv file if using lookup
        if udp.lookup:
            df = pd.read_csv(csv_path)
            udp.table = df.to_numpy()
            for rx in rx_list:
                rx.delete_line()

    working_list = working_receivers(rx_list)
    x_est,y_est = find_estimate(udp,working_list)
    udp.estimates.append((x_est,y_est))
    tag = Tag(x_est,y_est,canvas,height = HEIGHT, width = WIDTH, dist_x = DIST_X, dist_y = DIST_Y, color = 'red')
    # (self,x,y,canvas,height,width,dist_x,dist_y,x_vel = 0,y_vel = 0,color = 'red', R = 5) 
    score_label  = Label(window, text = f'{angle_str}, loc. = ({np.round(x_est,2)}, {np.round(y_est,2)})', font=("Helvetica", 12))
    score_label.pack()

    return canvas, window, score_label, rx_list, lines, tag

def update_step(udp, amps_avg, rx_list, tag, score_label):
    if udp.lookup:
        x_est,y_est = estimate_lookup(amps_avg,table = udp.table, n = udp.n)
        score_label.config(text= f'{angle_str}, loc. = ({np.round(x_est,2)}, {np.round(y_est,2)})', font=("Helvetica", 12))
    else:
        x_est,y_est,angle_str = estimate_location(udp, amps_avg, rx_list)
        score_label.config(text= f'loc. = ({np.round(x_est,2)}, {np.round(y_est,2)})', font=("Helvetica", 12))

    udp.estimates.append((x_est,y_est))
    x_est_disp, y_est_disp = x_est * (WIDTH / DIST_X), y_est * (HEIGHT / DIST_Y) #for displaying purposes
    tag.canvas.moveto(tag.image,x_est_disp - R,HEIGHT - y_est_disp - R)
    

def display_thread(udp,window,score_label,rx_list,rx_info,tag):

    while True:
        amps_avg = send_prompts(udp = udp,rx_info = rx_info)
        update_step(udp,amps_avg, rx_list, tag, score_label)
        window.update()

def read_thread(sock, name, udp):
    while True:
        s = sock.recv(65536)
        os.write(sys.stdout.fileno(), s) #probably don't need to do this, slowing things down ny prnting on command prompt
        string = s.decode('utf-8') #convert the message read from the socket to a string

        #Interpret the message, look for a minus sign and process the string accordingly
        if ('-' in string):
            str1 = after_minus(string,udp)
            udp.str += str1
        elif udp.minus_found:
            str2 = until_space(string,udp)
            udp.str += str2

def send_prompts(udp,rx_info):
    #send the prompts for all the receivers 
    num_rx = len(rx_info)
    for i in range(num_rx):
        port_index = rx_info[i]['port']
        x_prompt = port_index + "show /rf/xmag_dbm\n"
        z_prompt = port_index + "show /rf/zmag_dbm\n"
        udp.s.sendto(x_prompt.encode(),udp.destination)
        time.sleep(0.01)
        udp.s.sendto(z_prompt.encode(),udp.destination)
        time.sleep(0.01)
    time.sleep(0.1) #wait before interpreting the responses to the prompts 
    
    #interpret the response to the prompts 
    #str attribute of the udp object have the decoded message received from the transmitter
    #TODO: handle the case where the order of the ports is changes (non-increasing order etc.) ============================================================================
    sample = np.zeros((2*num_rx,1))
    message = udp.str.split('-') #processed response message 
    for i in range(num_rx):
        x_mag_db = -float(message[i+1]) #add 1 to not use anything before the first '-'
        z_mag_db = -float(message[i+2])
        x_mag = 10**(x_mag_db/10) 
        z_mag = 10**(z_mag_db/10)
        sample[2*i] = x_mag
        sample[2*i+1] = z_mag

    #add this sample column to the buffer and delete the oldest
    udp.buffer = np.concatenate((udp.buffer[:,1:],sample), axis = 1)
    udp.current_size += 1
    udp.str = ""
    #return the moving average 
    return np.sum(udp.buffer,axis = 1) / min(udp.window_size,udp.current_size)
               
   

#Helper functions for processing the message string
def until_space(string,udp):
    res = ''
    for char in string:
        if  char != " ":
            res += char 
        else:
            udp.minus_found = False
            break
    return res
def after_minus(string,udp):
    res = ''
    found = False
    for char in string:
        if char == '-':
            udp.minus_found = True
            found = True
        if found:
            if char != " ":
                res += char
            else:
                udp.minus_found = False
                break
    return res
 
if __name__ == '__main__':
    #Receiver specs
    rx_info = []
    info_rx0 = {
        'location': (0,0),
        'color': 'green',
        'noise floors': (-140,-140),
        'port': '0'
    }
    rx_info.append(info_rx0)
    info_rx1= {
        'location': (DIST_X,0),
        'color': 'blue',
        'noise floors': (-140,-140),
        'port': '2'
    }
    rx_info.append(info_rx1)
    # info_rx2= {
    #     'location': (SIDE,SIDE),
    #     'color': 'red',
    #     'noise floors': (-65,-65),
    #     'port': '2'
    # }
    # rx_info.append(info_rx2)
    # info_rx3= {
    #     'location': (0,SIDE),
    #     'color': 'orange',
    #     'noise floors': (-65,-65),
    #     'port': '3'
    # }
    # rx_info.append(info_rx3)

    #Establish the connection
    host = "192.168.0.2"
    port = 2323
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',50001))

    #Read using the socket thread
    udp = UDPConn(s, (host, port),num_rx = len(rx_info))
    th = threading.Thread(target=read_thread,args=(s, "name",udp))
    th.start()

    #Send the prompts to the transmitter asking the x_mag and z_mag values to the transmitter
    


    amps_avg = send_prompts(udp = udp, rx_info = rx_info)
    canvas, window, score_label, rx_list, lines, tag = setup_environment(udp,amps_avg,rx_info)
    #Display loop
    display_thread(udp,window,score_label,rx_list,rx_info,tag)
    udp.cmdloop()
    #python ./udpconn_v15.py