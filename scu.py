import os
import sys
import math
import time
import importlib
import subprocess

'''
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
====================================================================================================
   _____  _____ _    _             __ _  _   
  / ____|/ ____| |  | |       /\  /_ | || |  
 | (___ | |    | |  | |_   __/  \  | | || |_ 
  \___ \| |    | |  | \ \ / / /\ \ | |__   _|
  ____) | |____| |__| |\ V / ____ \| |_ | |  
 |_____/ \_____|\____/  \_/_/    \_\_(_)|_|  
                                             
====================================================================================================
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
https://patorjk.com/software/taag/#p=display&f=Big
'''

SCU_VERSION = 'A1.4'
SCU_VERSION_FULL = 'A1.4.2023-10-27'

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

def txt_c(*Args, Color:str=None, C:str=None, Color_background:str=None, Style:str=None):
    ''' Function to return a colored version of the text args submitted. '''
    if Color is None:
        Color = C
    sequence = '\033[' +STYLES[Style] +COLORS_FG[Color] +COLORS_BG[Color_background] +'m'
    return sequence +' '.join([str(x) for x in Args])+'\033[0m'

# ====================================================================================================

def printc(*Args, Color:str=None, C:str=None, Color_background:str=None, Style:str=None):
    ''' Function to print a colored version of the args submitted. '''
    if Color is None:
        Color = C
    print(txt_c(*Args, Color=Color, Color_background=Color_background, Style=Style))
    return None

def printf(*Args, Final:bool=False, Color:str=None, C:str=None, Color_background:str=None, Style:str=None, Width:int=None):
    ''' Function to overwrite the current line with a colored version of the args submitted. '''
    if Color is None:
        Color = C
    if Width is None:
        Width = os.get_terminal_size()[0]
    sys.stdout.write('\r'+' '*Width +'\r' +txt_c(*Args, Color=Color, Color_background=Color_background, Style=Style))
    if Final:
        sys.stdout.write('\n')
    return None

def printm(List, Final:bool=False, Width:int=None):
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
    return None

# ====================================================================================================

def txt_t(i:int, Max:int, Timestamp:float):
    ''' Function to create a percentage and remaining time string. '''
    per = (i+1)/Max
    rem = (time.perf_counter() - Timestamp) / per * (1-per)
    return '{:.2f}% {:.0f}s'.format(per*100, rem)

# ====================================================================================================

def txt_err(Value:float, Error:float, Separate_uncerainty:bool=False, Figures:int=2):
    ''' Function to format a value and error. '''
    cut_point = math.floor(math.log10(Error)) +1 -Figures
    if cut_point >= 0:
        if Separate_uncerainty:
            return '{:.0f} ± {:.0f}'.format(Value, Error)
        else:
            return '{:.0f}({:.0f})'.format(Value, Error)
    else:
        if Separate_uncerainty:
            return ('{:.' +str(-cut_point) +'f} ± {:.' +str(-cut_point) +'f}').format(Value, Error)
        else:
            return ('{:.' +str(-cut_point) +'f}({:.0f})').format(Value, Error *pow(10, -cut_point))
        
# ====================================================================================================

''' Physical qunatity configuration: '''   
QUANTITIES = {'Time':           ['s',       False],
              'Frequency':      ['Hz',      True],
              'Length':         ['m',       True],
              'Area':           ['m²',      False],
              'Volume':         ['m³',      False],
              'Volume_L':       ['L',       True],
              'Velocity':       ['m/s',     True],
              'Acceleration':   ['m/s²',    True],
              'Jerk':           ['m/s³',    True],
              'Angle':          ['rad',     False],
              'AngleSolid':     ['sr',      False],
              'Angle_degree':   ['°',       False],
              'Mass':           ['kg',      False],
              'Density':        ['kg/m³',   False],
              'Density_cm':     ['kg/cm³',  False],
              'Density_L':      ['kg/L',    False],
              'Current':        ['A',       True],
              'Temperature':    ['K',       True],
              'Amount':         ['mol',     True],
              'Voltage':        ['V',       True],
              'Force':          ['N',       True],
              'Pressure':       ['Pa',      True],
              'Pressure_Bar':   ['Bar',     True],
              'Energy':         ['J',       True],
              'Energy_eV':      ['eV',      True],
              'Power':          ['W',       True],
              'Capacitance':    ['F',       True],
              'Resistance':     ['Ω',       True],
              'Conductance':    ['S',       True],
              'MagFlux':        ['Wb',      True],
              'MagFluxDensity': ['T',       True],
              'Inductance':     ['H',       True],
              'LumFlux':        ['lm',      True],
              'Illuminance':    ['lx',      True],
              'Activity':       ['Bq',      True],
              'DoseAbs':        ['Gy',      True],
              'DoseEq':         ['Sv',      True]}

