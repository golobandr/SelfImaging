import os
import datetime
import shutil
import DataStructures as data
import pandas as pd
import math


def createStructures(filename):
    def parseBeam(data_in):
        beam = data.Beam()
        if len(data_in[0]) < 1 or math.isnan(float(data_in[0][0])):
            return [False, beam, 'missing mandatory beam wavelength parameter']
        beam.wavelength = float(data_in[0][0]) * 1E-6
        if beam.wavelength <= 0:
            return [False, beam, 'beam wavelength must be greater than 0']
        waist = data.XYData()
        if len(data_in[1]) > 0 and not math.isnan(float(data_in[1][0])):
            waist.x = float(data_in[1][0]) * 2
        if len(data_in[2]) > 0 and not math.isnan(float(data_in[2][0])):
            waist.y = float(data_in[2][0]) * 2
        if waist.x < 0 or waist.y < 0:
            return [False, beam, 'beam waist must be greater than 0']
        beam.waist = waist
        aperture = data.XYData()
        if len(data_in[1]) > 1 and not math.isnan(float(data_in[1][1])):
            aperture.x = float(data_in[1][1])
        if len(data_in[2]) > 1 and not math.isnan(float(data_in[2][1])):
            aperture.y = float(data_in[2][1])
        if aperture.x < 0 or aperture.y < 0:
            return [False, beam, 'beam aperture must be greater than 0']
        beam.aperture = aperture
        angle = data.XYData()
        if len(data_in[1]) > 2 and not math.isnan(float(data_in[1][2])):
            angle.x = float(data_in[1][2]) * 1E-3
        if len(data_in[2]) > 2 and not math.isnan(float(data_in[2][2])):
            angle.y = float(data_in[2][2]) * 1E-3
        beam.angle = angle
        curvature = data.XYData()
        if len(data_in[1]) > 3 and not math.isnan(float(data_in[1][3])):
            curvature.x = float(data_in[1][3])
        if len(data_in[2]) > 3 and not math.isnan(float(data_in[2][3])):
            curvature.y = float(data_in[2][3])
        beam.curvature = curvature
        aberration = data.XYDataString()
        if len(data_in[1]) > 4 and (type(data_in[1][4]) == type('string')):
            aberration.x = str(data_in[1][4])
        if len(data_in[2]) > 4 and (type(data_in[2][4]) == type('string')):
            aberration.y = str(data_in[2][4])
        message = ''  # will be ignored if error apper
        if (aberration.x != '' and aperture.x == 0) or (aberration.y != '' and aperture.y == 0):
            message = 'aberration function is ignored since beam aperture is not set'
            if aberration.x != '' and aperture.x == 0:
                aberration.x = ''
            if aberration.y != '' and aperture.y == 0:
                aberration.y = ''
        beam.aberration = aberration
        if len(data_in[0]) < 2:
            return [True, beam, message]
        if not math.isnan(data_in[0][1]):
            beam.band = float(data_in[0][1]) / 100
        if beam.band < 0:
            return [False, beam, 'beam band must be greater than 0']
        if len(data_in[0]) < 3:
            return [True, beam, message]
        if not math.isnan(data_in[0][2]):
            beam.intensity = float(data_in[0][2])
        if beam.intensity < 0:
            return [False, beam, 'beam intensity must be greater than 0']
        return [True, beam, message]

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
        if len(data_in) < 5 and 'phase' in grating.slit:
            return [False, grating, 'missing mandatory data column for phase grating']
        if len(data_in) < 4:
            return [True, grating, '']
        grating.depth = float(data_in[3])
        if math.isnan(grating.depth):
            grating.depth = 0
        if len(data_in) < 5:
            return [True, grating, '']
        grating.index = [float(data_in[4]), 0]
        if math.isnan(grating.index[0]):
            grating.index = [1, 0]
        if wavelength == 0 and 'phase' in grating.slit:
            return [False, grating, 'grating phase depth calculation is impossible with zero wavelength']
        grating.phase_depth = 2 * math.pi * ((grating.index[0] - 1) * grating.depth / wavelength -
                                             round((grating.index[0] - 1) * grating.depth / wavelength))
        if len(data_in) < 6:
            return [True, grating, '']
        grating.index[1] = float(data_in[5])
        if math.isnan(grating.index[1]):
            grating.index[1] = 0
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
        b_warn = False
        if not b_ok or (b_ok and message_tmp != ''):
            message += message_tmp
            b_warn = True
        [g_ok, grating, message_tmp] = parseGrating(grating, beam.wavelength)
        if not g_ok:
            if not b_ok or b_warn:
                message += blank_line
            message += message_tmp
        [p_ok, psd, message_tmp] = parsePsd(psd)
        if not p_ok:
            if not g_ok or not b_ok or b_warn:
                message += blank_line
            message += message_tmp
        if not g_ok or not b_ok or not p_ok:
            print(data.text.RED + '    ' + message.replace('\n', '\n    ') + data.text.END)
        elif b_warn:
            print(data.text.BLUE + '    ' + message.replace('\n', '\n    ') + data.text.END)
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
    if 'Add' in xls.sheet_names:
        add = pd.read_excel(filename, sheet_name='Add', skiprows=0)
    else:
        add = []
    if 'Beam.X' in xls.sheet_names:
        beam_x = pd.read_excel(filename, sheet_name='Beam.X', skiprows=0)
    else:
        beam_x = []
    if 'Beam.Y' in xls.sheet_names:
        beam_y = pd.read_excel(filename, sheet_name='Beam.Y', skiprows=0)
    else:
        beam_y = []
    if (not len(add) == 0 and add.values.shape[0] != data_len) or \
            (not len(beam_x) == 0 and beam_x.values.shape[0] != data_len) or \
            (not len(beam_y) == 0 and beam_y.values.shape[0] != data_len):
        return [False, 'File: datafile structures are different. Please check input data.']
    ret_val = {}
    copy_grating = True
    copy_beam = True
    for idx in range(data_len):
        ret_val[idx] = parseDataLine(grating.values[idx],
                                     [beam.values[idx],
                                      beam_x.values[idx] if not len(beam_x) == 0 else [],
                                      beam_y.values[idx] if not len(beam_y) == 0 else []],
                                     psd.values[idx],
                                     add.values[idx] if not len(add) == 0 else [], idx)
        if idx > 0 and copy_grating:
            if 'phase' in grating.values[idx][0]:
                if list(grating.values[idx]) != list(grating.values[idx - 1]) or \
                        list(beam.values[idx])[0:2] != list(beam.values[idx - 1])[0:2]:
                    copy_grating = False
            elif list(grating.values[idx])[0:3] != list(grating.values[idx - 1])[0:3]:
                copy_grating = False
        if idx > 0 and copy_beam and len(beam_x) != 0 or len(beam_y) != 0:
            if psd.values[idx][1] != psd.values[idx - 1][1]:
                copy_beam = False
            else:
                if len(beam_x) >= 2 and beam_x.values[idx][1] != beam_x.values[idx - 1][1]:
                    copy_beam = False
                if len(beam_x) >= 5 and beam_x.values[idx][4] != beam_x.values[idx - 1][4]:
                    copy_beam = False
                if len(beam_y) >= 2 and beam_y.values[idx][1] != beam_y.values[idx - 1][1]:
                    copy_beam = False
                if len(beam_y) >= 5 and beam_y.values[idx][4] != beam_y.values[idx - 1][4]:
                    copy_beam = False
    dependencies = ''
    if 'Dependencies' in xls.sheet_names:
        dependencies = pd.read_excel(filename, sheet_name='Dependencies', skiprows=0).to_string()
    xls.close()
    return [True, [ret_val, dependencies, copy_grating, copy_beam]]


def fromFile(wd, filename):
    print(f'  Data reading started at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
    io = data.Io()
    io.date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    io.filedir = os.path.join(wd, os.path.splitext(os.path.basename(filename))[0])
    io.workdir = wd
    io.filename = os.path.basename(filename)
    io.outputfile = os.path.join(str(io.filedir), io.filename)
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
        rd.copy_grating = retval[2]
        rd.copy_beam = retval[3]
    else:
        is_ok = False
        rd.is_ok = False
        rd.message = 'Copy warning: file copy is not possible. Please check access rights.'
        print('    ' + data.text.RED + rd.message + data.text.END)
    print(f'  Data reading finished at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n')
    return [is_ok, rd]
