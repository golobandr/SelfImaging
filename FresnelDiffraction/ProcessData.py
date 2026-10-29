import datetime
import math
import Calculate
import DataStructures as data
import os
import concurrent.futures
import multiprocessing


def fromLine(idx_line, idl, copy_beam, copy_grating, copy_data):
    if idl.is_ok:
        idl.start = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f'  Line {idx_line + 1} processing started at {idl.start}')
        tmp_beam = idl.beam
        tmp_grating = idl.grating
        idl.beam.band = Calculate.beambandSpectrumIntensities(idl.beam,
                                                              math.sqrt(idl.psd.distance ** 2 + idl.psd.aperture ** 2))
        tmp_beam.band = idl.beam.band
        if copy_grating:
            tmp_grating.coefficients = copy_data.grating
        else:
            idl.grating.coefficients = Calculate.gratingCoefficients(idl.grating, idl.beam.band.wavelength,
                                                                     idl.add.accuracy)
            tmp_grating.coefficients = idl.grating.coefficients
        if copy_beam:
            tmp_beam.coefficients = copy_data.beam
        else:
            idl.beam.coefficients = Calculate.beamCoefficients(idl.beam, idl.add.accuracy)
            tmp_beam.coefficients = idl.beam.coefficients
        idl.psd.image = Calculate.outputDistribution(tmp_grating, tmp_beam, idl.psd)
        idl.end = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f'  Line {idx_line + 1} processing finished at {idl.end}')
    else:
        print(data.text.RED + f'  Line {idx_line + 1} processing skipped since input data is incorrect' +
              data.text.END)
    return {idx_line: idl}


def fromStructure(ipt):
    if ipt.copy_grating:
        ipt.copy_data.grating = Calculate.gratingCoefficients(ipt.data[0].grating, ipt.data[0].beam.wavelength,
                                                              ipt.data[0].add.accuracy)
    if ipt.copy_beam:
        ipt.copy_data.beam = Calculate.beamCoefficients(ipt.data[0].beam, ipt.data[0].add.accuracy)

    tmp_data = {}
    worker_count = min(len(ipt.data), max(1, (os.cpu_count() or 1) - 1))
    if worker_count <= 1:
        for idx, line in enumerate(ipt.data):
            tmp_data.update(fromLine(idx, line, ipt.copy_beam, ipt.copy_grating, ipt.copy_data))
    else:
        ctx = multiprocessing.get_context("spawn")
        chunk_size = max(1, math.ceil(len(ipt.data) / (worker_count * 4)))
        with concurrent.futures.ProcessPoolExecutor(max_workers=worker_count, mp_context=ctx) as executor:
            results = executor.map(
                fromLine,
                range(len(ipt.data)),
                ipt.data,
                [ipt.copy_beam] * len(ipt.data),
                [ipt.copy_grating] * len(ipt.data),
                [ipt.copy_data] * len(ipt.data),
                chunksize=chunk_size)
            for result in results:
                tmp_data.update(result)
    data = []
    for i in range(len(tmp_data)):
        data.append(tmp_data[i])

    ipt.data = data
    for idx in range(len(ipt.data)):
        if not ipt.data[idx].is_ok:
            ipt.is_ok = False
            break
    return ipt
