def banner():
    return (Colour.green("""                                   
,------.          ,------.   ,---. ,--------. 
|  .--. ',--. ,--.|  .--. ' /  O  \'--.  .--' 
|  '--' | \  '  / |  '--'.'|  .-.  |  |  |    
|  | --'   \   '  |  |\  \ |  | |  |  |  |    
`--'     .-'  /   `--' '--'`--' `--'  `--'    
         `---'                                
    """) + "(" +
            Colour.blue("v1.0.0") + ")" +
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

# print(banner())
