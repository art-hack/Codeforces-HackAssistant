import tkinter as tk
from tkinter import messagebox,Tk, Label, Spinbox, Button, Text, END
import threading
from tkinter.scrolledtext import ScrolledText
import subprocess as sub
import os
import sys
import shutil

mainwin = Tk()
mainwin.title('Codeforces Hack Assistant')

Label(mainwin, text="Your Solution (CPP)").grid(row=1, column=0,columnspan=15)
Label(mainwin, text="Solution to hack (CPP)").grid(row=1, column=16,columnspan=15)

source = ScrolledText(mainwin, height=10, width=60)
source.grid(row=2, column=0,padx=20, pady=(0,50),columnspan=15)
compare = ScrolledText(mainwin, height=10, width=60)
compare.grid(row=2, column=16,padx=20, pady=(0,50),columnspan=15)
Label(mainwin, text="Test Case Generator (PYTHON)").grid(row=3, column=0,columnspan=15)
generator = ScrolledText(mainwin, height=10, width=60)
generator.grid(row=4, rowspan=3,column=0,padx=20, pady=(0,50),columnspan=15)
Label(mainwin, text="Number of Threads: ").grid(row=4, column=17,columnspan=5)
spin = Spinbox(mainwin, from_= 1, to = 16)
spin.grid(row=4,column = 22)
var1 = tk.IntVar()
checkbox = tk.Checkbutton(mainwin, text='Use Test Case Instead',variable=var1, onvalue=1, offvalue=0)
checkbox.grid(row=5,column=22)

tex=""
execute = ""
exit=""
continue_executing = True
workers = list()
test_num=1

mutex = threading.Lock()
available = threading.Lock()

if(not os.path.exists("usable")):
    os.mkdir("usable")


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if(os.path.exists("usable")):
            shutil.rmtree("usable")
        mainwin.destroy()


def printf(input,end="\n"):
    global tex
    tex.configure(state='normal')
    tex.insert(tk.END, input+end)
    tex.see(tk.END)
    tex.configure(state='disabled')


def passed():
    global mutex, test_num
    mutex.acquire()
    printf("Test Passed: "+str(test_num))
    test_num += 1
    mutex.release()


def exit2():
    global source, compare, generator, execute, spin, tex, workers, exit, continue_executing, workers, test_num
    continue_executing=False
    for i in range(len(workers)):
        workers[i].join()
        printf("Closed Worker: "+str(i+1))
    workers.clear()
    tex.configure(state='normal')
    checkbox.configure(state='normal')
    exit.configure(state='disabled')
    source.configure(state='normal')
    execute.configure(state='normal')
    spin.configure(state='normal')
    compare.configure(state='normal')
    generator.configure(state='normal')
    continue_executing = True
    test_num=1
    sys.exit()


def exitt():
    p = threading.Thread(target=exit2, name='exit2')
    p.start()


def rewrite(path, data):
	raw = open(path, "w")
	raw.write(data)
	raw.close()


def execut(name,input,type,num=0):
    # print(name,input,type)
    if(type=="Python"):
        p = sub.Popen('cd usable && python '+str(name)+'.py',stdout=sub.PIPE,stderr=sub.PIPE,shell = True)
    if(type=="C"):
        # print(str(name)+'<input.txt')
        rewrite("usable/input"+str(num)+".txt",str(input))
        # print('Rewrote input.txt')
        # print(str(name)+'<input'+num+'.txt')
        p = sub.Popen("cd usable && "+str(name)+'<input'+num+'.txt',stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
    try:
        output, errors = p.communicate(timeout=10)
    except sub.TimeoutExpired as e:
        p.kill()
        output, errors = p.communicate()
    return output.decode('ASCII'), errors.decode('ASCII')


def compares(input,pp):
    a = execut("source"+pp,input,"C",pp)
    b = execut("compare"+pp,input,"C",pp)
    if(a[1]!=""):
        printf("Runtime Error on Source!\n"+str(input)+"\n\n Error : "+a[1]+"Exiting Thread..")
        return False
    if(b[1]!=""):
        printf("Runtime Error on Hack!\n"+str(input)+"\n\n Error : "+a[1]+"Exiting Thread..")
        return False
    if(a[0]!=b[0]):
        printf("Output Mismatch on the following input!\n"+str(input)+"\nExiting..")
        exitt()
        return False
    return True


def run(pp,single=False):
    global continue_executing, available
    available.acquire()
    if(continue_executing==False):
        available.release()
        return
    p = sub.Popen('g++ usable/source.cpp -o usable/source'+pp,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    errors = errors.decode('ASCII')
    if(errors!=""):
        exitt()
        printf("Source Compilation Error!\nExiting..")
        available.release()
        return
    p = sub.Popen('g++ usable/compare.cpp -o usable/compare'+pp,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    errors = errors.decode('ASCII')
    if(errors!=""):
        printf("Solution to Hack Compilation Error!\nExiting..")
        exitt()
        available.release()
        return
    if(not single):
        rewrite("usable/generator"+pp+".py",generator.get(1.0, END))
    available.release()
    
    while(continue_executing):
        if single:
            result = compares(str(generator.get(1.0, END)),pp)
            if(result):
                passed()
            exitt()
            return

        generate=execut('generator'+pp,"","Python")
        if(generate[1]!=""):
            printf("Generator Error!\n"+generate[1]+"\nExiting..")
            exitt()
            return
        result = compares(generate[0],pp)
        if(result):
            passed()
        else:
            return



def printer():
    global source, compare, generator, execute, spin, tex, workers, exit, checkbox, var1
    tex = Text(mainwin,height=10, width=120)
    tex.grid(row=7,padx=20,pady=(0,20), column=0,columnspan=30)
    rewrite("usable/source.cpp",source.get(1.0, END))
    rewrite("usable/compare.cpp",compare.get(1.0, END))
    tex.configure(state='disabled')
    checkbox.configure(state='disabled')
    exit.configure(state='normal')
    source.configure(state='disabled')
    execute.configure(state='disabled')
    spin.configure(state='disabled')
    compare.configure(state='disabled')
    generator.configure(state='disabled')
    if(var1.get()==1):
        p = threading.Thread(target=run, args=(str(0),True),name=str(0))
        p.start()
        workers.append(p)
        printf("Started Thread: 1")
    else:    
        for i in range(int(spin.get())):
            p = threading.Thread(target=run, args=(str(i)),name=str(i))
            p.start()
            workers.append(p)
            printf("Started Thread: "+str(i+1))
    return


execute = Button(mainwin, text="Execute", command=printer)
execute.grid(row=6, column=18, columnspan=5, sticky="EW",pady=(0,25))
exit = Button(mainwin, text="Stop", command=exitt)
exit.grid(row=6, column=25, columnspan=3, sticky="EW",pady=(0,25))
exit.configure(state='disabled')
mainwin.protocol("WM_DELETE_WINDOW", on_closing)
mainwin.mainloop()
