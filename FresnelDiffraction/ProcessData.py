import threading
import datetime
import Calculate
import DataStructures as data


def fromStructure(ipt):
    threads = []

    def fromLine(idx_line, idl):
        idl.start = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        tmp_beam = idl.beam
        tmp_grating = idl.grating
        if ipt.copy_beam_band:
            tmp_beam.band = ipt.copy_data.beamband
        else:
            idl.beam.band = Calculate.beambandSpectrumIntensities(idl.beam)
            tmp_beam.band = idl.beam.band
        if ipt.copy_grating:
            tmp_grating.coefficients = ipt.copy_data.grating
        else:
            idl.grating.coefficients = Calculate.gratingCoefficients(idl.grating, tmp_beam.band.wavelength,
                                                                     idl.add.accuracy)
            tmp_grating.coefficients = idl.grating.coefficients
        if ipt.copy_beam:
            tmp_beam.coefficients = ipt.copy_data.beam
        else:
            idl.beam.coefficients = Calculate.beamCoefficients(idl.beam, idl.psd.aperture, idl.add.accuracy)
            tmp_beam.coefficients = idl.beam.coefficients
        idl.psd.image = Calculate.outputDistribution(tmp_grating, tmp_beam, idl.psd)
        ipt.data[idx_line] = idl
        idl.end = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

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
            thread = threading.Thread(target=fromLine, args=(idx, ipt.data[idx]))
            thread.name = f'Line {idx + 1}'
            print(f'  {thread.name} processing started at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
            threads.append(thread)
            thread.start()
        else:
            print(data.text.RED + f'  Line {idx + 1} processing skipped since input data is incorrect' + data.text.END)
    # Wait for all threads to finish
    for thread in threads:
        print(f'  {thread.name} processing finished at {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
        thread.join()
    for idx in range(len(ipt.data)):
        if not ipt.data[idx].is_ok:
            ipt.is_ok = False
            break
    return ipt
