
class Tag:
    BORDER = 50
    def __init__(self,x,y,canvas,height,width,dist_x,dist_y,x_vel = 0,y_vel = 0,color = 'red', R = 5) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.x_disp = x * (width / dist_x)
        self.y_disp = y * (height / dist_y)
        self.image = canvas.create_oval(self.x_disp-R,(height - self.y_disp )-R,self.x_disp+R,(height - self.y_disp )+R,fill = color)
        self.x_vel = x_vel 
        self.y_vel = y_vel 

    def get_xy(self):
        print(f'x: {self.x}, y: {self.y}')
    
    def set_xy(self,x0,y0):
        self.x = x0
        self.y = y0

    def move(self):
        coordinates = self.canvas.coords(self.image)

        if(coordinates[2]>=(self.canvas.winfo_width()-BORDER) or coordinates[0]<BORDER):
            self.x_vel = -self.x_vel
        if(coordinates[3]>=(self.canvas.winfo_height()-BORDER) or coordinates[1]<BORDER):
            self.y_vel = -self.y_vel

        self.canvas.move(self.image,self.x_vel,self.y_vel)
       
        self.x += self.x_vel 
        self.y += self.y_vel 


        