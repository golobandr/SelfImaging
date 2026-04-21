import threading
import datetime
import Calculate
import DataStructures as data
import DisplayData


def fromStructure(ipt):
    threads = []
    grating_coefficients = 0
    beam_coefficients = 0

    def fromLine(idx, idl):
        idl.start = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if ipt.copy_grating:
            idl.grating.coefficients = grating_coefficients
        else:
            idl.grating.coefficients = Calculate.gratingCoefficients(idl.grating, idl.add.accuracy)
        if ipt.copy_beam:
            idl.beam.coefficients = beam_coefficients
        else:
            idl.beam.coefficients = Calculate.beamCoefficients(idl.beam, idl.psd.aperture, idl.add.accuracy)
        idl.psd.image = Calculate.outputDistribution(idl.grating, idl.beam, idl.psd)
        ipt.data[idx] = idl
        idl.end = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    if ipt.copy_grating:
        grating_coefficients = Calculate.gratingCoefficients(ipt.data[0].grating, ipt.data[0].add.accuracy)
    if ipt.copy_beam:
        beam_coefficients = Calculate.beamCoefficients(ipt.data[0].beam, ipt.data[0].psd.aperture,
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
