from tkinter import *
from tkinter.scrolledtext import ScrolledText

mainwin = Tk()
# Label(mainwin, text="An Entry Box:").grid(row=0, column=0)
# ent = Entry(mainwin, width=70); ent.grid(row=0, column=1)
# Button(mainwin, text="Print Entry", command=(lambda: print(ent.get()))).grid(row=0, column=2, sticky="EW")

Label(mainwin, text="Your Solution").grid(row=1, column=0,columnspan=15)
Label(mainwin, text="Solution to hack").grid(row=1, column=16,columnspan=15)

source = ScrolledText(mainwin, height=5, width=60)
source.grid(row=2, column=0,padx=20, pady=(0,50),columnspan=15)
compare = ScrolledText(mainwin, height=5, width=60)
compare.grid(row=2, column=16,padx=20, pady=(0,50),columnspan=15)
Label(mainwin, text="Test Case Generator").grid(row=3, column=8,columnspan=15)
generator = ScrolledText(mainwin, height=5, width=60)
generator.grid(row=4, column=8,padx=20, pady=(0,50),columnspan=15)

def printer():
    global source, compare, generator
    print("Source:")
    print(source.get(1.0, END))
    print("Compare:")
    print(compare.get(1.0, END))
    print("Generator:")
    print(generator.get(1.0, END))

Button(mainwin, text="Execute", command=printer).grid(row=5, column=9, columnspan=3, sticky="EW",pady=(0,25))
# Button(mainwin, text="Print Text", command=(lambda: print(compare.get(1.0, END)))).grid(row=3, column=1, sticky="EW")

Button(mainwin, text="Exit", command=sys.exit).grid(row=5, column=19, columnspan=3, sticky="EW",pady=(0,25))
mainwin.mainloop()