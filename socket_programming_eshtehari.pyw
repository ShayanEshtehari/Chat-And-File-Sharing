# pip install ipaddress==1.0.23
# pip install netifaces==0.11.0
import socket
import os
import sys
import netifaces as ni
import ipaddress
import threading
import tkinter as tk
from tkinter import filedialog as tkfiledialog
from tkinter import messagebox as tkmessagebox
from multiprocessing import Queue


BUFSIZE = 65535
PORT = 50005
PRIVATE_NETWORK = ['192.168.1.0/24',
                   '192.168.0.0/16', '172.16.0.0/12', '10.0.0.0/8']
FT_PORT = 50006
BUFFER_SIZE = 4096
SEPARATOR = "<جداکننده>"
INTERFACE_ADDRESSES = [ni.ifaddresses(
    x)[ni.AF_INET][0] for x in ni.interfaces() if ni.AF_INET in ni.ifaddresses(x)]


def resource_path(relative_path=None):
    if hasattr(sys, '_MEIPASS') and relative_path != None:
        return os.path.join(sys._MEIPASS, relative_path)
    elif hasattr(sys, '_MEIPASS') and relative_path == None:
        return os.path.join(sys._MEIPASS)
    elif relative_path != None:
        return os.path.join(os.path.abspath(os.path.split(os.path.realpath(__file__))[0]), relative_path)
    return os.path.join(os.path.abspath(os.path.split(os.path.realpath(__file__))[0]))


def ft_server_listen(host='0.0.0.0', port=FT_PORT, q=None, label=None, listen_btn=None, recv_btn=None):
    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    client_socket, address = s.accept()

    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    if q:
        q.put((s, client_socket, filesize, filename))
    if label:
        label.set('سایز فایل: ' + str(filesize) +
                  '\n' + 'نام فایل: \n' + str(filename))
    if recv_btn:
        recv_btn['command'] = lambda arg=(
            listen_btn, recv_btn, label, s, client_socket, filesize, filename): tk_parallelcmd_recv(*arg)
    if recv_btn:
        recv_btn['state'] = tk.NORMAL
    return (s, client_socket, filesize, filename)


def ft_server_recv(s, client_socket, filesize, filename, full_path):
    with open(full_path, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)

    client_socket.close()
    s.close()
    tkmessagebox.showinfo(title="اتمام دریافت", message="فایل دریافت شد")


def ft_client(host, port, filename):
    filesize = os.path.getsize(filename)

    s = socket.socket()

    s.connect((host, port))

    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
    s.close()


