import os
import sys
import math
import time
import importlib
import subprocess
import json
import zlib

SCU_VERSION = 'A1.8'
SCU_VERSION_FULL = 'A1.8.2024-06-26'
# Updated the argmanage function
# Added compression filestorage methods

# ====================================================================================================

def argv():
    ''' Function to output command line arguments given to the program, separated between {normal} and {keyed (-)} arguments. '''
    argv = sys.argv[1:]
    args, kwargs, flag = [], {}, 0
    for key in argv:
        if key[0] == '-':
            if flag == 0:
                flag = 1
            if key[0] == '-' and flag == 1:
                flag = 2
                pack_key, pack_vals = key[1:], []
            if key[0] == '-' and flag == 2:
                flag = 1
                kwargs.update({pack_key: pack_vals})
        else:
            if flag == 0:
                args.append(key)
            else:
                pack_vals.append(key)
    return args, kwargs

def imports(*args):
    ''' Function to automatically import a number of packages. '''
    for arg in args:
        if isinstance(arg, str):
            pack_manage(arg)
        else:
            raise TypeError('The arguments have to be strings')
    return None

def pack_manage(package:str):
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

def pack_install(package:str):
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
                'white':';37', 'red':';31', 'green':';32', 'blue':';34', 'cyan':';36', 'yellow':';33', 'magenta':';35', 'black':';30', 'grey':';90',
                'w':';37', 'r':';31', 'g':';32', 'b':';34', 'c':';36', 'y':';33', 'm':';35', 'k':';30',
                'wb':';97', 'rb':';91', 'gb':';92', 'bb':';94', 'cb':';96', 'yb':';93', 'mb':';95', 'kb':';90',
                'orange':';38;5;208', 'o':';38;5;208'}

''' ANSI escape sequence background colors: '''
COLORS_BG = {   None:'',
                'white':';47', 'red':';41', 'green':';42', 'blue':';44', 'cyan':';46', 'yellow':';43', 'magenta':';45', 'black':';40', 'grey':';100',
                'w':';47', 'r':';41', 'g':';42', 'b':';44', 'c':';46', 'y':';43', 'm':',45', 'k':';40',
                'wb':';107', 'rb':';101', 'gb':';102', ';bb':';104', 'cb':';106', 'yb':';103', 'mb':';105', 'kb':';100',
                'orange':';48;5;208', 'o':';48;5;208'}

''' ANSI escape sequence text styles: '''
STYLES = {None:'0', 'b':'1', 'u':'2'}

def _lower_none(key:None|str):
    ''' Function that returns a lowered string or None, depending on the input. '''
    if key is None: return key
    else: return key.lower()

def txt_c(*args, color:str=None, c:str=None, color_background:str=None, style:str=None):
    ''' Function to return a colored version of the text args submitted. '''
    if color is None:
        color = c
    sequence = '\033[' +STYLES[_lower_none(style)] +COLORS_FG[_lower_none(color)] +COLORS_BG[_lower_none(color_background)] +'m'
    return sequence +' '.join([str(x) for x in args])+'\033[0m'

# ====================================================================================================

def printc(*args, color:str=None, c:str=None, color_background:str=None, style:str=None):
    ''' Function to print a colored version of the args submitted. '''
    if color is None:
        color = c
    print(txt_c(*args, color=color, color_background=color_background, style=style))
    return None

def printf(*args, final:bool=False, color:str=None, c:str=None, color_background:str=None, style:str=None, width:int=None):
    ''' Function to overwrite the current line with a colored version of the args submitted. '''
    if color is None:
        color = c
    if width is None:
        width = os.get_terminal_size()[0]
    sys.stdout.write('\r'+' '*width +'\r' +txt_c(*args, color=color, color_background=color_background, style=style))
    if final:
        sys.stdout.write('\n')
    return None

