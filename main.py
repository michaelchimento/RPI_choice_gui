#written by michael chimento; May 2023

#flag to be able to test the code on a laptop. will need to remove by the time it gets deployed
rpi = False

import tkinter as tk
import random
import time
import datetime as dt
import csv

if rpi:
    import RPi.GPIO as GPIO
    from adafruit_motorkit import MotorKit
    from adafruit_motor import stepper

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4,GPIO.IN)

def rotate_motor(steps=400):
    pull_style = stepper.MICROSTEP
    kit = MotorKit()
    for x in range(self.steps):
        self.kit.stepper1.onestep(direction=stepper.BACKWARD, style=self.pull_style)
    kit.stepper1.release()
    time.sleep(0.5)

class StimuliApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Stimuli Task")
        self.master.attributes('-fullscreen', True)

        self.canvas = tk.Canvas(self.master, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.trial_number = 0
        self.trial_start_time = dt.datetime.now()
        self.trial_data = []

        self.create_shapes()
        self.master.bind("<Escape>", lambda e: self.quit_app())

    def create_shapes(self):
    
        #set parameters
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        size = 400
        
        #remove everything from canvas
        self.canvas.delete('all')

        #randomly pick 2 positions
        positions = random.sample(['left', 'center' , 'right'], k=2)
        
        #define dictionary of x positions for shapes, where-ever they may go
        position_to_x = {'left': screen_width // 6 - size // 2 + random.randint(-1,1), 
                        'center': screen_width // 2 - size // 2 + random.randint(-1,1), 
                        'right': 5 * screen_width // 6 - size // 2 + random.randint(-1,1)}
        #choose indexs of randomly chosen positions
        x_triangle = position_to_x[positions[0]]
        x_circle = position_to_x[positions[1]]
        
        y = screen_height // 2 - size // 2 + random.randint(-50,50)
        
        self.create_triangle(x_triangle, y, size, 'lightblue','triangle','correct')
        self.create_circle(x_circle, y, size, 'lightgreen','circle','incorrect')
        
        #set the trial start time
        self.trial_start_time = dt.datetime.now()

    def create_triangle(self, x, y, size, color, symbol, status):
        ghost_size=self.master.winfo_screenwidth()//7
        self.canvas.create_rectangle(x-ghost_size//2, 0, x + ghost_size*2, self.master.winfo_screenheight(), fill="black", tags=(symbol, color, status))
        
        points = [x, y - size // 2, x + size, y - size // 2, x + size // 2, y + size // 2]
        self.canvas.create_polygon(points, fill=color, tags=(symbol, color, status))
        self.canvas.tag_bind(status, "<Button-1>", self.on_shape_click)
        #self.canvas.tag_bind(status, "<Button-1>", self.on_shape_click)

    def create_circle(self, x, y, size, color, symbol, status):
        ghost_size=self.master.winfo_screenwidth()//7
        self.canvas.create_rectangle(x-ghost_size//2, 0, x + ghost_size*2, self.master.winfo_screenheight(), fill="black", tags=(symbol, color, status))
        
        
        self.canvas.create_oval(x, y, x + size, y + size, fill=color, tags=(symbol, color,status))
        self.canvas.tag_bind(status, "<Button-1>", self.on_shape_click)
        #self.canvas.tag_bind(status, "<Button-1>", self.on_shape_click)
        
    def success_cue(self):
        #creates a colored rectangle that fills the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        color="green"
        self.canvas.create_rectangle(0,0,screen_width,screen_height,fill="white")

    def on_shape_click(self, event):

        self.trial_number += 1
        item = self.canvas.find_withtag(tk.CURRENT)[0]
        tags = self.canvas.gettags(item)
        symbol = tags[0]
        color = tags[1]

        response_time = dt.datetime.now()
        is_correct = symbol == 'triangle'

        trial_info = {
            'trial_number': self.trial_number,
            'trial_start_time': self.trial_start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'response_time': response_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'symbol': symbol,
            'color': color,
            'is_correct': is_correct
        }

        self.trial_data.append(trial_info)
        self.write_trial_data_to_csv(trial_info)

        if not is_correct:
            self.canvas.delete('all')
            self.canvas.create_text(self.master.winfo_screenwidth() // 2, self.master.winfo_screenheight() // 2, text= "LOCKED",fill="white",font=('Helvetica 15 bold'))
            
            self.master.after(5000, self.create_shapes)
        else:
            #insert code to run motor here
            #show a green screen while motors run
            self.success_cue()
            if rpi:
                rotate_motor(steps=400)
            #recreate shapes for next trial
            self.master.after(1000, self.create_shapes)

    def write_trial_data_to_csv(self, trial_info):
        with open('trial_data.csv', 'a', newline='') as csvfile:
            fieldnames = ['trial_number', 'trial_start_time', 'response_time', 'symbol', 'color', 'is_correct']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if self.trial_number == 1:
                writer.writeheader()
            writer.writerow(trial_info)

    def quit_app(self):
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StimuliApp(root)
    root.mainloop()

