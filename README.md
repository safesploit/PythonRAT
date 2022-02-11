# PythonRAT

**The MALWARE _PythonRAT_ is for EDUCATIONAL PURPOSES ONLY!!** 

**Description**

PythonRAT is a Command and Control (C2) server which can control multiple machines running the Remote Administration Trojan (RAT) forming a botnet cluster which was written in Python3. 


# Features

- Keylogger written as a class
- Keylogger can be started and stopped remote with options to _dump_ or _overwrite_ the log file
- Download files from target
- Upload files to target
- C2 allows control of multiple target sessions w/ background session
- Issue a _sendall *command*_ to every active session
- Persistence by creating a registry entry (Windows)
- Screenshot of the target's screen which is sent to server
- Remote shutdown of the backdoor _(executable is NOT safely removed)_


# Usage Manuals
**C2 Manual**

    targets                 --> Prints Active Sessions
    session *session num*   --> Will Connect To Session (background to return)
    clear                   --> Clear Terminal Screen
    exit                    --> Quit ALL Active Sessions and Closes C2 Server!!
    kill *session num*      --> Issue 'quit' To Specified Target Session
    sendall *command*       --> Sends The *command* To ALL Active Sessions (sendall notepad)



**Session Manual**

    quit                                --> Quit Session With The Target
    clear                               --> Clear The Screen
    background                          --> Send Session With Target To Background
    cd *Directory name*                 --> Changes Directory On Target System
    upload *file name*                  --> Upload File To The Target Machine From Working Dir 
    download *file name*                --> Download File From Target Machine
    get *url*                           --> Download File From Specified URL
    keylog_start                        --> Start The Keylogger
    keylog_dump                         --> Print Keystrokes That The Target From taskmanager.txt
    keylog_stop                         --> Stop And Self Destruct Keylogger File
    persistence *RegName* *filename*    --> Create Persistence In Registry
    screenshot                          --> Takes screenshot and sends to server ./screenshots/
    remove_backdoor                     --> Removes backdoor from target!!!

# Wine and Pyinstaller (Win version) Installation on Linux

Python 2.7.14 Releases: https://www.python.org/downloads/release/python-2714/

**Environment Setup**

┌──(root💀kali)-[~/]

└─# 
    sudo su
    
    dpkg --add-architecture i386
    apt update
    apt install wine32 
    wget https://www.python.org/ftp/python/2.7.14/python-2.7.14.msi
    sudo wine msiexec -i ~/python-2.7.14.msi #x86 arch
    
    
**Installing Dependencies**

┌──(root💀kali)-[~/.wine/drive_c]

└─# 

    cd /root/.wine/drive_c/Python27
    wine python.exe -m pip install  pyinstaller
                                    requests
                                    pyautogui


# Backdoor Compilation and Obfuscation for Windows

**Compile to Executable using Pyinstaller**

    $ pyinstaller --onefile --noconsole backdoor.py
    
This will produce _./dist/backdoor.exe_


**Obfuscation using SFX archive**

The executable _backdoor.exe_ will be made to look like an image (jpg) file.
By default Windows does not show file extensions (e.g. backdoor.exe will show in Windows Explorer as backdoor).
Hence, we will create an SFX archive name _wallpaper.jpg.exe_ which Windows Explorer will show as _wallpaper.jpg_.

This will involve having image.jpg which we will also create an icon version of _.ico_ to assign the SFX archive.
Making the executable appear to be an image.

**Creating SFX archive**

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


This will produce an SFX archive which looks like an image

While inspecting the file will reveal it is an executable the file extension _.exe_ is concealed.
Furthermore, if viewed from the Desktop cannot be differentiated between a 'real' image.

<img width="842" alt="image8" src="https://user-images.githubusercontent.com/10171446/153408539-972eba00-ca38-4cfc-be3b-556cf9ae74c7.PNG">


Once opened the SFX archive will open the image file inside the archive and the malware will execute after.

Due to _--noconsole_ argument in _Pyinstaller_, no window will be rendered.


**Task Manager**

The _backdoor.exe_ process can be seen in Task Manager and ended there if necessary.

# Preview Images

**Target connection to C2 Server**

![Screenshot_2022-02-10_06-16-22](https://user-images.githubusercontent.com/10171446/153403206-4ce3dc23-4c1a-41b6-a715-2e2021d965ce.png)


**Interacting with Session**

![Screenshot_2022-02-10_06-17-20](https://user-images.githubusercontent.com/10171446/153403283-3df77fd8-2cbe-4990-b82f-d847bdde3bee.png)


**Test Commands on Target**

![Screenshot_2022-02-10_06-22-48](https://user-images.githubusercontent.com/10171446/153403427-058ebe8a-36d8-465c-8386-7a55cea1641b.png)


**Session Options**

![Screenshot_2022-02-10_06-23-21](https://user-images.githubusercontent.com/10171446/153403579-3b090b00-2dec-4c33-a94d-020eb2b0d2b4.png)


**Backgrounding and Killing Session**

![Screenshot_2022-02-10_06-25-04](https://user-images.githubusercontent.com/10171446/153403973-d9757c68-4ca2-405f-ae13-a0ca0666bfcc.png)

