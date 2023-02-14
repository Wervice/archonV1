import re
from datetime import datetime
import os
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
def is_unc_path(path):
    unc_path = re.compile(r"^\\\\[\w\.]+\\.+")
    return bool(unc_path.match(path))
def get_file_extension(file_path):
    file_extension = os.path.splitext(file_path)[1].replace(".","")
    return file_extension

def push(status, file, to, folder=False):
    if is_unc_path(to):
        note = to + " is a network resource. You should unmount it after backup."
    else:
        note = to + " seemes to be a local path. If it's a removable drive, make sure it's disconected from your PC after backup."
    icon = "mimeicons/mimeicon_"+get_file_extension(file)+".svg"
    open("assets/backup_list.html", "a").write("<tr><td>"+file+" to "+to+"</td><td>"+status.replace("success", "<span class=green>Success</span>").replace("fail_copyisfalse", "<span class=red>Copy is not correct</span>").replace("fail_filenotfound", "<span class=red>File Not Found</span>")+"</td><td>"+dt_string+"</td></tr>")
    open("assets/backup_list.csv", "a").write("\n"+file+" -> "+to+";"+status+";"+dt_string+";;")
    if folder:
        icon = "mimeicons/folder.svg"
    open("assets\\index.html", "w").write(open("assets\\template.html").read().replace("$status", status.replace("success", "<span class=green>Success</span>").replace("fail_copyisfalse", "<span class=red>Copy is not correct</span>").replace("fail_filenotfound", "<span class=red>File Not Found</span>")).replace("$file", str(file) + " to " + to).replace("$time", dt_string).replace("$note", note).replace("$icon", icon).replace("$backup_list", open("assets/backup_list.html", "r").read()))
def show():
    import os
    os.system("start assets\\index.html")