# Author: Berk Bozkurt
# Date: February 15, 2024

import numpy as np
import pandas as pd
import cmd
import socket
import os
import sys
import threading
import time
from datetime import date
from tkinter import *
from Receiver_v5 import *
from Tag_v2 import *
from PIL import ImageTk, Image


# #Global vars
DIST_STRAIGHT = 8
DIST_X = 4
DIST_Y = 6
HEIGHT = 750
WIDTH = 500
L = DIST_Y * 4
R = 5
todays_date = date.today()

class UDPConn(cmd.Cmd):
    prompt = '' 

    def __init__(self, s, destination, num_rx = 4, window_size = 5, est_window = 5):
        cmd.Cmd.__init__(self)
        self.s = s
        self.destination = destination
        self.minus_found = False
        self.str = "" 
        self.window_size = window_size
        self.current_size = 0
        self.num_rx = num_rx 
        self.buffer = np.zeros((2*self.num_rx,self.window_size))
        self.est_window = est_window
        self.current_est_size = 0
        self.est_buffer = np.zeros((2,self.est_window))
        self.estimates = [(DIST_X/2,DIST_Y/2)]
        self.running = False
        self.data = pd.DataFrame(columns = set_data_cols(self.num_rx))

    def reset_data(self):
        self.data = pd.DataFrame(columns = set_data_cols(self.num_rx))

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
    
def set_data_cols(num_rx):
    lst = []
    for i in range(num_rx):
        # lst.append(f'Px{i}')
        lst.append(f'Py{i}')
        lst.append(f'Pz{i}')
    lst.append('time')
    return lst

