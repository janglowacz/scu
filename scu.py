import os
import sys
import math
import time
import importlib
import subprocess

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# ====================================================================================================
#   _____  _____ _____ _    _               __   ____  
#  / ____|/ ____/ ____| |  | |         /\  /_ | |___ \ 
# | (___ | |   | |    | |  | | __   __/  \  | |   __) |
#  \___ \| |   | |    | |  | | \ \ / / /\ \ | |  |__ < 
#  ____) | |___| |____| |__| |  \ V / ____ \| |_ ___) |
# |_____/ \_____\_____|\____/    \_/_/    \_\_(_)____/ 
#                                                                                                 
# ====================================================================================================
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# https://patorjk.com/software/taag/#p=display&f=Big

SCU_VERSION = 'A1.3'
SCU_VERSION_FULL = 'A1.3.2023-09-20'

# ====================================================================================================

def argv():
    ''' Function to output command line arguments given to the program, separated between {normal} and {-} arguments. '''
    args = sys.argv[1:]
    return [arg for arg in args if not arg[:1] == '-'], {arg[1:] for arg in args if arg[:1] == '-'}

def imports(*Args):
    ''' Function to automatically import a number of packages. '''
    for arg in Args:
        if isinstance(arg, str):
            pack_manage(arg)
        else:
            raise TypeError('The arguments have to be strings')

def pack_manage(package):
    ''' Function to automatically import a package. '''
    try:
        importlib.import_module(package)
        return True
    except ModuleNotFoundError:
        Flag = pack_install(package)
        if Flag == False:
            return False
        try:
            importlib.import_module(package)
            return True
        except ModuleNotFoundError:
            return False

def pack_install(package):
    ''' Function to automatically install a package. '''
    printc('SCU> Attemting to install package', package, Color='Blue')
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except subprocess.CalledProcessError:
        return False

# ====================================================================================================

''' ANSI escape sequence foreground colors: '''
COLORS_FG = {   None:';37',
                'White':';37', 'Red':';31', 'Green':';32', 'Blue':';34', 'Cyan':';36', 'Yellow':';33', 'Magenta':';35', 'Black':';30', 'Grey':';90',
                'W':';37', 'R':';31', 'G':';32', 'B':';34', 'C':';36', 'Y':';33', 'M':';35', 'K':';30',
                'Wb':';97', 'Rb':';91', 'Gb':';92', 'Bb':';94', 'Cb':';96', 'Yb':';93', 'Mb':';95', 'Kb':';90',
                'Orange':';38;5;208', 'O':';38;5;208'}

''' ANSI escape sequence background colors: '''
COLORS_BG = {   None:'',
                'White':';47', 'Red':';41', 'Green':';42', 'Blue':';44', 'Cyan':';46', 'Yellow':';43', 'Magenta':';45', 'Black':';40', 'Grey':';100',
                'W':';47', 'R':';41', 'G':';42', 'B':';44', 'C':';46', 'Y':';43', 'M':',45', 'K':';40',
                'Wb':';107', 'Rb':';101', 'Gb':';102', ';Bb':';104', 'Cb':';106', 'Yb':';103', 'Mb':';105', 'Kb':';100',
                'Orange':';48;5;208', 'O':';48;5;208'}

''' ANSI escape sequence text styles: '''
STYLES = {None:'0', 'B':'1', 'U':'2'}

def txt_c(*Args, Color=None, C=None, Color_background=None, Style=None):
    ''' Function to return a colored version of the text args submitted. '''
    if Color is None:
        Color = C
    sequence = '\033[' +STYLES[Style] +COLORS_FG[Color] +COLORS_BG[Color_background] +'m'
    return sequence +' '.join([str(x) for x in Args])+'\033[0m'

# ====================================================================================================

def printc(*Args, Color=None, Color_background=None, Style=None):
    ''' Function to print a colored version of the args submitted. '''
    print(txt_c(*Args, Color=Color, Color_background=Color_background, Style=Style))

def printf(*Args, Final=False, Color='White', Color_background=None, Style=None, Width=None):
    ''' Function to overwrite the current line with a colored version of the args submitted. '''
    if Width is None:
        Width = os.get_terminal_size()[0]
    sys.stdout.write('\r'+' '*Width +'\r' +txt_c(*Args, Color=Color, Color_background=Color_background, Style=Style))
    if Final:
        sys.stdout.write('\n')

def printm(List, Final=False, Width=None):
    ''' Function to overwrite multiple lines with the args taken from the list submitted. '''
    if Width is None:
        Width = os.get_terminal_size()[0]
    if not(isinstance(List, list) or isinstance(List, tuple)):
        raise TypeError('The first argument has to be a list or a tuple')
    sys.stdout.write('\033[' +str(len(List))+'F')
    for line in List:
        if isinstance(line, list) or isinstance(line, tuple):
            line = ' '.join([str(x) for x in line])
        sys.stdout.write(' '*Width +'\r' +line +'\033[1E')
    if Final:
        sys.stdout.write('\n')

# ====================================================================================================

def txt_t(i, Max, Timestamp):
    ''' Function to create a percentage and remaining time string. '''
    per = (i+1)/Max
    rem = (time.perf_counter() - Timestamp) / per * (1-per)
    return '{:.2f}% {:.0f}s'.format(per*100, rem)

def txt_err(value, error, separate_uncerainty=False, figures=2):
    ''' Function to format a value and its error. '''
    cut_point = math.floor(math.log10(error)) +1 -figures
    if cut_point >= 0:
        if separate_uncerainty:
            return '{:.0f} ± {:.0f}'.format(value, error)
        else:
            return '{:.0f}({:.0f})'.format(value, error)
    else:
        if separate_uncerainty:
            return ('{:.' +str(-cut_point) +'f} ± {:.' +str(-cut_point) +'f}').format(value, error)
        else:
            return ('{:.' +str(-cut_point) +'f}({:.0f})').format(value, error *pow(10, -cut_point))

# ====================================================================================================

def chi_squared_test(f, xdata, ydata, sigma, par):
    ''' Function to calculate the chi square and reduced chi square from the outputs of a curve fit.\n 
        Returns the chi^2; nu; chi^2/nu.\n
        Chi^2/nu >> 1 inidcates a poor model.\n
        Chi^2/nu > 1 indicates a slightly mismatched model or an error underestimation.\n
        Chi^2/nu ~ 1 indicates a good fit.\n
        Chi^2/nu < 1 indicates an overfit or an error overestimation.\n
        Implementation source: https://en.wikipedia.org/wiki/Reduced_chi-squared_statistic. '''
    f_data = [f(x, *par) for x in xdata]
    chi_squared = sum([pow((ydata[i]-f_data[i])/sigma[i], 2) for i, _ in enumerate(ydata)])
    nu = len(xdata) - len(par)
    return chi_squared, nu, chi_squared/nu

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# ====================================================================================================
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

if __name__ == '__main__':
    print(txt_c('SCU version:', C='Blue'), SCU_VERSION_FULL)
    print(txt_c('Sys platform:', C='Blue'), sys.platform)
    print(txt_c('Sys recursion limit:', C='Blue'), sys.getrecursionlimit())