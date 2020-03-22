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

Label(mainwin, text="Your Solution").grid(row=1, column=0,columnspan=15)
Label(mainwin, text="Solution to hack").grid(row=1, column=16,columnspan=15)

source = ScrolledText(mainwin, height=10, width=60)
source.grid(row=2, column=0,padx=20, pady=(0,50),columnspan=15)
compare = ScrolledText(mainwin, height=10, width=60)
compare.grid(row=2, column=16,padx=20, pady=(0,50),columnspan=15)
Label(mainwin, text="Test Case Generator").grid(row=3, column=0,columnspan=15)
generator = ScrolledText(mainwin, height=10, width=60)
generator.grid(row=4, rowspan=2,column=0,padx=20, pady=(0,50),columnspan=15)
Label(mainwin, text="Number of Threads: ").grid(row=4, column=17,columnspan=5)
spin = Spinbox(mainwin, from_= 1, to = 16)
spin.grid(row=4,column = 22)
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
    exit.configure(state='disabled')
    source.configure(state='normal')
    execute.configure(state='normal')
    spin.configure(state='normal')
    compare.configure(state='normal')
    generator.configure(state='normal')
    continue_executing = True
    test_num=1
    sys.exit()


def exit():
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
        continue_executing=False
        return False
    return True


def run(pp):
    global continue_executing, available
    available.acquire()
    p = sub.Popen('g++ usable/source.cpp -o usable/source'+pp,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    errors = errors.decode('ASCII')
    if(errors!=""):
        continue_executing = False
        printf("Source Compilation Error!\nExiting..")
        return
    p = sub.Popen('g++ usable/compare.cpp -o usable/compare'+pp,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    errors = errors.decode('ASCII')
    if(errors!=""):
        printf("Solution to Hack Compilation Error!\nExiting..")
        continue_executing = False
        return
    rewrite("usable/generator"+pp+".py",generator.get(1.0, END))
    available.release()

    # p = sub.Popen('python generator.py',stdout=sub.PIPE,stderr=sub.PIPE)
    # output, errors = p.communicate()
    # output = output.decode('ASCII')
    # errors = errors.decode('ASCII')
    # if(errors!=""):
    #     print(errors)
    #     print("Generator Error!\nExiting..")
    #     return

    while(continue_executing):
        generate=execut('generator'+pp,"","Python")
        if(generate[1]!=""):
            print("Generator Error!\n"+generate[1]+"\nExiting..")
            return
        result = compares(generate[0],pp)
        if(result):
            passed()
        else:
            return
    # print(output,errors,output=='')


def printer():
    global source, compare, generator, execute, spin, tex, workers, exit
    tex = Text(mainwin,height=10, width=120)
    tex.grid(row=6,padx=20,pady=(0,20), column=0,columnspan=30)
    rewrite("usable/source.cpp",source.get(1.0, END))
    rewrite("usable/compare.cpp",compare.get(1.0, END))

    tex.configure(state='disabled')
    exit.configure(state='normal')
    source.configure(state='disabled')
    execute.configure(state='disabled')
    spin.configure(state='disabled')
    compare.configure(state='disabled')
    generator.configure(state='disabled')
    
    for i in range(int(spin.get())):
        p = threading.Thread(target=run, args=(str(i)),name=str(i))
        p.start()
        workers.append(p)
        printf("Started Thread: "+str(i+1))
    return


execute = Button(mainwin, text="Execute", command=printer)
execute.grid(row=5, column=18, columnspan=5, sticky="EW",pady=(0,25))
exit = Button(mainwin, text="Stop", command=exit)
exit.grid(row=5, column=25, columnspan=3, sticky="EW",pady=(0,25))
exit.configure(state='disabled')
mainwin.protocol("WM_DELETE_WINDOW", on_closing)
mainwin.mainloop()