''' SI unit prefixes: ''' 
PREFIXES = ['q','r','y','z','a','f','p','n','μ','m','','k','M','G','T','P','E','Z','Y','R','Q']

''' Special unit configuration: ''' 
UNITS_SPECIAL = {'Time':('s', (('as',1/1000),('fs',1/1000),('ps',1/1000),('ns',1/1000), ('μs',1/1000), ('ms',1/1000), ('s', 1), ('min',60), ('h',60), ('d',24), ('y',365), ('ky',1000), ('My',1000), ('Gy',1000), ('Ty',1000))),
                'Area':('m²', (('am³',pow(1000, -3)), ('fm²',pow(1000, -2)), ('pm²',pow(1000, -2)), ('nm²',pow(1000, -2)), ('μm²',pow(1000, -2)), ('mm²',pow(1000, -2)), ('m²', 1), ('km²',pow(1000, 2)), ('Mm²',pow(1000, 2)), ('Gm²',pow(1000, 2)), ('Tm²',pow(1000, 2)))),
                'Volume':('m²', (('am³',pow(1000, -3)), ('fm³',pow(1000, -3)), ('pm³',pow(1000, -3)), ('nm³',pow(1000, -3)), ('μm³',pow(1000, -3)), ('mm³',pow(1000, -3)), ('m³', 1), ('km³',pow(1000, 3)), ('Mm³',pow(1000, 3)), ('Gm³',pow(1000, 3)), ('Tm³',pow(1000, 3)))),
                'Angle':('rad', (('rad', 1),)),
                'AngleSolid':('sr', (('sr', 1),)),
                'Mass':('kg', (('ag', 1/1000), ('fg', 1/1000), ('pg', 1/1000), ('ng', 1/1000), ('μg', 1/1000), ('mg', 1/1000), ('g', 1/1000), ('kg', 1), ('T', 1000), ('kT', 1000), ('MT', 1000), ('GT', 1000), ('TT', 1000))),
                'Density':('kg/m³', (('ag', 1/1000), ('fg', 1/1000), ('pg', 1/1000), ('ng', 1/1000), ('μg', 1/1000), ('mg', 1/1000), ('g/cm³', 1/1000), ('kg/m³', 1), ('T/m³', 1000), ('kT', 1000), ('MT', 1000), ('GT', 1000), ('TT', 1000))),
                'Density':('kg/cm³', (('ag/cm³', 1/1000), ('fg/cm³', 1/1000), ('pg/cm³', 1/1000), ('ng/cm³', 1/1000), ('μg/cm³', 1/1000), ('mg/cm³', 1/1000), ('g/cm³', 1/1000), ('kg/cm³', 1), ('T/cm³', 1000), ('kT/cm³', 1000), ('MT/cm³', 1000), ('GT/cm³', 1000), ('TT/cm³', 1000))),
                'Density_Liter':('kg/m³', (('ag/L', 1/1000), ('fg/L', 1/1000), ('pg/L', 1/1000), ('ng/L', 1/1000), ('μg/L', 1/1000), ('mg/L', 1/1000), ('g/cm³', 1/1000), ('kg/L', 1), ('T/L', 1000), ('kT/L', 1000), ('MT/L', 1000), ('GT/L', 1000), ('TT/L', 1000)))}

def sign(x:float):
    ''' Function that returns the sign of x.'''
    return (x > 0) - (x < 0)