def set_window(udp):
    entry_list = []
    inlan_color = '#0A0D35'
    window = Tk()
    window.title('Real-time Tracking')
    window.geometry("300x550")
    # canvas = Canvas(window,width=WIDTH,height=HEIGHT,bg = 'gray')
    # canvas.pack(padx= 1,pady=1, side = 'right') 
    path = 'inlan_logo.png'
    img = ImageTk.PhotoImage(Image.open(path).resize((50,50)))
    logo = Label(window, image = img)
    logo.place(x = 10, y = 10)

    labelText1=StringVar()
    labelText1.set("Port 0 - Rx location")
    label1=Label(window, textvariable=labelText1, font = ('Helvetica',12))
    label1.place(x=15,y = 90)

    global e1
    e1 = Entry(window,width = 7, font = ('Helvetica',12),fg = inlan_color)
    e1.focus_set()
    e1.insert(0,'8.5,5') 
    e1.place(x = 165, y = 92)
    entry_list.append(e1)

    global e2
    labelText2=StringVar()
    labelText2.set("Port 1 - Rx location")
    label2=Label(window, textvariable=labelText2, font = ('Helvetica',12))
    label2.place(x = 15, y = 130)
    e2 = Entry(window,width = 7, font = ('Helvetica',12),fg = inlan_color)
    e2.insert(0,'13.6,2.8') 
    e2.place(x = 165, y = 132)
    entry_list.append(e2)

    global e3
    labelText3=StringVar()
    labelText3.set("Port 2 - Rx location")
    label3=Label(window, textvariable=labelText3, font = ('Helvetica',12))
    label3.place(x = 15, y = 170)
    e3 = Entry(window,width = 7, font = ('Helvetica',12),fg = inlan_color)
    e3.insert(0,'8.5,21.9') 
    e3.place(x = 165, y = 172)
    entry_list.append(e3)

    global e4
    labelText4=StringVar()
    labelText4.set("Port 3 - Rx location")
    label4=Label(window, textvariable=labelText4, font = ('Helvetica',12))
    label4.place(x = 15, y = 210)
    e4 = Entry(window, width = 7, font = ('Helvetica',12), fg = inlan_color)
    e4.insert(0,'17.5,14') 
    e4.place(x = 165, y = 212)
    entry_list.append(e4)

    global tx_entry
    tx_text=StringVar()
    tx_text.set("Tx location")
    tx_label=Label(window, textvariable=tx_text, font = ('Helvetica',12))
    tx_label.place(x = 15, y = 250)
    tx_entry = Entry(window, width = 7, font = ('Helvetica',12), fg = inlan_color)
    tx_entry.insert(0,'8.5,13') 
    tx_entry.place(x = 165, y = 252)

    global height_entry
    h_text=StringVar()
    h_text.set("Tag height")
    h_label=Label(window, textvariable=h_text, font = ('Helvetica',12))
    h_label.place(x = 15, y = 290)
    height_entry = Entry(window, width = 7, font = ('Helvetica',12), fg = inlan_color)
    height_entry.insert(0,'0.6') 
    height_entry.place(x = 165, y = 292)


    labelText5=StringVar()
    labelText5.set("Starting position")
    label5=Label(window, textvariable=labelText5, font = ('Helvetica',12))
    label5.place(x = 15, y = 330)
    global start_pos_entry
    start_pos_entry = Entry(window, width = 7, font = ('Helvetica',12), fg = inlan_color)
    # e5.insert(0,'10,10') 
    start_pos_entry.place(x = 165, y = 332)
    # entry_list.append(start_pos_entry)


    fin_text=StringVar()
    fin_text.set("Finish position")
    fin_label=Label(window, textvariable=fin_text, font = ('Helvetica',12))
    fin_label.place(x = 15, y = 370)
    global finish_pos_entry
    finish_pos_entry = Entry(window, width = 7, font = ('Helvetica',12), fg = inlan_color)
    # e5.insert(0,'10,10') 
    finish_pos_entry.place(x = 165, y = 372)

    freq_text=StringVar()
    freq_text.set("Frequency (MHz)")
    freq_label=Label(window, textvariable=freq_text, font = ('Helvetica',12))
    freq_label.place(x = 15, y = 410)
    global freq_entry
    freq_entry = Entry(window, width = 7, font = ('Helvetica',12), fg = inlan_color)
    freq_entry.insert(0,'915.5') 
    freq_entry.place(x = 165, y = 412)


    labelText6=StringVar()
    labelText6.set("file name")
    label6=Label(window, textvariable=labelText6, font = ('Helvetica',12))
    label6.place(x = 15, y = 450)
    file_name_entry = Entry(window, width = 10, font = ('Helvetica',12), fg = inlan_color)
    file_name_entry.insert(0,'data_apr_' + str(todays_date.day) )
    file_name_entry.place(x = 165, y = 452)


    b1 = Button(window, text = 'Start' , command = lambda: start(udp,entry_list,file_name_entry, window), width = 20,bg = inlan_color, fg = 'white', font = ('Helvetica',12))
    b1.place(x = 20,y = 480)


    b2 = Button(window, text = 'Stop' , command = lambda: stop(window), width = 20,bg = inlan_color, fg = 'white', font = ('Helvetica',12))
    b2.place(x = 20,y = 520)

    # score_label = Label(window, text = 'Tag Location (x,y) = 3.42, 5.45', font = ('Helvetica',12), fg = inlan_color)
    # score_label.place(x = 5, y = 420)
    window.mainloop()

    return entry_list, b1, window

def read_thread(sock, name, udp):
    while True:
        s = sock.recv(65536)
        os.write(sys.stdout.fileno(), s) #probably don't need to do this, slowing things down by prnting on command prompt
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
        # x_prompt = port_index + "show /rf/xmag_dbm\n"
        y_prompt = port_index + "show /rf/ymag_dbm\n"
        z_prompt = port_index + "show /rf/zmag_dbm\n"
        # udp.s.sendto(x_prompt.encode(),udp.destination)
        # time.sleep(0.01)
        udp.s.sendto(y_prompt.encode(),udp.destination)
        time.sleep(0.005)
        udp.s.sendto(z_prompt.encode(),udp.destination)
        time.sleep(0.005)
    time.sleep(0.01) #wait before interpreting the responses to the prompts 
      
    #interpret the response to the prompts 
    #str attribute of the udp object have the decoded message received from the transmitter
    sample = np.zeros((2*num_rx + 1,))
    message = udp.str.split('-') #processed response message 
    for i in range(num_rx):
        y_mag_db = -float(message[2*i+1]) #add 1 to not use anything before the first '-'
        z_mag_db = -float(message[2*i+2])
        # z_mag_db = -float(message[3*i+3])

        sample[2*i] = y_mag_db
        sample[2*i+1] = z_mag_db
        # sample[3*i+2] = z_mag_db

    udp.str = "" #clear the message for the next prompt
    sample[-1] = time.time() - time_start #add the time stamp to the sample  
    return sample
   
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

