import os
import datetime
import shutil
import DataStructures as data
import pandas as pd
import math


def createStructures(filename):
    def parseBeam(data_in):
        beam = data.Beam()
        if len(data_in) < 7:
            return [False, beam, 'missing mandatory beam data column']
        angle = data.Distribution2D()
        angle.x = float(data_in[0]) * 1E-3
        if math.isnan(angle.x):
            angle.x = 0
        angle.y = float(data_in[3]) * 1E-3
        if math.isnan(angle.y):
            angle.y = 0
        beam.angle = angle
        curvature = data.Distribution2D()
        curvature.x = float(data_in[1])
        if math.isnan(curvature.x):
            curvature.x = 0
        curvature.y = float(data_in[4])
        if math.isnan(curvature.y):
            curvature.y = 0
        beam.curvature = curvature
        waist = data.Distribution2D()
        waist.x = float(data_in[2])
        waist.y = float(data_in[5])
        if math.isnan(waist.x):
            waist.x = 0
        if math.isnan(waist.y):
            waist.y = 0
        if waist.x < 0 or waist.y < 0:
            return [False, beam, 'beam waist must be greater than 0']
        beam.waist = waist
        beam.wavelength = float(data_in[6]) * 1E-6
        if math.isnan(beam.wavelength):
            return [False, beam, 'missing mandatory beam wavelength parameter']
        if beam.wavelength <= 0:
            return [False, beam, 'beam wavelength must be greater than 0']
        if len(data_in) < 8:
            return [True, beam, '']
        beam.band = float(data_in[7]) / 100
        if math.isnan(beam.band):
            beam.band = 0
        if len(data_in) < 8:
            return [True, beam, '']
        beam.intensity = float(data_in[8])
        if math.isnan(beam.intensity):
            beam.intensity = 1
        return [True, beam, '']

    def parseGrating(data_in, wavelength):
        grating = data.Grating()
        if len(data_in) < 3:
            return [False, grating, 'missing mandatory grating data column']
        grating.slit = data_in[0]
        grating.period = float(data_in[1]) * 1E-3
        if math.isnan(grating.period):
            return [False, grating, 'missing mandatory grating period parameter']
        if grating.period <= 0:
            return [False, grating, 'grating period must be greater than 0']
        grating.duty_factor = float(data_in[2])
        if math.isnan(grating.duty_factor):
            grating.duty_factor = 0
        if grating.duty_factor < 0 or grating.duty_factor > 1:
            return [False, grating, 'grating duty factor must be within [0, 1]']
        if grating.duty_factor == 0 and 'square' in grating.slit:
            grating.slit = grating.slit.replace('square', 'delta')
        if 'square' in grating.slit and grating.duty_factor == 0:
            grating.slit.replace('square', 'delta')
        if len(data_in) < 6 and 'phase' in grating.slit:
            return [False, grating, 'missing mandatory data column for phase grating']
        if len(data_in) < 4:
            return [True, grating, '']
        grating.aperture = float(data_in[3])
        if math.isnan(grating.aperture):
            grating.aperture = 0
        if grating.aperture < 0:
            return [False, grating, 'grating aperture must be greater than 0']
        if len(data_in) < 5:
            return [True, grating, '']
        grating.depth = float(data_in[4])
        if math.isnan(grating.depth):
            grating.depth = 0
        if len(data_in) < 6:
            return [True, grating, '']
        grating.index = [float(data_in[5]), 0]
        if math.isnan(grating.index[0]):
            grating.index = [0, 0]
        if wavelength == 0 and 'phase' in grating.slit:
            return [False, grating, 'grating phase depth calculation is impossible with zero wavelength']
        grating.phase_depth = 2 * math.pi * ((grating.index[0] - 1) * grating.depth / wavelength -
                                             round((grating.index[0] - 1) * grating.depth / wavelength))
        return [True, grating, '']

    def parsePsd(data_in):
        psd = data.Psd()
        if len(data_in) < 3:
            return [False, psd, 'missing mandatory psd data column']
        psd.distance = float(data_in[0])
        if math.isnan(psd.distance):
            return [False, psd, 'missing mandatory psd distance parameter']
        if psd.distance < 0:
            return [False, psd, 'psd distance must be greater than 0']
        psd.aperture = float(data_in[1])
        if math.isnan(psd.aperture):
            return [False, psd, 'missing mandatory psd aperture parameter']
        if psd.aperture <= 0:
            return [False, psd, 'psd aperture must be greater than 0']
        psd.step = float(data_in[2]) * 1E-3
        if math.isnan(psd.step):
            return [False, psd, 'missing mandatory psd lateral step parameter']
        if psd.step <= 0:
            return [False, psd, 'psd lateral step must be greater than 0']
        if psd.aperture < psd.step:
            return [False, psd, 'psd lateral step must be less than psd aperture']
        if len(data_in) < 4:
            return [True, psd, '']
        psd.div_factor = round(data_in[3])
        if math.isnan(psd.div_factor):
            psd.div_factor = 1
        if psd.div_factor < 1:
            return [False, psd, 'psd div factor must be greater than 1']
        return [True, psd, '']

    def parseAdd(data_in):
        add = data.Add()
        if len(data_in) == 0:
            return add
        if len(data_in) > 0:
            add.accuracy = float(data_in[0])
        if len(data_in) > 1:
            add.debug = 'Y' in data_in[1]
        if len(data_in) > 2:
            add.save = 'Y' in data_in[2]
        return add

    def parseDataLine(grating, beam, psd, add, idx):
        message = f'Line {idx + 1} '
        blank_line = '\n'.ljust(len(message) + len('\n'))
        [b_ok, beam, message_tmp] = parseBeam(beam)
        if not b_ok:
            message += message_tmp
        [g_ok, grating, message_tmp] = parseGrating(grating, beam.wavelength)
        if not g_ok:
            if not b_ok:
                message += blank_line
            message += message_tmp
        [p_ok, psd, message_tmp] = parsePsd(psd)
        if not p_ok:
            if not g_ok or not b_ok:
                message += blank_line
            message += message_tmp
        if not g_ok or not b_ok or not p_ok:
            print(data.text.RED + '    ' + message.replace('\n', '\n    ') + data.text.END)
        else:
            message = ''
        add = parseAdd(add)
        rd = data.OutputDataLine()
        rd.is_ok = g_ok and b_ok and p_ok
        rd.psd = psd
        rd.add = add
        rd.message = message
        rd.grating = grating
        rd.beam = beam
        return rd

    xls = pd.ExcelFile(filename)
    if 'Grating' not in xls.sheet_names or 'Beam' not in xls.sheet_names or 'Psd' not in xls.sheet_names:
        return [False, 'File: datafile structure is incorrect. Please check input data structures.']
    grating = pd.read_excel(filename, sheet_name='Grating', skiprows=0)
    beam = pd.read_excel(filename, sheet_name='Beam', skiprows=0)
    psd = pd.read_excel(filename, sheet_name='Psd', skiprows=0)
    if grating.empty or beam.empty or psd.empty:
        return [False, 'File: datafile structure is empty. Please check input data.']
    if (grating.values.shape[0] != beam.values.shape[0] or
            beam.values.shape[0] != psd.values.shape[0] or
            psd.values.shape[0] != grating.values.shape[0]):
        return [False, 'File: datafile structures are different. Please check input data.']
    data_len = grating.values.shape[0]
    add = []
    if 'Add' in xls.sheet_names:
        add = pd.read_excel(filename, sheet_name='Add', skiprows=0)
        if add.empty or add.values.shape[0] != data_len:
            return [False, 'File: datafile structures are different. Please check input data.']
    ret_val = {}
    for idx in range(data_len):
        if 'Add' in xls.sheet_names:
            ret_val[idx] = parseDataLine(grating.values[idx], beam.values[idx], psd.values[idx], add.values[idx], idx)
        else:
            ret_val[idx] = parseDataLine(grating.values[idx], beam.values[idx], psd.values[idx], add, idx)
    if 'Dependencies' in xls.sheet_names:
        dependencies = pd.read_excel(filename, sheet_name='Dependencies', skiprows=0).to_string()
        xls.close()
        return [True, [ret_val, dependencies]]
    else:
        xls.close()
        return [True, [ret_val, '']]


def fromFile(wd, filename):
    print(f'  Data reading started at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
    io = data.Io()
    io.date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    io.filedir = os.path.join(wd, os.path.splitext(os.path.basename(filename))[0])
    io.workdir = wd
    io.filename = os.path.basename(filename)
    io.outputfile = os.path.join(io.filedir, io.filename)
    if not os.path.isdir(io.filedir):
        os.mkdir(io.filedir)
    dest = shutil.copy(filename, io.outputfile)
    rd = data.OutputData()
    rd.io = io
    if dest == io.outputfile:
        [is_ok, retval] = createStructures(io.outputfile)
        if not is_ok:
            rd.is_ok = is_ok
            rd.message = retval
            print('    ' + data.text.RED + rd.message + data.text.END)
        rd.data = retval[0]
        rd.dependencies = retval[1]
    else:
        is_ok = False
        rd.is_ok = False
        rd.message = 'Copy warning: file copy is not possible. Please check access rights.'
        print('    ' + data.text.RED + rd.message + data.text.END)
    print(f'  Data reading finished at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n')
    return [is_ok, rd]
