import os
import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import pickle

from sympy.codegen.cfunctions import isnan

import ProcessData
import ReadData
import DataStructures as data
import VisualizeData
import SaveData
import platform

if __name__ == "__main__":
    dt = datetime.datetime.now()
    cur_dt = dt.strftime("%Y-%m-%d_%H%M")
    Tk().withdraw()
    if not os.path.isdir("data_inputs"):
        filenames = askopenfilenames(title='Choose files',
                                     filetypes=(("Excel files", "*.xls*"),
                                                ("Text files", "*.txt*"),
                                                ("all files", "*.*")))
    else:
        dn = os.path.join(os.getcwd(), "data_inputs")
        filenames = []
        for file in os.listdir(dn):
            if file.endswith(".xls") or file.endswith(".xlsx"):
                filenames.append(os.path.join(dn, file))

    init_st_time = datetime.datetime.now()
    log_str = (f'Calculation start time: {init_st_time.strftime("%Y/%m/%d %H:%M:%S")}\n'
               f'System parameters:\n'
               f'  OS:        {platform.system()} ({platform.platform()})\n'
               f'  Processor: {platform.processor()} ({os.cpu_count()} cores)\n\n')
    if len(filenames) > 0:
        wd = os.path.join(os.path.dirname(os.path.realpath(filenames[0])), "results")
        if not os.path.isdir(wd):
            os.mkdir(wd)
        wd = os.path.join(wd, cur_dt)
        if not os.path.isdir(wd):
            os.mkdir(wd)
        for index, filename in enumerate(filenames, start=1):
            print(data.text.BOLD + f'File {filename}' + data.text.END)
            log_str += f'File {filename}\n'
            st_time = datetime.datetime.now()
            print(data.text.BOLD + f'File #{index}: calculation started at '
                                   f'{st_time.strftime("%Y/%m/%d %H:%M:%S")}\n' + data.text.END)
            log_str += f'Calculation started at {st_time.strftime("%Y/%m/%d %H:%M:%S")}\n'
            [is_ok, result] = ReadData.fromFile(wd, filename)
            if not is_ok:
                log_str += f'Calculation skipped: {result.message}\n\n'
                del result
                continue
            result = ProcessData.fromStructure(result)
            print(f'\n  Data visualization and saving started at '
                  f'{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
            VisualizeData.images(result)
            SaveData.fromDatLine(result)
            result.dependencies = VisualizeData.dependencies(result)
            SaveData.forDependencies(result)
            print(f'  Data visualization and saving finished at '
                  f'{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n')
            end_time = datetime.datetime.now()
            print(data.text.BOLD + f'File #{index}: calculation finished at '
                                   f'{end_time.strftime("%Y/%m/%d %H:%M:%S")}' + data.text.END)
            log_str += f'Calculation finished at {end_time.strftime("%Y/%m/%d %H:%M:%S")}\n'
            calc_time = end_time - st_time
            print(data.text.BOLD + f'File #{index}: calculation time is '
                                   f'{calc_time}' + data.text.END)
            log_str += f'Calculation time is {calc_time}\n\n'
            f = open(os.path.join(result.io.filedir, 'result.dat'), 'wb')
            pickle.dump(result, f, 2)
            f.close()
            del result

        init_end_time = datetime.datetime.now()
        log_str += f'Calculation finish time: {init_end_time.strftime("%Y/%m/%d %H:%M:%S")}'
        f = open(os.path.join(wd, 'result.log'), 'w')
        f.write(log_str)
        f.close()
