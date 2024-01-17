import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
# from mpl_toolkits.mplot3d import axes3d 
from matplotlib.ticker import LinearLocator
import itertools

# FC = 2*920 * 1e6
# C = 3 * 1e8
# lamb = C/FC
# B = 1000 #side length of a square room
R = 10
SIDE = 500

class Receiver:
    def __init__(self,x,y,sigma,canvas,height = 500, width = 500, dist_x = 10, dist_y = 10,color = 'green',slope = 1, intersect = 0, x_floor_db = -140, z_floor_db = -140) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.x_disp = x * (width / dist_x)
        self.y_disp = y * (height / dist_y)
        self.image = canvas.create_oval(self.x_disp-R,(height-self.y_disp)-R,self.x_disp+R,(height-self.y_disp)+R,fill = color)
        self.x_mag = 0 
        self.z_mag = 0
        self.x_floor = 10**(x_floor_db /10) 
        self.z_floor = 10**(z_floor_db /10) 
        self.on = True 
        # self.image = canvas.create_oval(x-R,y-R,x+R,y+R,fill = color)
        self.slope = slope
        self.intersect = intersect
        self.line = canvas.create_line(self.x_disp, height - self.y_disp, 0, 0, width = 2)
        self.sigma = sigma #each receiver can have a different error coefficient now
    
    def set_on(self,onoff = True): #set if the receiver is functioning
        self.on = onoff
    
    def set_floor(self,x_db,z_db ):
        self.x_floor = 10**(x_db /10)
        self.z_floor = 10**(z_db /10)

    def delete_line(self):
        self.canvas.delete(self.line)
        
    def set_line(self,x1,y1,height,width,dist_x,dist_y):
        x1_disp = x1 * (width / dist_x)
        y1_disp = y1 * (height/ dist_y)
        coord_update = [self.x_disp, height - self.y_disp, x1_disp, height - y1_disp]
        self.canvas.coords(self.line,coord_update)
         
    def get_xy(self):
        print(f'x: {self.x}, y: {self.y}')
    
    def set_mb(self,m,b):
        self.slope = m
        self.intersect = b
                            
    def get_amps(self):
        return self.x_mag,self.y_mag
    
    def set_amps(self,x,z):
        self.x_mag = x
        self.z_mag = z

    def set_xy(self,x0,y0):
        self.x = x0
        self.y = y0

    """""
    Calculates the errored angle for a given point in the room
    Parameters:
        x0: x coordinate of the tag
        y0: y coordinate of the tag
        b: length of a side of the square room
    Returns:
        phi_e: angle from receiver to tag (with error)
    """""
    def calculate_angle(self,x0,y0):
        assert x0 < B and y0 < B, 'The tag must be inside the room'
        slope = (y0-self.y)/(x0-self.x)
        phi1 = np.arctan(slope)
        if phi1 >= 0:
            theta1 = math.pi/2 - phi1   
        else:
            theta1 = phi1

        #introduce error to the angle
        theta_e = np.arctan(math.tan(theta1) * np.sqrt(1 + self.sigma)) 
        
        if theta_e >= 0:
            phi_e = math.pi/2 - theta_e
        else:          
            phi_e  = theta_e
        return phi_e

    """""
    Returns the parameters of a line with the equation y = mx + b
    Parameters:
        x0: x coordinate of the tag
        y0: y coordinate of the tag
    Returns:
        m,b in the equation of the line given above
    """""
    def line_params(self,x0,y0):
        m = np.tan(self.calculate_angle(x0,y0))
        b = self.y - m * self.x
        return m,b