from colorama import init,Fore,Style
init(autoreset=True)



class Color_Helper:

    def green_colored_printer(self,string):
        print(Fore.GREEN + Style.BRIGHT + string)

    def red_colored_printer(self,string):
        print(Fore.RED + Style.BRIGHT + string)

    def blue_colored_printer(self,string):
        print(Fore.BLUE + Style.BRIGHT + string)

