import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

def add_file():
    """find files and attach to list"""
    files = filedialog.askopenfilenames(title="pdf 파일을 선택하세요", filetypes=(("pdf 파일", "*.pdf"), ("모든 파일", "*.*")),
    initialdir=r"")

    for file in files:
        list_file.insert(tk.END, file)

def del_file():
    """delete file from list"""
    for index in reversed(list_file.curselection()):
        list_file.delete(index)

def browse_dest_path():
    """set location for rotated pdf files"""
    folder_selected = filedialog.askdirectory()
    if folder_selected == '':
        return
    entry_dest_path.configure(state='normal')
    entry_dest_path.delete(0, tk.END)
    entry_dest_path.insert(0, folder_selected)
    entry_dest_path.configure(state='disabled')


def start():
    pass

root = tk.Tk()
root.title("pdf util")

# 파일 선택, 삭제
frame_file = tk.Frame(root)
frame_file.pack(fill='x', padx=5, pady=5)  # 간격 띄우기

btn_add_file = tk.Button(frame_file, padx=5, pady=5,
                      width=12, text="파일추가", command=add_file)
btn_add_file.pack(side="left")

btn_del_file = tk.Button(frame_file, padx=5, pady=5,
                      width=12, text="선택삭제", command=del_file)
btn_del_file.pack(side="right")

# 파일 리스트
frame_list = tk.Frame(root)
frame_list.pack(fill="both", padx=5, pady=5)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side="right", fill="y")

list_file = tk.Listbox(frame_list, selectmode="extended", height=15, yscrollcommand=scrollbar.set)
list_file.pack(side="left", fill="both", expand=True)
scrollbar.config(command=list_file.yview)

# 저장 경로
frame_path = tk.LabelFrame(root, text="저장경로")
frame_path.pack(fill="x", padx=5, pady=5, ipady=5)

entry_dest_path = tk.Entry(frame_path, state='disabled')
entry_dest_path.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4)

btn_dest_path = tk.Button(frame_path, text="찾아보기", width=10, command=browse_dest_path)
btn_dest_path.pack(side="right", padx=5, pady=5)

# 옵션
frame_option = tk.LabelFrame(root, text="옵션")
frame_option.pack(fill="both", padx=5, pady=5, ipady=5)

lbl_rotate = tk.Label(frame_option, text="회전", width=8)
lbl_rotate.pack(side="left", padx=5, pady=5)

opt_rotate = ("90", "180", "270")
cmb_rotate = ttk.Combobox(frame_option, state="readonly", values=opt_rotate, width=5)
cmb_rotate.current(0)
cmb_rotate.pack(side="left", padx=5, pady=5)

# 진행 상황
frame_progress = tk.LabelFrame(root, text="진행상황")
frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

p_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
progress_bar.pack(fill="x", padx=5, pady=5)

# 실행
frame_run = tk.Frame(root)
frame_run.pack(fill="x", padx=5, pady=5)

btn_start = tk.Button(frame_run, padx=5, pady=5, text="시작", width=12, command=start)
btn_start.pack(padx=5, pady=5)

# root.resizable(False, False)
root.mainloop()