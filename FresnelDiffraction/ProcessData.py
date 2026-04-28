import threading
import datetime
import Calculate
import DataStructures as data


def fromLine(idx, idl, copy_beam_band, copy_beam, copy_grating, copy_data):
    idl.start = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f'  Line {idx + 1} processing started at {idl.start}')
    tmp_beam = idl.beam
    tmp_grating = idl.grating
    if copy_beam_band:
        tmp_beam.band = copy_data.beamband
    else:
        idl.beam.band = Calculate.beambandSpectrumIntensities(idl.beam)
        tmp_beam.band = idl.beam.band
    if copy_grating:
        tmp_grating.coefficients = copy_data.grating
    else:
        idl.grating.coefficients = Calculate.gratingCoefficients(idl.grating, tmp_beam.band.wavelength,
                                                                 idl.add.accuracy)
        tmp_grating.coefficients = idl.grating.coefficients
    if copy_beam:
        tmp_beam.coefficients = copy_data.beam
    else:
        idl.beam.coefficients = Calculate.beamCoefficients(idl.beam, idl.psd.aperture, idl.add.accuracy)
        tmp_beam.coefficients = idl.beam.coefficients
    idl.psd.image = Calculate.outputDistribution(tmp_grating, tmp_beam, idl.psd)
    idl.end = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f'  Line {idx + 1} processing finished at {idl.end}')
    return idl


def fromStructure(ipt):
    if ipt.copy_beam_band:
        ipt.copy_data.beamband = Calculate.beambandSpectrumIntensities(ipt.data[0].beam)
    if ipt.copy_grating:
        ipt.copy_data.grating = Calculate.gratingCoefficients(ipt.data[0].grating, ipt.copy_data.beamband.wavelength,
                                                              ipt.data[0].add.accuracy)
    if ipt.copy_beam:
        ipt.copy_data.beam = Calculate.beamCoefficients(ipt.data[0].beam, ipt.data[0].psd.aperture,
                                                        ipt.data[0].add.accuracy)
    for idx in range(len(ipt.data)):
        if ipt.data[idx].is_ok:
            ipt.data[idx] = fromLine(idx, ipt.data[idx], ipt.copy_beam_band, ipt.copy_beam, ipt.copy_grating,
                                     ipt.copy_data)
        else:
            print(data.text.RED + f'  Line {idx + 1} processing skipped since input data is incorrect' + data.text.END)
    for idx in range(len(ipt.data)):
        if not ipt.data[idx].is_ok:
            ipt.is_ok = False
            break
    return ipt