def specs(entry_list):
    color_list = ['green', 'blue', 'red', 'orange']
    rx_info = []
    for i, entry in enumerate(entry_list):
        text = entry.get()
        if len(text) != 0:
            x,y = text.split(',')
            info = {
                'location': (float(x),float(y)),
                'color': color_list[i],
                'noise floors': (-300,-300), #change this to modify when the receiver is considered operational 
                'port': str(i)
            }
            rx_info.append(info)
    return rx_info

def start(udp, entry_list, file_name_entry,window):
    # window.update()
    global time_start
    if not udp.running:
        udp.running = True
        time_start = time.time()
    rx_info = specs(entry_list)
    collect_data(udp = udp ,window = window ,rx_info = rx_info, num_intervals = 20, file_name = file_name_entry.get())

def stop(window):
    window.update()
    if udp.running:
        udp.running = False
    global time_elapsed 
    time_elapsed = time.time() - time_start
    # window.update()
    print(f'Total time elapsed is {time_elapsed} seconds')
    

def collect_data(udp,window,rx_info, num_intervals = 10, file_name = 'data_collected'):
    while True:
        sample = send_prompts(udp,rx_info)
        # print(sample)
        udp.data.loc[len(udp.data.index)] = sample
        window.update()
        if not udp.running:
            time_array = np.linspace(0,time_elapsed,num_intervals+1)
            # map_time(udp,udp.data,time_array,num_points = 3, file_name = file_name)
            # udp.data.to_csv(file_name + '.csv')
            add_ground_truth(data = udp.data, x0 = 0, y0 = 0, num_intervals = num_intervals, file_name = file_name + '_loc')
            udp.reset_data()
            break

def add_ground_truth(data,x0,y0,num_intervals,file_name, is_rectangle = False):
    start_x = float(start_pos_entry.get().split(",")[0])
    start_y = float(start_pos_entry.get().split(",")[1])

    end_x = float(finish_pos_entry.get().split(",")[0])
    end_y = float(finish_pos_entry.get().split(",")[1])
    
    freq = float(freq_entry.get())

    #Get receiver locations
    rx0_x = float(e1.get().split(",")[0])
    rx0_y = float(e1.get().split(",")[1])
    rx1_x = float(e2.get().split(",")[0])
    rx1_y = float(e2.get().split(",")[1])
    rx2_x = float(e3.get().split(",")[0])
    rx2_y = float(e3.get().split(",")[1])
    rx3_x = float(e4.get().split(",")[0])
    rx3_y = float(e4.get().split(",")[1])

    #Get transmitter location
    tx_x = float(tx_entry.get().split(",")[0])
    tx_y = float(tx_entry.get().split(",")[1])

    tag_h = float(height_entry.get())

    num_rows = len(data.index)
    # x_list, y_list = divide_rectangle(x0 = x0, y0 = y0, side_a = DIST_X, side_b = DIST_Y, num_intervals = num_rows-1)
    if is_rectangle:
        total_distance = (DIST_X + DIST_Y) * 2
    else:
        total_distance = DIST_STRAIGHT
    dist = np.linspace(0,((end_y - start_y)**2 + (end_x - start_x)**2)**(0.5),num_rows)
    y_values = np.linspace(start_y,end_y,num_rows)
    x_values = np.linspace(start_x,end_x,num_rows)
    # x_values = np.full(y_values.shape,start_x)
    # bin_array = np.linspace(0,total_distance,num_intervals+1)[1:]
    # class_list = np.digitize(dist, bins = bin_array, right = True)
    # data.insert(len(data.columns),'x',x_list)
    # data.insert(len(data.columns),'y',y_list)

    data.insert(len(data.columns),'tag_height',np.full(y_values.shape,tag_h))
    data.insert(len(data.columns),'frequency',np.full(y_values.shape,freq))
    
    data.insert(len(data.columns),'tx_x',np.full(y_values.shape,tx_x))
    data.insert(len(data.columns),'tx_y',np.full(y_values.shape,tx_y))

    data.insert(len(data.columns),'rx0_x',np.full(y_values.shape,rx0_x))
    data.insert(len(data.columns),'rx0_y',np.full(y_values.shape,rx0_y))

    data.insert(len(data.columns),'rx1_x',np.full(y_values.shape,rx1_x))
    data.insert(len(data.columns),'rx1_y',np.full(y_values.shape,rx1_y))

    data.insert(len(data.columns),'rx2_x',np.full(y_values.shape,rx2_x))
    data.insert(len(data.columns),'rx2_y',np.full(y_values.shape,rx2_y))

    data.insert(len(data.columns),'rx3_x',np.full(y_values.shape,rx3_x))
    data.insert(len(data.columns),'rx3_y',np.full(y_values.shape,rx3_y))




    data.insert(len(data.columns),'x',x_values)
    data.insert(len(data.columns),'y',y_values)

    # data.insert(len(data.columns),'y',y_values)

    data.insert(len(data.columns),'distance',dist)
    # data.insert(len(data.columns),'class',class_list)
    data.to_csv(file_name + '.csv')

