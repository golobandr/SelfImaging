import os
import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import pickle
import ProcessData
import ReadData
import DataStructures as data
import VisualizeData
import SaveData

dt = datetime.datetime.now()
cur_dt = dt.strftime("%Y-%m-%d_%H%M")
Tk().withdraw()
filenames = askopenfilenames(title='Choose files',
                             filetypes=(("Excel files", "*.xls*"),
                                        ("Text files", "*.txt*"),
                                        ("all files", "*.*")))
if len(filenames) > 0:
    wd = os.path.join(os.path.dirname(os.path.realpath(filenames[0])), "results")
    if not os.path.isdir(wd):
        os.mkdir(wd)
    wd = os.path.join(wd, cur_dt)
    if not os.path.isdir(wd):
        os.mkdir(wd)
    results = {}
    for index, filename in enumerate(filenames, start=1):
        print(data.text.BOLD + f'File {filename}' + data.text.END)
        print(data.text.BOLD + f'File #{index}: calculation started at '
                               f'{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n' + data.text.END)
        [is_ok, result] = ReadData.fromFile(wd, filename)
        if not is_ok:
            results[result.io.filename] = result
            continue
        result = ProcessData.fromStructure(result)
        print(f'\n  Data visualization and saving started at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
        VisualizeData.images(result)
        SaveData.fromDatLine(result)
        result.dependencies = VisualizeData.dependencies(result)
        SaveData.forDependencies(result)
        print(f'  Data visualization and saving finished at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n')
        print(data.text.BOLD + f'File #{index}: calculation finished at '
                               f'{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}' + data.text.END)
        results[result.io.filename] = result
    # f = open(os.path.join(wd, 'result.dat'), 'wb')
    # pickle.dump(results, f, 2)
    # f.close()
