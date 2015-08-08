import tkinter as tk
import tkinter.filedialog
from PIL import Image, ImageTk
import glob
import os
import csv

class App( tk.Tk ):
    def __init__( self ):
        tk.Tk.__init__( self )
        
        tk.Button(self, text = "open frame folder", command = self.askdir).pack()
        tk.Label(self, text = "enter glob").pack()
        self.globentry = tk.Entry(self)
        self.globentry.pack()
        self.globentry.insert(0, "*[!seg].jpg")
        self.form = tk.Entry(self)
        self.form.pack()
        self.form.insert(0, "img_?.jpg")
		
    def askdir(self):
        self.file_path = tk.filedialog.askdirectory()
        #self.file_path = "c:/users/sbf/desktop/images"
        os.chdir(self.file_path)
        self.initialize()
			
    def initialize(self):
        self.win = tk.Toplevel()
        
        self.ii = 0
        
        self.imagenames = glob.glob(self.globentry.get())
        self.reorder_names()
        self.data = (len(self.imagenames))*[None]
        img = Image.open(self.imagenames[self.ii])
        self.imwidth, self.imheight = img.size
        self.tkimg = ImageTk.PhotoImage(img)
        
        self.frame1 = tk.Frame(self.win)
        self.frame2 = tk.Frame(self.win)
        self.canvas = tk.Canvas(self.frame2, width = self.imwidth, height = self.imheight)
        self.cimg = self.canvas.create_image(0, 0, image = self.tkimg , anchor = tk.NW)
        self.canvas.configure(highlightthickness=0)
        self.scb = tk.Scrollbar(self.frame2, orient = tk.VERTICAL)
        self.listbox = tk.Listbox(self.frame2, width = 35, yscrollcommand=self.scb.set, selectmode=tk.SINGLE, activestyle="none")#, selectbackground="#FFFF66", selectforeground="black")
        self.save_button = tk.Button(self.frame1, text = "Save", command = self.save_data)
        self.load_button = tk.Button(self.frame1, text = "Load", command = self.load_data)
        self.save_location = None
        self.label = tk.Label(self.frame1, text = "Right Arrow: Next, Left Arrow: Prev, Right-Click: No Object")
        self.scb.config(command=self.listbox.yview)
        for i in self.imagenames:
            self.listbox.insert(tk.END, " "*3 + i)
        self.listbox.itemconfig(self.ii, bg="#FFFF66")
        
        self.win.bind("<Right>", self.next_image)
        self.win.bind("<Left>", self.prev_image)
        self.canvas.bind("<B1-Motion>", self.clicked)
        self.canvas.bind("<ButtonRelease-1>", self.new_rect)
        self.canvas.bind("<Button-3>", self.clear_rect)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_select)
        
        self.state = "idle"
        self.flag_has_rect = False
        
        pad = 3
        
        self.frame1.pack()
        self.frame2.pack(fill=tk.Y, expand=1)
        self.label.pack(side=tk.LEFT, padx=pad, pady=pad)
        self.load_button.pack(side = tk.RIGHT, padx=pad, pady=pad)
        self.save_button.pack(side = tk.RIGHT, padx=pad, pady=pad)
        self.canvas.pack(side = tk.LEFT)
        self.scb.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.RIGHT, fill = tk.BOTH, expand = 1)
    
    def reorder_names(self):
        form = self.form.get()
        ff = form.split("?")
        #print(ff)
        results = []
        for i,val in enumerate(self.imagenames):
            _,_,rest = val.partition(ff[0])
            result,_,_ = rest.partition(ff[1])
            results.append(int(result))
        sresult = sorted(range(len(results)), key=lambda k: results[k])
        names = [self.imagenames[i] for i in sresult]
        self.imagenames = names
    
    def listbox_select(self, event):
        self.save_rect()
        w = self.listbox.curselection()
        #print(w)
        self.listbox.select_clear(int(w[0]))
        self.ii = int(w[0])
        self.listbox.itemconfig(self.ii, bg="#FFFF66")
        self.clear_draw()
        self.draw_stored_rect()
        self.flag_yview = False
        self.display_image()
    
    
    def display_image(self):
        img = Image.open(self.imagenames[self.ii])
        w,h = img.size
        if w != self.imwidth or h != self.imheight:
            self.canvas.configure(width = w, height = h)
            self.imwidth = w
            self.imheight = h
        self.tkimg = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.cimg, image = self.tkimg)
        if self.ii > 10 and self.flag_yview:
            self.listbox.yview(self.ii-11)
    
    
    def next_image(self, event):
        #print("next")
        if self.ii+1 < len(self.imagenames):
            self.listbox.itemconfig(self.ii, bg="white")
            self.save_rect()
            self.ii += 1
            self.listbox.itemconfig(self.ii, bg="#FFFF66")
            if self.data[self.ii] != None:
                self.clear_draw()
            #print(self.data[self.ii])
            self.draw_stored_rect()
            self.flag_yview = True
            self.display_image()

        
    def prev_image(self, event):
        #print("prev")
        if self.ii-1 > -1:
            self.listbox.itemconfig(self.ii, bg="white")
            self.save_rect()
            self.ii -= 1
            self.listbox.itemconfig(self.ii, bg="#FFFF66")
            if self.data[self.ii] != None:
                self.clear_draw()
            #print(self.data[self.ii])
            self.draw_stored_rect()
            self.flag_yview = True
            self.display_image()
            
    def save_rect(self):
        if self.flag_has_rect:
            self.data[self.ii] = self.canvas.coords(self.rect)
            #print(self.data[self.ii])
            self.listbox.itemconfig(self.ii, bg = "#199643")
        elif self.data[self.ii] != None:
            self.listbox.itemconfig(self.ii, bg = "#3366CC")
        else:
            self.listbox.itemconfig(self.ii, bg = "white")
        
    def clicked(self, event):
        #print("xy ", event.x, event.y)
        if self.flag_has_rect:
            points = self.canvas.coords(self.rect)
        if self.state == "idle":
            if self.flag_has_rect:
                xleft = points[0]
                xright = points[2]
                ytop = points[1]
                ybot = points[3]
                buf = 30
                tl = self.dist([xleft, ytop], [event.x, event.y])
                tr = self.dist([xright, ytop], [event.x, event.y])
                bl = self.dist([xleft, ybot], [event.x, event.y])
                br = self.dist([xright, ybot], [event.x, event.y])
                if tl < buf:
                    self.state = "resizing"
                    self.point = [event.x, event.y]
                    self.resize_corner = "tl"
                elif tr < buf:
                    self.state = "resizing"
                    self.point = [event.x, event.y]
                    self.resize_corner = "tr"
                elif bl < buf:
                    self.state = "resizing"
                    self.point = [event.x, event.y]
                    self.resize_corner = "bl"
                elif br < buf:
                    self.state = "resizing"
                    self.point = [event.x, event.y]
                    self.resize_corner = "br"
                elif event.x > xleft and event.x < xright and event.y > ytop and event.y < ybot:
                    self.state = "moving"
                    self.point = [event.x, event.y]
                else:
                    self.canvas.delete(self.rect)
                    self.rect = self.canvas.create_rectangle(event.x, event.y, event.x+5, event.y+5, fill = "", outline = "blue", width = 3)
                    self.point = [event.x, event.y]
                    self.state = "drawing" 
            else:
                self.rect = self.canvas.create_rectangle(event.x, event.y, event.x+5, event.y+5, fill = "", outline = "blue", width = 3)
                self.point = [event.x, event.y]
                self.state = "drawing"
                self.flag_has_rect = True
                
        elif self.state == "drawing":
            minx = min(event.x, self.point[0])
            maxx = max(event.x, self.point[0])
            miny = min(event.y, self.point[1])
            maxy = max(event.y, self.point[1])
            #print(minx,miny,maxx,maxy)
            self.canvas.coords(self.rect, minx, miny, maxx, maxy)
        elif self.state == "moving":
            xoff = event.x - self.point[0]
            yoff = event.y - self.point[1]
            self.point = [event.x, event.y]
            #print(minx,miny,maxx,maxy)
            self.canvas.coords(self.rect, points[0]+xoff, points[1]+yoff, points[2]+xoff, points[3]+yoff)
        elif self.state == "resizing":
            xoff = event.x - self.point[0]
            yoff = event.y - self.point[1]
            self.point = [event.x, event.y]
            if self.resize_corner == "tl":
                self.canvas.coords(self.rect, points[0]+xoff, points[1]+yoff, points[2], points[3])
            elif self.resize_corner == "tr":
                self.canvas.coords(self.rect, points[0], points[1]+yoff, points[2]+xoff, points[3])
            elif self.resize_corner == "bl":
                self.canvas.coords(self.rect, points[0]+xoff, points[1], points[2], points[3]+yoff)
            elif self.resize_corner == "br":
                #print(xoff, yoff)
                self.canvas.coords(self.rect, points[0], points[1], points[2]+xoff, points[3]+yoff)

            
    def snap_to_border(self):
        if self.flag_has_rect == True:
            points = self.canvas.coords(self.rect)
            points = [max(0,x) for x in points]
            w = self.imwidth
            h = self.imheight
            if points[2] > w:
                points[2] = w
            if points[3] > h:
                points[3] = h
            self.canvas.coords(self.rect, points[0], points[1], points[2], points[3])
            
    def new_rect(self, event):
        self.state = "idle"
        self.snap_to_border()
    
    def dist(self, p1, p2):
        return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
    
    def clear_rect(self, event):
        if self.flag_has_rect:
            self.canvas.delete(self.rect)
            self.flag_has_rect = False
        self.state = "idle"
        self.data[self.ii] = ["NaN","NaN","NaN","NaN"]
    
    def clear_draw(self):
        if self.flag_has_rect:
            self.canvas.delete(self.rect)
            self.flag_has_rect = False
        
    def draw_stored_rect(self):
        if self.data[self.ii] != None and self.data[self.ii][0] != "NaN":
            minx = self.data[self.ii][0]
            miny = self.data[self.ii][1]
            maxx = self.data[self.ii][2]
            maxy = self.data[self.ii][3]
            if self.flag_has_rect:
                self.canvas.coords(self.rect, minx, miny, maxx, maxy)
            else:
                self.rect = self.canvas.create_rectangle(minx, miny, maxx, maxy, fill = "", outline = "blue", width = 3)
                self.flag_has_rect = True
    
    def save_data(self):
        self.save_rect()
        if self.save_location == None:
            self.save_location = tk.filedialog.asksaveasfilename()
        fid = open(self.save_location, "w")
        for i, val in enumerate(self.data):
            if not val == None:
                if not val[0] == "NaN":
                    towrite = self.imagenames[i] + "," + ','.join(str(int(n)) for n in val) + "\n"
                else:
                    towrite = self.imagenames[i] + "," + ','.join(val) + "\n"
            else:
                towrite = self.imagenames[i] + "," + "unchecked" + "\n"
            fid.write(towrite)
        fid.close()
        print("data saved")
        
    def load_data(self):
        print("loading data")
        fid = open(tk.filedialog.askopenfilename(), "r")
        reader = csv.reader(fid)
        for val in reader:
            idx = self.imagenames.index(val[0])
            if val[1] != "unchecked":
                if val[1] != "NaN":
                    self.data[idx] = [int(x) for x in val[1:6]]
                    self.listbox.itemconfig(idx, bg = "#199643")
                else:
                    self.data[idx] = ["NaN", "NaN", "NaN", "NaN"]
                    self.listbox.itemconfig(idx, bg = "#3366CC")
            self.draw_stored_rect()
        print("data loaded")
        fid.close()
        

app = App()
app.mainloop()
