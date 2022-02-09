# PythonRAT

**The MALWARE _PythonRAT_ is for EDUCATIONAL PURPOSES ONLY!!** 

**Description**

PythonRAT is a Command and Control (C2) server which can control multiple machines running the Remote Administration Trojan (RAT) forming a botnet cluster which was written in Python3. 



# Usage Manuals
**C2 Manual**

    targets                 --> Prints Active Sessions
    session *session num*   --> Will Connect To Session (background to return)
    clear                   --> Clear Terminal Screen
    exit                    --> Quit ALL Active Sessions and Closes C2 Server!!
    kill *session num*      --> Issue 'quit' To Specified Target Session
    sendall *command*       --> Sends The *command* To ALL Active Sessions (sendall notepad)
    remove_backdoor         --> Removes backdoor from target



**Session Manual**

    quit                                --> Quit Session With The Target
    clear                               --> Clear The Screen
    background                          --> Send Session With Target To Background
    cd *Directory name*                 --> Changes Directory On Target System
    upload *file name*                  --> Upload File To The Target Machine From Working Dir 
    download *file name*                --> Download File From Target Machine
    keylog_start                        --> Start The Keylogger
    keylog_dump                         --> Print Keystrokes That The Target From taskmanager.txt
    keylog_stop                         --> Stop And Self Destruct Keylogger File
    persistence *RegName* *filename*    --> Create Persistence In Registry
    screenshot                          --> Takes screenshot and sends to server ./screenshots/
    remove_backdoor                     --> Removes backdoor from target
