def banner():
    return (Colour.green("""                                   
,------.          ,------.   ,---. ,--------. 
|  .--. ',--. ,--.|  .--. ' /  O  \'--.  .--' 
|  '--' | \  '  / |  '--'.'|  .-.  |  |  |    
|  | --'   \   '  |  |\  \ |  | |  |  |  |    
`--'     .-'  /   `--' '--'`--' `--'  `--'    
         `---'                                
    """) + "(" +
            Colour.blue("v0.12.0-alpha") + ")" +
            Colour.yellow(" Author: safesploit") +
            "\n")


class Colour():
    @staticmethod
    def red(str):
        return "\033[91m" + str + "\033[0m"

    @staticmethod
    def green(str):
        return "\033[92m" + str + "\033[0m"

    @staticmethod
    def yellow(str):
        return "\033[93m" + str + "\033[0m"

    @staticmethod
    def blue(str):
        return "\033[94m" + str + "\033[0m"

# TODO
# The following are untested values

    @staticmethod
    def purple(str):
        return "\033[95m" + str + "\033[0m"

    @staticmethod
    def cyan(str):
        return "\033[96m" + str + "\033[0m"

    @staticmethod
    def white(str):
        return "\033[97m" + str + "\033[0m"

    @staticmethod
    def black(str):
        return "\033[90m" + str + "\033[0m"
    

    @staticmethod
    def bright_green(str):
        return "\033[1;92m" + str + "\033[0m"

    @staticmethod
    def bright_yellow(str):
        return "\033[1;93m" + str + "\033[0m"

    @staticmethod
    def bright_blue(str):
        return "\033[1;94m" + str + "\033[0m"

    @staticmethod
    def bright_purple(str):
        return "\033[1;95m" + str + "\033[0m"

    @staticmethod
    def bright_cyan(str):
        return "\033[1;96m" + str + "\033[0m"

    @staticmethod
    def bright_white(str):
        return "\033[1;97m" + str + "\033[0m"

    @staticmethod
    def bg_red(str):
        return "\033[41m" + str + "\033[0m"

    @staticmethod
    def bg_green(str):
        return "\033[42m" + str + "\033[0m"

    @staticmethod
    def bg_yellow(str):
        return "\033[43m" + str + "\033[0m"

    @staticmethod
    def bg_blue(str):
        return "\033[44m" + str + "\033[0m"

    @staticmethod
    def bg_purple(str):
        return "\033[45m" + str + "\033[0m"

    @staticmethod
    def bg_cyan(str):
        return "\033[46m" + str + "\033[0m"

    @staticmethod
    def bg_white(str):
        return "\033[47m" + str + "\033[0m"
# print(banner())
