import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.messagebox as msgbox
import PyPDF2
import os
import time
import subprocess
import platform


def add_file():
    """find files and attach to list"""
    files = filedialog.askopenfilenames(title="pdf 파일을 선택하세요", filetypes=(("pdf 파일", "*.pdf"), ("모든 파일", "*.*")),
                                        initialdir=r"")

    for file in sorted(files):
        list_file.insert(tk.END, file)


def del_file():
    """delete file from list"""
    if len(list_file.curselection()) == 0:
        msgbox.showwarning("경고", "삭제할 pdf 파일을 선택해주세요!")
        return
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


def toggle_enrty_password():
    """toggle password entries"""
    if chkvar_encrypt.get() == 0:
        entry_password.configure(state='disabled')
        entry_password_confirm.configure(state='disabled')
    else:
        entry_password.configure(state='normal')
        entry_password_confirm.configure(state='normal')


def decorator_exception(f):
    """exception wrapper"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            msgbox.showerror("오류", e)
            p_var.set(0)
            progress_bar.update()
    return wrapper


def decorator_validation(f):
    """validation wrapper"""
    def wrapper(*args, **kwargs):
        if list_file.size() == 0:
            msgbox.showwarning("경고", "pdf 파일을 추가해주세요!")
            return

        if len(entry_dest_path.get()) == 0:
            msgbox.showwarning("경고", "저장 경로를 선택하세요!")
            return

        if chkvar_encrypt.get() == 1:
            if not entry_password.get() or not entry_password_confirm.get():
                msgbox.showwarning("경고", "암호를 입력해주세요.")
                return
            if entry_password.get() != entry_password_confirm.get():
                msgbox.showwarning("경고", "암호가 일치하지 않습니다.")
                return
        return f(*args, **kwargs)
    return wrapper


def decorator_success_msg(f):
    """success msg wrapper"""
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = f(*args, **kwargs)
        except Exception as e:
            raise e
        else:
            msgbox.showinfo("알림", "작업이 완료되었습니다!")
            if chkvar_open_result.get() == 1:
                dest = entry_dest_path.get()
                _open_file(dest)
            return result
    return wrapper


def decorator_init_progress(f):
    def wrapper(*args, **kwargs):
        p_var.set(0)
        progress_bar.update()
        return f(*args, **kwargs)
    return wrapper


def _open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _rotated_pdf(filepath, angle, dest):
    filename = os.path.basename(filepath)
    name_without_ext, ext = os.path.splitext(filename)
    rotated_file_name = _get_output_filename(dest, name_without_ext, ext)

    with open(filepath, 'rb') as original_file:
        pdfReader = PyPDF2.PdfFileReader(original_file, strict=False)
        pdfWriter = PyPDF2.PdfFileWriter()
        page_length = pdfReader.getNumPages()
        for i in range(pdfReader.getNumPages()):
            page = pdfReader.getPage(i)
            page.rotateClockwise(int(angle))
            pdfWriter.addPage(page)
        with open(rotated_file_name, 'wb') as result_file:
            if chkvar_encrypt.get() == 1:
                pdfWriter.encrypt(entry_password.get())
            pdfWriter.write(result_file)


def _encrypt_pdf(filepath, dest):
    filename = os.path.basename(filepath)
    name_without_ext, ext = os.path.splitext(filename)
    encrypted_file_name = _get_output_filename(
        dest, name_without_ext + '_encrypted', ext)

    with open(filepath, 'rb') as original_file:
        pdfReader = PyPDF2.PdfFileReader(original_file, strict=False)
        pdfWriter = PyPDF2.PdfFileWriter()
        page_length = pdfReader.getNumPages()
        for i in range(page_length):
            page = pdfReader.getPage(i)
            pdfWriter.addPage(page)
        with open(encrypted_file_name, 'wb') as result_file:
            pdfWriter.encrypt(entry_password.get())
            pdfWriter.write(result_file)


@decorator_init_progress
@decorator_exception
@decorator_success_msg
def _rotate_pdf_files(pdf_files, angle, dest):
    for idx, pdf_file in enumerate(pdf_files):
        _rotated_pdf(pdf_file, angle, dest)
        progress = (idx + 1) / len(pdf_files) * 100
        p_var.set(progress)
        progress_bar.update()


@decorator_init_progress
@decorator_exception
@decorator_success_msg
def _merge_pdf_files(pdf_files, dest):
    merger = PyPDF2.PdfFileMerger()
    try:
        for idx, pdf_file in enumerate(pdf_files):
            with open(pdf_file, 'rb') as f:
                merger.append(PyPDF2.PdfFileReader(f, strict=False))
            progress = (idx + 1) / len(pdf_files) * 100
            p_var.set(progress)
            progress_bar.update()
        merged_pdf_filename = _get_output_filename(dest, "merged")
        merger.write(merged_pdf_filename)
        if chkvar_encrypt.get() == 1:
            encrypted_pdf = PyPDF2.PdfFileWriter()
            encrypt_pdf_filename = _get_output_filename(dest, "encrypt")
            with open(merged_pdf_filename, 'rb') as f:
                merged_pdf = PyPDF2.PdfFileReader(f)
                for i in range(merged_pdf.getNumPages()):
                    encrypted_pdf.addPage(merged_pdf.getPage(i))
                with open(encrypt_pdf_filename, 'wb') as f:
                    encrypted_pdf.encrypt(entry_password.get())
                    encrypted_pdf.write(f)
            os.remove(merged_pdf_filename)
            os.rename(encrypt_pdf_filename, merged_pdf_filename)

    finally:
        if merger is not None:
            merger.close()


@decorator_init_progress
@decorator_exception
@decorator_success_msg
def _encrypt_files(pdf_files, dest):
    for idx, pdf_file in enumerate(pdf_files):
        _encrypt_pdf(pdf_file, dest)
        progress = (idx + 1) / len(pdf_files) * 100
        p_var.set(progress)
        progress_bar.update()


def _get_output_filename(dest, name_without_ext, ext=".pdf"):
    cur_time = time.strftime("_%Y%m%d_%H%M%S")
    filename = os.path.join(dest, ''.join((name_without_ext, cur_time, ext)))
    return filename


@decorator_validation
def rotate_file():
    """rotate"""
    angle = cmb_rotate.get()
    dest = entry_dest_path.get()
    pdf_files = list_file.get(0, tk.END)
    _rotate_pdf_files(pdf_files, angle, dest)


@decorator_validation
def merge_file():
    """merge pdf file"""
    if list_file.size() < 2:
        msgbox.showwarning("경고", "pdf 파일을 2개 이상 추가해주세요!")
        return
    dest = entry_dest_path.get()
    pdf_files = list_file.get(0, tk.END)
    _merge_pdf_files(pdf_files, dest)


@decorator_validation
def encrypt_file():
    """encrypt pdf file """
    if chkvar_encrypt.get() == 0:
        msgbox.showwarning("경고", "암호 설정 부분을 체크해 주세요!")
        return
    dest = entry_dest_path.get()
    pdf_files = list_file.get(0, tk.END)
    _encrypt_files(pdf_files, dest)


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

list_file = tk.Listbox(frame_list, selectmode="extended",
                       height=15, yscrollcommand=scrollbar.set)
list_file.pack(side="left", fill="both", expand=True)
scrollbar.config(command=list_file.yview)

# 저장 경로
frame_path = tk.LabelFrame(root, text="저장경로")
frame_path.pack(fill="x", padx=5, pady=5, ipady=5)

entry_dest_path = tk.Entry(frame_path, state='disabled')
entry_dest_path.pack(side="left", fill="x", expand=True,
                     padx=5, pady=5, ipady=4)

btn_dest_path = tk.Button(frame_path, text="찾아보기",
                          width=10, command=browse_dest_path)
btn_dest_path.pack(side="right", padx=5, pady=5)

# 옵션
frame_option = tk.LabelFrame(root, text="옵션")
frame_option.pack(fill="both", padx=5, pady=5, ipady=5)

lbl_rotate = tk.Label(frame_option, text="회전", width=8)
lbl_rotate.grid(row=0, column=0, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

opt_rotate = ("90", "180", "270")
cmb_rotate = ttk.Combobox(
    frame_option, state="readonly", values=opt_rotate, width=5)
cmb_rotate.current(1)
cmb_rotate.grid(row=0, column=1, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

chkvar_open_result = tk.IntVar(value=1)
cb_open_result = tk.Checkbutton(
    frame_option, text="완료 후 폴더 열기", variable=chkvar_open_result)
cb_open_result.grid(row=1, column=0, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

chkvar_encrypt = tk.IntVar()
cb_encrypt = tk.Checkbutton(frame_option, text="암호 설정",
                            variable=chkvar_encrypt, command=toggle_enrty_password)
cb_encrypt.grid(row=2, column=0, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

entry_password = tk.Entry(frame_option, show="*", state='disabled')
entry_password.grid(row=2, column=1, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

lbl_password_confirm = tk.Label(frame_option, text="암호 확인", width=8)
lbl_password_confirm.grid(
    row=2, column=2, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

entry_password_confirm = tk.Entry(frame_option, show="*", state='disabled')
entry_password_confirm.grid(
    row=2, column=3, sticky=tk.N+tk.W+tk.S, padx=3, pady=3)

# 진행 상황
frame_progress = tk.LabelFrame(root, text="진행상황")
frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

p_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
progress_bar.pack(fill="x", padx=5, pady=5)

# 실행
frame_run = tk.Frame(root)
frame_run.pack(fill="x", padx=5, pady=5)

btn_start_rotate = tk.Button(frame_run, padx=5, pady=5,
                             text="회전", width=8, command=rotate_file)
btn_start_rotate.pack(side="left", padx=5, pady=5)

btn_start_merge = tk.Button(frame_run, padx=5, pady=5,
                            text="합치기", width=8, command=merge_file)
btn_start_merge.pack(side="left", padx=5, pady=5)

btn_start_encrypt = tk.Button(frame_run, padx=5, pady=5,
                              text="암호걸기", width=8, command=encrypt_file)
btn_start_encrypt.pack(side="left", padx=5, pady=5)

root.resizable(False, False)
root.mainloop()