def server_listen(msgbox, interface='', port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((interface, port))
    while True:
        data, address = s.recvfrom(BUFSIZE)
        text = data.decode('utf8')
        l = msgbox.get()
        l = l + '\n' + address[0] + ': ' + text
        msgbox.set(l)


def udp_send(text, network, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(text.encode('utf8'), (network, port))


def is_local_communication(ipaddr, i):
    s = False
    s = s or ipaddress.ip_address(
        ipaddr) in ipaddress.ip_network(PRIVATE_NETWORK[i])
    return s


def become_server(q=None):
    for i in INTERFACE_ADDRESSES:
        if is_local_communication(i['addr'], 0):
            response = (i['addr'], i['broadcast'])
            if q:
                q.put(response)
            return response
    for i in INTERFACE_ADDRESSES:
        if is_local_communication(i['addr'], 1):
            response = (i['addr'], i['broadcast'])
            if q:
                q.put(response)
            return response
    for i in INTERFACE_ADDRESSES:
        if is_local_communication(i['addr'], 2):
            response = (i['addr'], i['broadcast'])
            if q:
                q.put(response)
            return response
    for i in INTERFACE_ADDRESSES:
        if is_local_communication(i['addr'], 3):
            response = (i['addr'], i['broadcast'])
            if q:
                q.put(response)
            return response
    raise Exception('No intrefaces found!')


## -- user interface -- ##


def tk_on_closing(root):
    if tkmessagebox.askyesno("خروج", "خارج می‌شوید؟"):
        root.destroy()
        sys.exit()


def tk_choose_file(label=None, btn=None):
    try:
        path = tkfiledialog.askopenfilename(initialdir=os.path.split(
            resource_path())[0], title="Select A File",)
        if label:
            label.set(path)
        if path == "":
            if btn:
                btn['state'] = tk.DISABLED
            if label:
                label.set("فایلی انتخاب نشد")
        else:
            if btn:
                btn['state'] = tk.NORMAL
    except:
        path = ""
        if label:
            label.set("فایل پیدا نشد")
        if btn:
            btn['state'] = tk.DISABLED
    finally:
        return path


def tk_save_file(label=None, btn=None, initialfile='', extension=''):
    try:
        path = tkfiledialog.asksaveasfilename(initialdir=os.path.split(resource_path())[0], initialfile=initialfile, title="Save As File", filetypes=(
            ("text file", ".txt"), ("video file", "*.mp4"), ("all files", "*.*")), defaultextension=extension)
        if label:
            label.set(path)
        if path == "":
            if btn:
                btn['state'] = tk.DISABLED
            if label:
                label.set("فایلی انتخاب نشد")
        else:
            if btn:
                btn['state'] = tk.NORMAL
    except:
        path = ""
        if label:
            label.set("لغو شد")
        if btn:
            btn['state'] = tk.DISABLED
    finally:
        return path


def tk_make_Label2(root, text='Label text', wraplength=200, justify=tk.CENTER, row=0, col=0, colspan=2, sticky=tk.W+tk.W, padx=10, pady=10):
    var = tk.StringVar()
    var.set(text)
    tk.Label(root, textvariable=var, wraplength=wraplength, justify=justify).grid(
        row=row, column=col, columnspan=colspan, sticky=sticky, padx=padx, pady=pady)
    return var


def tk_make_Entry(root, row=0, col=0, colspan=2, width=200, sticky=tk.W, padx=10, pady=10):
    var = tk.StringVar()
    tk.Entry(root, width=width, textvariable=var).grid(
        row=row, column=col, columnspan=colspan, sticky=sticky, padx=padx, pady=pady)
    return var


def tk_make_Button(root, cmd=None, text='Btn text', width=30, row=0, col=0, colspan=2, sticky=tk.W+tk.W, padx=10, pady=10, state=tk.NORMAL):
    btn = tk.Button(root, text=text, command=cmd, width=width, state=state)
    btn.grid(row=row, column=col, columnspan=colspan,
             sticky=sticky, padx=padx, pady=pady)
    return btn


def tk_make_childWindow(root, geo="240x250", title="Child Window"):
    def tk_child_on_closing(cw):
        cw.withdraw()
    cw = tk.Toplevel(root)
    cw.geometry(geo)
    cw.title(title)
    cw.protocol("WM_DELETE_WINDOW", lambda arg=window: tk_child_on_closing(cw))
    return cw


def tk_parallelcmd_sendmsg(msg, event=None):
    text = msg.get()
    msg.set('')
    q1 = Queue()
    p1 = threading.Thread(target=become_server, args=(q1,))
    p1.start()
    p1.join()
    p2 = threading.Thread(target=udp_send, args=(text, q1.get()[1]))
    p2.start()


def tk_parallelcmd_joinroom(btn_join, btn_send, room):
    btn_join['state'] = tk.DISABLED
    btn_send['state'] = tk.NORMAL
    p1 = threading.Thread(target=server_listen, args=(room, '0.0.0.0', PORT))
    p1.daemon = True
    p1.start()


def tk_parallelcmd_listen(listen_btn, recv_btn, label):
    listen_btn['state'] = tk.DISABLED
    q1 = Queue()
    p1 = threading.Thread(target=become_server, args=(q1,))
    p1.start()
    p1.join()
    host = q1.get()[0]
    p2 = threading.Thread(target=ft_server_listen, args=(
        host, FT_PORT,), kwargs={'label': label, 'listen_btn': listen_btn, 'recv_btn': recv_btn})
    p2.start()


def tk_parallelcmd_recv(listen_btn, recv_btn, label, s, client_socket, file_size, file_name):
    recv_btn['state'] = tk.DISABLED
    file_extension = os.path.splitext(file_name)[1]
    full_path = tk_save_file(
        label=label, initialfile=file_name, extension=file_extension)
    p1 = threading.Thread(target=ft_server_recv, args=(
        s, client_socket, file_size, file_name, full_path))
    p1.start()
    listen_btn['state'] = tk.NORMAL


def tk_parallelcmd_connect(ipaddr_box, label):
    ipaddr = ipaddr_box.get().strip()
    try:
        ipaddress.IPv4Address(ipaddr)
    except ipaddress.AddressValueError:
        tkmessagebox.showerror(
            title="خطا", message="مقدار وارد شده یک آی‌پی ورژن ۴ صحیح نمی‌باشد")
        return

    file_path = tk_choose_file(label=label)
    p1 = threading.Thread(target=ft_client, args=(ipaddr, FT_PORT, file_path,))
    p1.start()


def tk_cmd_cw_reappear(cw):
    cw.deiconify()


def tk_cmd_cw(root, geo, title, this_btn):
    child_window = tk_make_childWindow(root, geo=geo, title=title)

    this_btn['command'] = lambda arg=child_window: tk_cmd_cw_reappear(arg)

    this_btn['state'] = tk.NORMAL

    tkvar_serverListenBtn = tk_make_Button(child_window, lambda arg=(): tk_parallelcmd_listen(*arg), text='شنیدن', width=15,
                                           row=0, col=1, colspan=1, sticky=tk.E, padx=5, pady=10, state=tk.NORMAL)

    tkvar_serverRecvBtn = tk_make_Button(child_window, lambda arg=(): tk_parallelcmd_recv(*arg), text='دریافت فایل', width=15,
                                         row=0, col=0, colspan=1, sticky=tk.W, padx=5, pady=10, state=tk.DISABLED)

    tkvar_stateLabel = tk_make_Label2(child_window, text='', wraplength=200,
                                      justify=tk.CENTER, row=3, col=0, colspan=2, sticky=tk.W+tk.E, padx=10, pady=10)

    tkvar_serverListenBtn['command'] = lambda arg=(
        tkvar_serverListenBtn, tkvar_serverRecvBtn, tkvar_stateLabel): tk_parallelcmd_listen(*arg)

    tkvar_serverRecvBtn['command'] = lambda arg=(
        tkvar_serverListenBtn, tkvar_serverRecvBtn): tk_parallelcmd_recv(*arg)

    tkvar_addr = tk_make_Entry(
        child_window, row=1, col=0, colspan=2, width=30, sticky=tk.W+tk.E, padx=10, pady=10)

    tk_make_Button(child_window, lambda arg=(tkvar_addr, tkvar_stateLabel): tk_parallelcmd_connect(
        *arg), text='انتخاب فایل و ارسال', width=30, row=2, col=0, colspan=2, sticky=tk.W+tk.W, padx=10, pady=10, state=tk.NORMAL)


if __name__ == '__main__':

    window = tk.Tk()
    window.geometry("240x500")
    window.title("سوکت پروگرمینگ")
    window.configure(bg="azure")
    window.protocol("WM_DELETE_WINDOW", lambda arg=window: tk_on_closing(arg))

    tkvar_ftbtn = tk_make_Button(window, lambda arg=(window, '250x250', 'اشتراک فایل'): tk_cmd_cw(*arg), text='اشتراک فایل', width=30,
                                 row=3, col=0, colspan=2, sticky=tk.W+tk.W, padx=10, pady=10, state=tk.NORMAL)

    tkvar_ftbtn['command'] = lambda arg=(
        window, '250x250', 'اشتراک فایل', tkvar_ftbtn): tk_cmd_cw(*arg)

    tkvar_chatroom = tk_make_Label2(window, text='چت روم', wraplength=200,
                                    justify=tk.CENTER, row=30, col=0, colspan=2, sticky=tk.W+tk.E, padx=10, pady=10)

    tkvar_joinroom = tk_make_Button(window, text='پیوستن به چت روم', width=30,
                                    row=4, col=0, colspan=2, sticky=tk.W+tk.W, padx=10, pady=10, state=tk.NORMAL)

    tkvar_msgbox = tk_make_Entry(
        window, row=5, col=0, colspan=2, width=30, sticky=tk.W+tk.E, padx=10, pady=10)

    tkvar_sendbtn = tk_make_Button(window, lambda kwargs={'msg': tkvar_msgbox}: tk_parallelcmd_sendmsg(**kwargs), text='ارسال', width=30,
                                   row=6, col=0, colspan=2, sticky=tk.W+tk.W, padx=10, pady=10, state=tk.DISABLED)

    window.bind("<Return>", lambda event: tk_parallelcmd_sendmsg(
        event=event, msg=tkvar_msgbox))

    tkvar_joinroom['command'] = lambda arg=(
        tkvar_joinroom, tkvar_sendbtn, tkvar_chatroom): tk_parallelcmd_joinroom(*arg)

    window.mainloop()
