import time

try:                        # In order to be able to import tkinter for
    import tkinter as tk    # either in python 2 or in python 3
except:
    import Tkinter as tk
from PIL import Image, ImageTk


if __name__ == '__main__':
    mode = False
    def get_pstree_clicked():
        try:  # put to mainloop!
            tm = time.time()
            print("Getting process tree at", str(int(time.time())))
            my_label.configure(text=u'\u2713' + "Getting process tree at " + str(int(time.time())))
            label = tk.Label(root)
            img = Image.open(r"stock.jpg")
            label.img = ImageTk.PhotoImage(img)
            label['image'] = label.img
            label.grid(column=1, row=0)
        except:
            pass

    def run_reconstruction():
        try:  # put to mainloop!
            tm = time.time()
            print("Running reconstruction pipeline")
            my_label.configure(text=u'\u2713' + "Running reconstruction pipeline")
            label = tk.Label(root)
            img = Image.open(r"stock.jpg")
            label.img = ImageTk.PhotoImage(img)
            label['image'] = label.img
            label.grid(column=1, row=1)

        except:
            pass

        my_label.configure(text=u'\u2713' + "Reconstruction ends")

    def get_periodicaly():
        if v.get():
            print(str(v.get()))
            my_label.configure(text=u'\u2713'+"periodic pstree getting is activated")
            get_pstree_btn['state'] = 'disabled'
        else:
            print(str(v.get()))
            my_label.configure(text=u'\u2713'+"periodic pstree getting is deactivated")
            get_pstree_btn['state'] = 'normal'
        pass


    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry('%sx%s' % (int(width), int(height )))
    root.title('Bonsai')
    text_frame = tk.Frame(root, background="#CCE4CA", bd=1, relief="sunken")
    button_frame = tk.Frame(root, background="white", bd=1, relief="sunken")
    text_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=2, pady=2)
    button_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=2, pady=2)
    root.grid_rowconfigure(0, weight=3)
    root.grid_rowconfigure(1, weight=2)
    root.grid_columnconfigure(0, weight=3)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=2)
    # current state vars:
    v = tk.IntVar()
    current_snap = tk.StringVar()

    get_pstree_btn = tk.Button(button_frame, text="Get process tree", width=13, command=get_pstree_clicked)
    get_pstree_btn.grid(column=0, row=0)
    run_reconstr_btn = tk.Button(button_frame, text="Run reconstruction", width=13, command=run_reconstruction)
    run_reconstr_btn.grid(column=0, row=1)
    get_periodicaly_btn = tk.Checkbutton(button_frame, text="Get periodically", variable=v, onvalue=1,offvalue=0, width=13, command=get_periodicaly)
    get_periodicaly_btn.grid(column=0, row=2)
    my_label = tk.Label(root, text="\u2713Program started",width=30)
    my_label.grid(column=0, row=2)
    #my_label.pack()

    # NB: .config() can also be used

    root.mainloop()