def txt_unit(Value:float, Error:float=None, Unit:str=None, Quantity:str=None, Separator:float='', Figures_Main:int=3, Figures_Error:int=2):
    ''' Function to format a value, error and unit. '''
    if Quantity is None:
        if Error is None:
            cut_point = math.floor(math.log10(Value)) +1 -Figures_Main
            valuepack = ('{:.'+str(max(0,-cut_point))+'f}').format(Value)
        else:
            valuepack = txt_err(Value, Error=Error)
        if Unit is None:
            unitpack = ''
        else:
            unitpack = Unit
    elif not Quantity is None:
        if not Quantity in QUANTITIES:
            raise ValueError(f'{Quantity} is not a valid quantity. Options are:\n'+', '.join(q for q in QUANTITIES))
        if QUANTITIES[Quantity][1]:
            if not Unit is None:
                if not QUANTITIES[Quantity][0] in Unit:
                    raise ValueError(f'Unit {Unit} does not match the quantity {QUANTITIES}')
                prefix = Unit.split(QUANTITIES[Quantity][0])[0]
                if not prefix in PREFIXES:
                    raise ValueError(f'{prefix} is not a valid prefix')
                prefix = PREFIXES.index(prefix)
                Value = Value * pow(10, -30+prefix*3)
            options = []
            for i in range(len(PREFIXES)):
                test = Value / pow(10, -30+i*3)
                if not Error is None:
                    test_error = Error / pow(10, -30+i*3)
                    options.append((i, txt_err(test, Error=test_error, Figures=Figures_Error)))
                else:
                    cut_point = math.floor(math.log10(test)) +1 -Figures_Main
                    options.append((i, ('{:.'+str(max(0,-cut_point))+'f}').format(test)))
            best = tuple(x for x in options if len(x[1].replace('.','')) == min(len(x[1].replace('.','')) for x in options))[-1]
            valuepack = best[1]
            unitpack = PREFIXES[best[0]]+QUANTITIES[Quantity][0]
        else:
            ref_i = UNITS_SPECIAL[Quantity][1].index((UNITS_SPECIAL[Quantity][0], 1))
            options = []
            for i in range(len(UNITS_SPECIAL[Quantity][1])):
                test = Value
                test_error = Error
                if not i == ref_i:
                    for j in [x for x in range(ref_i, i+sign(i-ref_i), sign(i-ref_i))][1:]:
                        test = test / UNITS_SPECIAL[Quantity][1][j][1]
                        if not Error is None:
                            test_error = test_error / UNITS_SPECIAL[Quantity][1][j][1]
                if not Error is None:
                    options.append((i, txt_err(test, Error=test_error, Figures=Figures_Error)))
                else:
                    cut_point = math.floor(math.log10(test)) +1 -Figures_Main
                    options.append((i, ('{:.'+str(max(0,-cut_point))+'f}').format(test)))
            best = tuple(x for x in options if len(x[1].replace('.','')) == min(len(x[1].replace('.','')) for x in options))[-1]
            valuepack = best[1]
            unitpack = UNITS_SPECIAL[Quantity][1][best[0]][0]
    return valuepack + Separator + unitpack

# ====================================================================================================

def chi_squared_test(F, Xdata, Ydata, Sigma, Par):
    ''' Function to calculate the chi square and reduced chi square from the outputs of a curve fit.\n 
        Returns the chi^2; nu; chi^2/nu.\n
        Chi^2/nu >> 1 inidcates a poor model.\n
        Chi^2/nu > 1 indicates a slightly mismatched model or an error underestimation.\n
        Chi^2/nu ~ 1 indicates a good fit.\n
        Chi^2/nu < 1 indicates an overfit or an error overestimation.\n
        Implementation source: https://en.wikipedia.org/wiki/Reduced_chi-squared_statistic. '''
    f_data = [F(x, *Par) for x in Xdata]
    chi_squared = sum([pow((Ydata[i]-f_data[i])/Sigma[i], 2) for i, _ in enumerate(Ydata)])
    nu = len(Xdata) - len(Par)
    return chi_squared, nu, chi_squared/nu

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# ====================================================================================================
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

if __name__ == '__main__':
    print(txt_c('SCU version:', C='Blue'), SCU_VERSION_FULL)
    print(txt_c('Sys platform:', C='Blue'), sys.platform)
    print(txt_c('Sys recursion limit:', C='Blue'), sys.getrecursionlimit())