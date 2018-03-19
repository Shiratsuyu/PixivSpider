import os
import tkinter as tk
import tkinter.font as tkfont
from random import sample

from PIL import ImageTk

from gui_decorator import decorator_thread
from gui_func import resize_img
from setting import img_list, img_file_path
from main_logic import button_of_get_a_picture

root = tk.Tk()

ft = tkfont.Font(family='Times', size=12, )  # weight=tkFont.BOLD

painterid_var = tk.StringVar()
picture_var = tk.StringVar()
username_var = tk.StringVar()
passwd_var = tk.StringVar()
status_var = tk.StringVar()
work_message_var = tk.StringVar()
painter_info_var = tk.StringVar()
img_var = tk.StringVar(value=img_list)

img_path_var = tk.StringVar()

work_message_var.set('Please wait......')
painter_info_var.set('Please wait......')


# def get_info():
#     def get_img(usr, passwd, status, pter_id):
#         print(usr, passwd, status, pter_id)
#         demo = Pixiv()
#         if demo.login(usr, passwd):
#             demo.get_work_of_painter(pter_id)
#             status.set('Success...')
#         else:
#             status.set('Error...')
#
#     thread_item = threading.Thread(target=get_img,
#                                    args=(username_var.get(), passwd_var.get(), status_var, painterid_var.get()))
#     thread_item.setDaemon(True)
#     thread_item.start()


# def all_works_func():
#     def inner(usr, passwd, status, pter_id):
#         status.set('运行中...')
#         try:
#             sign = button_of_get_a_picture(usr, passwd, pter_id)
#         except Exception:
#             status.set('运行失败...')  # 这个地方说不定也可以改成装饰器。
#             raise
#         else:
#             if sign:
#                 status.set('运行完成...')
#             else:
#                 status.set('运行失败...登录失败...')
#
#     thread_item = threading.Thread(target=inner,  # 这个地方可以改成带参数的装饰器。
#                                    args=(username_var.get(), passwd_var.get(), status_var, painterid_var.get()))
#     thread_item.setDaemon(True)
#     thread_item.start()


def get_a_picture_button():
    def inner_button(picture_id, status, usr, password):  # 放入线程中的函数
        status.set('运行中...')
        try:
            save_path, picture_info = button_of_get_a_picture(picture_id, account=usr, password=password)
        except Exception:
            status.set('运行失败...')
            raise
        else:
            status.set('运行完成...')
            work_message_var.set(str(picture_info))
            change_logo_from_button(save_path)

    @decorator_thread(func_name=inner_button)
    def inner(picture_id, status, usr, password):  # Only to pass parameters
        pass

    inner(picture_id=picture_var.get(), status=status_var, usr=username_var.get(), password=passwd_var.get())


def change_logo(event):
    global logo, logo_lbl
    logo_lbl.destroy()
    picture_file_path = os.path.join(img_file_path, img_list[img_lbox.curselection()[0]])
    logo = ImageTk.PhotoImage(resize_img(file_name=picture_file_path, width=600, height=800))
    logo_lbl = tk.Label(frame, image=logo, width=600, height=800)
    logo_lbl.grid(column=10, row=0, columnspan=20, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))
    print(img_lbox.curselection()[0])  # 第几项
    # work_message_var.set('当前图片编号为{}'.format(img_lbox.curselection()[0]))


def change_logo_from_button(img_path):
    global logo, logo_lbl
    # logo_lbl.destroy()  # 虽然不知道原理，但是不注释的话，会在替换的一刻，出现图片消失的情况
    logo = ImageTk.PhotoImage(resize_img(file_name=img_path, width=600, height=800))
    logo_lbl = tk.Label(frame, image=logo, width=600, height=800)
    logo_lbl.grid(column=10, row=0, columnspan=20, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))


root.title('Pixiv_spider')
content = tk.Frame(root, padx=3, pady=3)
frame = tk.Frame(content, borderwidth=5, relief='sunken')
option_frame = tk.Frame(content)
work_message_frame = tk.Frame(option_frame, borderwidth=5, relief='sunken')
painter_info_frame = tk.Frame(option_frame, borderwidth=5, relief='sunken')
list_frame = tk.Frame(frame)

img_lbox = tk.Listbox(list_frame, listvariable=img_var, height=10)
logo = ImageTk.PhotoImage(resize_img(file_name=os.path.join(img_file_path, sample(img_list, 1)[0]), width=600, height=800))
logo_lbl = tk.Label(frame, image=logo, width=600, height=800)  # 固定图片窗体大小
img_lbox.bind('<Double-1>', change_logo)

