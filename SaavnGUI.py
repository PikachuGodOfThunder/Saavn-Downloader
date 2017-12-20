
import sys

try:
    from Tkinter import *
except ImportError:
    from tkinter import *
from tkinter import messagebox
 

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1
from bs4 import BeautifulSoup
import os
import requests
from json import JSONDecoder
import base64

from pyDes import *
import urllib


proxy_ip = ''
# set http_proxy from environment
if('http_proxy' in os.environ):
    proxy_ip = os.environ['http_proxy']

proxies = {
  'http': proxy_ip,
  'https': proxy_ip,
}
# proxy setup end here

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
}
base_url = 'http://h.saavncdn.com'
json_decoder = JSONDecoder()

# Key and IV are coded in plaintext in the app when decompiled
# and its preety insecure to decrypt urls to the mp3 at the client side
# these operations should be performed at the server side.
des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0" , pad=None, padmode=PAD_PKCS5)

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root, top
    root = Tk()
    top = New_Toplevel_1 (root)
    root.mainloop()

w = None
listoflink=[]
listofname=[]
def hello(event):
    top.Text1.delete('1.0', END)
    query=top.Entry1.get().strip()
    if "www.saavn.com" in query:
        input_url=query
    else:
        input_url = "https://www.saavn.com/search/"+query
    print (input_url)
    try:
        res = requests.get(input_url, proxies=proxies, headers=headers)
    except Exception as e:
        print('Error accesssing website error: '+e)
        sys.exit()


    soup = BeautifulSoup(res.text,"lxml")

    # Encrypted url to the mp3 are stored in the webpage
    songs_json = soup.find_all('div',{'class':'hide song-json'});
    listoflink[:]=[]
    listofname[:]=[]
    count =1
    stringtobeappended=""
    for song in songs_json:
        try:
            print "Press "+str(count)+" to Download!!!"
            obj = json_decoder.decode(song.text)
            print(obj['album'],'-',obj['title'])
            print obj
            stringtobeappended=stringtobeappended+">>Song Number: "+str(count)+"<<\n"+obj['album']+'-'+obj['title']+'-'+obj['singers']
            enc_url = base64.b64decode(obj['url'].strip())
            dec_url = des_cipher.decrypt(enc_url,padmode=PAD_PKCS5).decode('utf-8')
            dec_url = base_url + dec_url.replace('mp3:audios','') + '.mp3'
            listofname.append(obj['title'])
            listoflink.append(dec_url)
            stringtobeappended=stringtobeappended+"\n"+dec_url+"\n--------------------------------------------------------\n"
            print(dec_url,'\n\n')
            print("--------------------------------------------------------")
            count=count+1
        except:
            pass
    top.Text1.insert(END,(stringtobeappended))    
    top.Entry2.focus_set();
    
def download(event):
    testfile = urllib.URLopener()
    stringValue=top.Entry2.get()
    if stringValue.upper()=="ALL":
        for i in range(len(listoflink)):
            testfile.retrieve(listoflink[i], listofname[i]+".mp3")
    else:
        temp=int(stringValue)-1
        testfile.retrieve(listoflink[temp], listofname[temp]+".mp3")
    # messagebox.showinfo("Alert", "Download Success")
def helloworld():
    change=1
    # print top.Label1.config(text=str(change))
    # top.Text1.insert(END,str(change))
    hello()

def callbackFunction(event):
    top.Entry2.focus_set();

class New_Toplevel_1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 

        top.geometry("632x516+325+117")
        top.title("Version 1.000")
        top.configure(background="#d9d9d9")



        self.menubar = Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)



        self.Entry1 = Entry(top)
        self.Entry1.place(relx=0.28, rely=0.04, relheight=0.04, relwidth=0.48)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.bind('<Return>', hello)
        self.Entry1.bind('<Control-d>', callbackFunction)
        self.Entry1.focus_set();

        self.Label1 = Label(top)
        self.Label1.place(relx=0.08, rely=0.04, height=21, width=106)
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''Enter Search Query''')

        self.Button1 = Button(top)
        self.Button1.place(relx=0.84, rely=0.03, height=24, width=47)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(command=helloworld)
        self.Button1.configure(text='''Search''')

        self.Text1 = Text(top)
        self.Text1.place(relx=0.09, rely=0.12, relheight=0.63, relwidth=0.81)
        self.Text1.configure(background="white")
        self.Text1.configure(font="TkTextFont")
        self.Text1.configure(foreground="black")
        self.Text1.configure(highlightbackground="#d9d9d9")
        self.Text1.configure(highlightcolor="black")
        self.Text1.configure(insertbackground="black")
        self.Text1.configure(selectbackground="#c4c4c4")
        self.Text1.configure(selectforeground="black")
        self.Text1.configure(width=514)
        self.Text1.configure(wrap=WORD)

        self.Label2 = Label(top)
        self.Label2.place(relx=0.09, rely=0.83, height=21, width=196)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''Enter Number to Download Song''')
        self.Label2.configure(width=196)

        self.Entry2 = Entry(top)
        self.Entry2.place(relx=0.43, rely=0.83, relheight=0.04, relwidth=0.18)
        self.Entry2.configure(background="white")
        self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="#c4c4c4")
        self.Entry2.configure(selectforeground="black")
        self.Entry2.configure(width=112)
        self.Entry2.bind('<Return>', download)

        self.Button2 = Button(top)
        self.Button2.place(relx=0.66, rely=0.83, height=24, width=67)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#d9d9d9")
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''Download''')
        self.Button2.configure(command=download)
        self.Button2.configure(width=67)






if __name__ == '__main__':
    vp_start_gui()