def printm(iterable, final:bool=False, width:int=None):
    ''' Function to overwrite multiple lines with the args taken from the list submitted. '''
    if width is None:
        width = os.get_terminal_size()[0]
    if not(isinstance(iterable, list) or isinstance(iterable, tuple)):
        raise TypeError('The first argument has to be a list or a tuple')
    sys.stdout.write('\033[' +str(len(iterable))+'F')
    for line in iterable:
        if isinstance(line, list) or isinstance(line, tuple):
            line = ' '.join([str(x) for x in line])
        sys.stdout.write(' '*width +'\r' +line +'\033[1E')
    if final:
        sys.stdout.write('\n')
    return None

# ====================================================================================================

def txt_t(i:int, max:int, timestamp:float):
    ''' Function to create a percentage and remaining time string. '''
    per = (i+1)/max
    rem = (time.perf_counter() - timestamp) / per * (1-per)
    return '{:.2f}% {:.0f}s'.format(per*100, rem)

# ====================================================================================================

def txt_err(value:float, error:float, sperate_uncertainty:bool=False, figures:int=2):
    ''' Function to format a value and error. '''
    cut_point = math.floor(math.log10(error)) +1 -figures
    if cut_point >= 0:
        if sperate_uncertainty:
            return '{:.0f} ± {:.0f}'.format(value, error)
        else:
            return '{:.0f}({:.0f})'.format(value, error)
    else:
        if sperate_uncertainty:
            return ('{:.' +str(-cut_point) +'f} ± {:.' +str(-cut_point) +'f}').format(value, error)
        else:
            return ('{:.' +str(-cut_point) +'f}({:.0f})').format(value, error *pow(10, -cut_point))

def chi_squared_test(func, x_data, y_data, sigma, pars):
    ''' Function to calculate the chi square and reduced chi square from the outputs of a curve fit.\n 
        Returns the chi^2; nu; chi^2/nu.\n
        Chi^2/nu >> 1 inidcates a poor model.\n
        Chi^2/nu > 1 indicates a slightly mismatched model or an error underestimation.\n
        Chi^2/nu ~ 1 indicates a good fit.\n
        Chi^2/nu < 1 indicates an overfit or an error overestimation.\n
        Implementation source: https://en.wikipedia.org/wiki/Reduced_chi-squared_statistic. '''
    f_data = [func(x, *pars) for x in x_data]
    chi_squared = sum([pow((y_data[i]-f_data[i])/sigma[i], 2) for i, _ in enumerate(y_data)])
    nu = len(x_data) - len(pars)
    return chi_squared, nu, chi_squared/nu

# ====================================================================================================

def dump_c(object, file)->None:
    ''' Compresses the json serializable object into the file.\n
        File must be opened as \"wb\".'''
    object_comp = dumps_c(object)
    file.write(object_comp)
    return None

def load_c(file)->None:
    ''' Decompresses the json serializable object from the file.\n
        File must be opened as \"rb\". '''
    object_comp = file.read()
    object = loads_c(object_comp)
    return object

def dumps_c(object)->None:
    ''' Compresses the json serializable object into a bytes. '''
    object_json = json.dumps(object)
    object_bytes = bytes(object_json, 'utf-8')
    compressor = zlib.compressobj(level=9, memLevel=9)
    object_comp = compressor.compress(object_bytes)
    object_comp += compressor.flush()
    return object_comp

def loads_c(object_comp:bytes):
    ''' Decompresses the json serializable object from a bytes. '''
    decompressor = zlib.decompressobj()
    object_bytes = decompressor.decompress(object_comp)
    object_bytes += decompressor.flush()
    object = json.loads(str(object_bytes, 'utf-8'))
    return object

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# ====================================================================================================
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

if __name__ == '__main__':
    print(txt_c('SCU version:', color='Blue'), SCU_VERSION_FULL)
    print(txt_c('Sys platform:', color='Blue'), sys.platform)
    print(txt_c('Sys recursion limit:', color='Blue'), sys.getrecursionlimit())