def divide_rectangle(x0, y0, side_a, side_b, num_intervals):
    l = 2 * (side_a + side_b)
    # coords = np.zeros((num_intervals+1,2))
    lst_x = []
    lst_y = []
    x_start = x0 + side_a / 2
    y_start = y0
    # coords[0,:] = [x0,y0]
    line_array = np.linspace(0,l,num_intervals + 1)
    for i,k in enumerate(line_array):
        if k < side_a / 2:
            x = x_start + k
            y = y0
        elif k >= side_a / 2 and k < side_a / 2 + side_b:
            x = x_start + side_a / 2
            y = y0 + (k - side_a / 2)

        elif k >= side_a / 2 + side_b and k < side_a / 2 + side_a + side_b:
            x = x0 + side_a - (k - (side_a / 2 + side_b))
            y = y0 + side_b
        elif k >= side_a / 2 + side_a + side_b and k < side_a / 2 + side_a + 2 * side_b:
            x = x0
            y = y0 + side_b - (k - (side_a / 2 + side_a +  side_b))
        else:
            x = x0 + k - (side_a / 2 + side_a + 2 * side_b)
            y = y0
        lst_x.append(x)
        lst_y.append(y)
    return lst_x, lst_y


def map_time(udp,data,time_array,num_points, file_name):
    data_arr = data.to_numpy()
    new_df = pd.DataFrame(columns = set_data_cols(udp.num_rx))
    for t in time_array:
        ind = np.argmin(np.abs(data_arr[:,-1]-t)) #index of the closest time stamp
        if ind == 0:
            row = np.average(data_arr[0:num_points+1,:], axis = 0)
        elif ind == len(data_arr[:,-1]) - 1:
            row = np.average(data_arr[ind-num_points:ind+1,:], axis = 0)
        else:
            row = np.average(data_arr[ind-num_points:ind+num_points+1,:], axis = 0)
        row[-1] = t #put the timestamp as the actual time
        print(row)
        new_df.loc[len(new_df.index)] = row
    new_df.to_csv(file_name + '_processed.csv')

if __name__ == '__main__':
    #Establish the connection
    host = "192.168.0.2"
    port = 2323
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',50001))

    #Receiver specs example
    # rx_info = []
    # info_rx0 = {
    #     'location': (0,0),
    #     'color': 'green',
    #     'noise floors': (-140,-140),
    #     'port': '0'
    # }
    # rx_info.append(info_rx0)

    #Read using the socket thread
    NUM_RX = 4

    udp = UDPConn(s, (host, port),num_rx = NUM_RX)
    th = threading.Thread(target=read_thread,args=(s, "name",udp))
    th.start()
    entry_list, button, window = set_window(udp)
    udp.cmdloop()
    #to run the script
    #python ./collect_data_v6.py`