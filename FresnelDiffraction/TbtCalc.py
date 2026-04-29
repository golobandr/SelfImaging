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

    if len(filenames) > 0:
        wd = os.path.join(os.path.dirname(os.path.realpath(filenames[0])), "results")
        if not os.path.isdir(wd):
            os.mkdir(wd)
        wd = os.path.join(wd, cur_dt)
        if not os.path.isdir(wd):
            os.mkdir(wd)
        for index, filename in enumerate(filenames, start=1):
            print(data.text.BOLD + f'File {filename}' + data.text.END)
            st_time = datetime.datetime.now()
            print(data.text.BOLD + f'File #{index}: calculation started at '
                                   f'{st_time.strftime("%Y/%m/%d %H:%M:%S")}\n' + data.text.END)
            [is_ok, result] = ReadData.fromFile(wd, filename)
            if not is_ok:
                continue
            result = ProcessData.fromStructure(result)
            print(f'\n  Data visualization and saving started at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
            VisualizeData.images(result)
            SaveData.fromDatLine(result)
            result.dependencies = VisualizeData.dependencies(result)
            SaveData.forDependencies(result)
            print(f'  Data visualization and saving finished at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n')
            end_time = datetime.datetime.now()
            print(data.text.BOLD + f'File #{index}: calculation finished at '
                                   f'{end_time.strftime("%Y/%m/%d %H:%M:%S")}' + data.text.END)
            calc_time = end_time - st_time
            print(data.text.BOLD + f'File #{index}: calculation time is '
                                   f'{calc_time}' + data.text.END)

            f = open(os.path.join(result.io.filedir, 'result.dat'), 'wb')
            pickle.dump(result, f, 2)
            f.close()
            del result