# 右边框
idlbl = tk.Label(option_frame, text='painter_id')
id = tk.Entry(option_frame, textvariable=painterid_var)
pic_idlbl = tk.Label(option_frame, text='picture_id')
pic_id = tk.Entry(option_frame, textvariable=picture_var)

usernamelbl = tk.Label(option_frame, text='pixiv username')
username = tk.Entry(option_frame, textvariable=username_var)
passwordlbl = tk.Label(option_frame, text='password')
password = tk.Entry(option_frame, textvariable=passwd_var, show='*')
work_message_bar = tk.Message(work_message_frame, textvariable=work_message_var, font=ft)  # 巨丑！！！！
status_lbl = tk.Label(option_frame, textvariable=status_var)

ok_button = tk.Button(option_frame, text='Okay', command=lambda: None)
get_an_work_button = tk.Button(option_frame, text='start', command=get_a_picture_button)
quit_button = tk.Button(option_frame, text='quit!', command=root.destroy)

painter_info_widget = tk.Message(painter_info_frame, textvariable=painter_info_var, font=ft)


content.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
frame.grid(column=0, row=0, columnspan=30, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))
img_lbox.grid(column=0, row=0, columnspan=10, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))
list_frame.grid(column=0, row=0, columnspan=10, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))
logo_lbl.grid(column=10, row=0, columnspan=20, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))
option_frame.grid(column=30, row=0, columnspan=10, rowspan=60, sticky=(tk.N, tk.S, tk.W, tk.E))


idlbl.grid(columnspan=20, rowspan=5, sticky=(tk.N,), padx=5)
id.grid(columnspan=20, rowspan=5, sticky=(tk.N, tk.E, tk.W), padx=5)

usernamelbl.grid(columnspan=20, rowspan=5, sticky=(tk.N,), padx=5)
username.grid(columnspan=20, rowspan=5, sticky=(tk.N, tk.E, tk.W), padx=5)
passwordlbl.grid(columnspan=20, rowspan=5, sticky=(tk.N,), padx=5)
password.grid(columnspan=20, rowspan=5, sticky=(tk.N, tk.E, tk.W), padx=5)

status_lbl.grid(columnspan=20, rowspan=5, sticky=(tk.W, tk.S), padx=5)
work_message_frame.grid(column=0, row=35, columnspan=20, rowspan=10, sticky=(tk.W, tk.E))
work_message_bar.grid(sticky=(tk.N, tk.W))


ok_button.grid(column=0, row=45, columnspan=10, rowspan=5, sticky=(tk.W, tk.E))
quit_button.grid(column=10, row=45, columnspan=10, rowspan=5, sticky=(tk.W, tk.E))

pic_idlbl.grid(columnspan=20, rowspan=5, sticky=(tk.N,), padx=5)
pic_id.grid(columnspan=20, rowspan=5, sticky=(tk.N, tk.W, tk.E), padx=5)
get_an_work_button.grid(columnspan=20, rowspan=5, sticky=(tk.W, tk.E))

painter_info_frame.grid(column=0, row=65, columnspan=20, rowspan=10, sticky=(tk.W, tk.E))
painter_info_widget.grid(sticky=(tk.N, tk.W))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)  # good !!!
content.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)

# content.rowconfigure(10, weight=1)
# # content.rowconfigure(2, weight=1)
# # content.rowconfigure(3, weight=1)
# # content.rowconfigure(4, weight=1)
# content.rowconfigure(50, weight=1)
# content.columnconfigure(0, weight=5)
# content.columnconfigure(10, weight=5)
# content.columnconfigure(20, weight=5)  # weight 是不是指拉伸时候的比重
# content.columnconfigure(30, weight=1)
# content.columnconfigure(40, weight=1)

frame.columnconfigure(0, minsize=200, weight=1)
frame.rowconfigure(0, weight=1)
list_frame.columnconfigure(0, weight=1)  # 不写这个，listbox 扩不出来
list_frame.rowconfigure(0, weight=1)
work_message_frame.rowconfigure(0, weight=1, minsize=200)
work_message_frame.columnconfigure(0, weight=1)
painter_info_frame.rowconfigure(0, weight=1, minsize=200)
painter_info_frame.columnconfigure(0, weight=1)