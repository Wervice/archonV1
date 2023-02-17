import os
import sys
import shutil
import re
import ftplib
import random
import math
import pyAesCrypt
from libs import dashboard as dashboard
from termcolor import colored
from datetime import datetime
now = datetime.now()
# Date and time as a formatted string
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
def filedestroy(file):
    bi = 0
    while bi != 3:
        s = ""
        i = 0
        while i != os.stat(file).st_size:
            s = s+chr(random.randint(0, 100))
            i = i+1
        overwriter = open(file, "w")
        overwriter.write(s)
        overwriter.close()
        bi = bi+1
    os.remove(file)
def is_unc_path(path):
    unc_path = re.compile(r"^\\\\[\w\.]+\\.+")
    return bool(unc_path.match(path))
try:
    if len(sys.argv) == 1:
        # Writes the breefing
        breefing_f = open(".\\assets\\breefing.txt", "r")
        print(breefing_f.read())
        breefing_f.close()
    else:
        if sys.argv[1] == "sbackup":
            # Backup a single file
            try:
                # Copies the file to the destination location
                dest_f = open(sys.argv[3], "wb")
                origin_f = open(sys.argv[2], "rb")
                dest_f.write(origin_f.read())
                dest_f.close()
                origin_f.close()
                # Shows the copy indicator
                print(colored("[-] Copy: " + sys.argv[2] + " => " + sys.argv[3], "blue"))
                # Check the copy
                origin_f_check = open(sys.argv[2], "rb")
                dest_f_check = open(sys.argv[3], "rb")
                if (origin_f_check.read() == dest_f_check.read()):
                    print(colored("[*] Backup file", "green"))
                    # Push to the dashboard
                    dashboard.push("success", sys.argv[2], sys.argv[3])
                    dashboard.show()
                else:
                    # Push to the dashboard if copy failed
                    dashboard.push("fail_copyisfalse",
                                   sys.argv[2], sys.argv[3])
                    dashboard.show()
                    # Print error message
                    print("The backup is not the same as the orginal.")
            except FileNotFoundError:
                dashboard.push("fail_filenotfound", sys.argv[2], sys.argv[3])
                dashboard.show()
                print(colored("File Not Found", "red"))
                origin_f_check.close()
                dest_f_check.close()
        elif sys.argv[1] == "fbackup":
            # Backup a folder and compress it as xztar file.
            encrypted = "Y" == input(colored("Do you want to make an encrypted archive? (Y/n) ", "blue"))
            if encrypted:
                password = input(colored("Password> ", "blue"))
                overwrite = "y" == input(colored("Do you want to overwrite the unencrypted version (y/N) ", "blue"))
            try:
                if is_unc_path(sys.argv[3]):
                    print(colored("[-] Backup folder to network location", "blue"))
                else:
                    print(colored("[-] Backup folder to local path", "blue"))
                foldername = os.path.dirname(sys.argv[2]).split(
                    "\\")[len(os.path.dirname(sys.argv[2]).split("\\"))-1]  # Get foldername
                print(colored("[-] Make compressed tar archive", "blue"))  # Print "Make the archive"
                # Write the metadata to the backupfolder
                metadata_f_writer = open(sys.argv[2]+"archon_metadata", "w")
                metadata_f_writer.write(dt_string+";\n"+str(now)+";\n"+os.getlogin())
                metadata_f_writer.close()
                # Make the arcive
                shutil.make_archive(
                    sys.argv[3]+"\\"+foldername, 'xztar', sys.argv[2])
                if encrypted:
                    pyAesCrypt.encryptFile(sys.argv[3]+"\\"+foldername+".tar.xz", sys.argv[3]+"\\"+foldername+".tar.xz.aes", passw=password, bufferSize=1024*64)
                    if overwrite:
                        print(colored("[-] Overwriting unencrypted version. This may take long.", "blue"))
                        filedestroy(sys.argv[3]+"\\"+foldername+".tar.xz")
                    else:
                        os.remove(sys.argv[3]+"\\"+foldername+".tar.xz")
                # Delete the metadata from the folder
                os.remove(sys.argv[2]+"archon_metadata")
                print(colored("[*] Backup folder", "green"))  # Print Done
                # Push to the dashboard
                dashboard.push("success", sys.argv[2], sys.argv[3]+foldername+".tar.xz", True)
                dashboard.show()
            except FileNotFoundError:
                dashboard.push("fail_filenotfound",
                               sys.argv[2], sys.argv[3]+foldername+".tar.xz", True)
                dashboard.show()
                print(colored("File Not Found\nExiting now", "red"))
        elif sys.argv[1] == "frestore":
            encrypted = "Y" == input(colored("Is the backup you want to use encrypted? (Y/n) ", "blue"))
            if encrypted:
                password = input(colored("Password> ", "blue"))
            try:
                print(colored("[-] Getting backups", "blue"))  # Status message
                # Download the backup
                shutil.copy(sys.argv[2], ".\\temp_archon_restore_file.tmp")
                if encrypted:
                    pyAesCrypt.decryptFile(infile=".\\temp_archon_restore_file.tmp", outfile=".\\temp_archon_restore_file.tmp.d", passw=password, bufferSize=1024*64)
                if os.path.exists(".\\temp_archon_restore_file.tmp"):
                    print(colored("[*] Got backups", "green"))
                else:
                    print(colored("[x] Getting backups failed. Please try again.", "red"))
                    print("Exiting now")
                    exit()
                print(colored("[-] Restoring files", "blue"))  # Status message
                # Unpack the downloaded archive
                if encrypted:
                    shutil.unpack_archive(
                        ".\\temp_archon_restore_file.tmp.d", sys.argv[3], format="xztar")
                    print(colored("[*] Restoring files", "green"))
                else:
                    shutil.unpack_archive(
                        ".\\temp_archon_restore_file.tmp", sys.argv[3], format="xztar")
                    print(colored("[*] Restoring files", "green"))
                # Read the metadata to the chache
                metadata_f_reader_ftp = open(sys.argv[3]+"archon_metadata", "r")
                metadata = metadata_f_reader_ftp.read()
                metadata_f_reader_ftp.close()
                print(colored("[-] Remove temporary files", "blue"))  # Status message
                os.remove(sys.argv[3]+"archon_metadata")  # Remove metadata file
                os.remove(".\\temp_archon_restore_file.tmp") # Remove downloaded file
                if encrypted:
                    os.remove(".\\temp_archon_restore_file.tmp.d")
                # Print status message and metadata time
                print(colored("[*] Restored from backup (Backup Time " +
                    metadata.split(";\n")[0]+")", "green"))
            except IndexError:
                print(colored("File Not Found\nExiting now", "red"))
        elif sys.argv[1] == "fbackupftp":
            host = input(colored("Host: ", "blue"))
            username = input(colored("Username: ", "blue"))
            password_server = input(colored("Password: ", "blue"))
            backup_archive = ".\\archon_temp_backup_ftp_archive.tar.xz"
            backup_location = sys.argv[3]

            encrypted = "Y" == input(colored("Do you want to make an encrypted archive? (Y/n) ", "blue"))
            if encrypted:
                password = input(colored("Password> ", "blue"))
                overwrite = "y" == input(colored("Do you want to overwrite the unencrypted version (y/N) ", "blue"))

            try:
                print(colored("[-] Generate archive", "blue"))
                foldername = os.path.dirname(sys.argv[2]).split(
                    "\\")[len(os.path.dirname(sys.argv[2]).split("\\"))-1]  # Get foldername
                print(colored("[-] Make compressed tar archive", "blue"))  # Print "Make the archive"
                # Write the metadata to the backupfolder
                metadata_f_writer_ftp = open(sys.argv[2]+"archon_metadata",
                     "w")
                metadata_f_writer_ftp.write(dt_string+";\n"+str(now)+";\n"+os.getlogin())
                metadata_f_writer_ftp.close()
                # Make the arcive
                shutil.make_archive(
                    ".\\archon_temp_backup_ftp_archive", 'xztar', sys.argv[2])
                if encrypted:
                    pyAesCrypt.encryptFile(".\\archon_temp_backup_ftp_archive.tar.xz", ".\\archon_temp_backup_ftp_archive.tar.xz.aes", passw=password, bufferSize=1024*64)
                    if overwrite:
                        filedestroy(".\\archon_temp_backup_ftp_archive.tar.xz")
                    else:
                        os.remove(".\\archon_temp_backup_ftp_archive.tar.xz")
                # Delete the metadata from the folder
                os.remove(sys.argv[2]+"archon_metadata")
                print(colored("[*] Backup folder", "green"))  # Print Done
            except FileNotFoundError:
                print(colored("File Not Found\nExiting now", "red"))
                
            print(colored("[-] Connecting", "blue"))
            if sys.argv[4] == "tls":
                print(colored("[-] Will use TLS (FTPS)", "blue"))
                connection = ftplib.FTP_TLS(host=host)
            elif sys.argv[4] == "none":
                print(colored("[?] Your connection is not secure. Do you want to continue?", "red"))
                if input("Y/n> ") == "Y":
                    connection = ftplib.FTP(host=host)
                else:
                    print(colored("[x] Abborted", "red"))
                    exit()
            else:
                print(colored("[?] Your connection is not secure. Do you want to continue?", "red"))
                if input("Y/n> ") == "Y":
                    connection = ftplib.FTP(host=host)
                else:
                    print(colored("[x] Abborted", "red"))
                    exit()
            connection.connect()
            try:
                connection.login(user=username, passwd=password_server)
                print(colored("[*] Connected", "green"))
            except ftplib.error_perm:
                print(colored("[x] Permission Error", "red"))
                exit()
            try:
                if encrypted:
                    backup_archive += ".aes"
                else:
                    backup_archive = backup_archive
                backup_submitter = open(backup_archive, "rb")
                connection.storbinary("STOR %s" % (backup_location),  backup_submitter)
                backup_submitter.close()
                print(colored("[*] Wrote file to server", "green"))
            except ftplib.error_perm:
                print(colored("[x] You're not allowed to write the backup there", "red"))
            connection.close()
            if encrypted:
                os.remove(".\\archon_temp_backup_ftp_archive.tar.xz.aes")
            else:
                os.remove(".\\archon_temp_backup_ftp_archive.tar.xz")
            print(colored("[-] FTP Connection Closed", "blue"))
            print(colored("[*] Done", "green"))
        elif sys.argv[1] == "frestoreftp":
            host = input(colored("Host: ", "blue"))
            username = input(colored("Username: ", "blue"))
            password = input(colored("Password: ", "blue"))
            encrypted = "Y" == input(colored("Is the backup you want to use encrypted? (Y/n) ", "blue"))
            if encrypted:
                password_archive = input(colored("Password> ", "blue"))

            # FTP
            # Build FTP Connection
            if sys.argv[4] == "tls":
                print(colored("[-] Will use TLS (FTPS)", "blue"))
                connection = ftplib.FTP_TLS(host=host)
            elif sys.argv[4] == "none":
                print(colored("[?] Your connection is not secure. Do you want to continue?", "red"))
                if input("Y/n> ") == "Y":
                    connection = ftplib.FTP(host=host)
                else:
                    print(colored("[x] Abborted", "red"))
                    exit()
            else:
                print(colored("[?] Your connection is not secure. Do you want to continue?", "red"))
                if input("Y/n> ") == "Y":
                    connection = ftplib.FTP(host=host)
                else:
                    print(colored("[x] Abborted", "red"))
                    exit()
            connection.login(user=username, passwd=password)
            print(colored("[*] Connected", "green"))
            connection.retrbinary("RETR %s" % (sys.argv[2]), open("temp_archon_restore_file_ftp.tmp", "wb").write)
            if encrypted:
                pyAesCrypt.decryptFile("temp_archon_restore_file_ftp.tmp", "temp_archon_restore_file_ftp.tmp.d", passw=password_archive, bufferSize=1024*63)
            try:
                print(colored("[-] Getting backups", "blue"))  # Status message
                # Download the backup
                if os.path.exists(".\\temp_archon_restore_file_ftp.tmp") or os.path.exists(".\\temp_archon_restore_file_ftp.tmp.d"):
                    print(colored("[*] Got backups", "green"))
                else:
                    print(colored("[x] Getting backups failed. Please try again.", "red"))
                    print("Exiting now")
                    exit()
                print(colored("[-] Restoring files", "blue"))  # Status message
                # Unpack the downloaded archive
                if encrypted:
                    shutil.unpack_archive(
                        ".\\temp_archon_restore_file_ftp.tmp.d", sys.argv[3], format="xztar")
                else:
                        shutil.unpack_archive(
                        ".\\temp_archon_restore_file_ftp.tmp", sys.argv[3], format="xztar")
                print(colored("[*] Restoring files", "green"))
                # Read the metadata to the chache
                metadata = open(sys.argv[3]+"archon_metadata", "r").read()
                print(colored("[-] Remove temporary files", "blue"))  # Status message
                os.remove(sys.argv[3]+"archon_metadata")  # Remove metadata file
                os.remove(".\\temp_archon_restore_file_ftp.tmp") # Remove downloaded file
                if encrypted:
                    os.remove(".\\temp_archon_restore_file_ftp.tmp.d")
                # Print status message and metadata time
                print(colored("[*] Restored from backup (Backup Time " +
                    metadata.split(";\n")[0]+")", "green"))
            except FileNotFoundError:
                print(colored("File Not Found\nExiting now", "red"))
            except ftplib.error_perm:
                print(colored("Permission Error. Please check your password and username.", "red"))
except IndexError:
    print(colored("You need more arguments.\nExiting now", "red"))