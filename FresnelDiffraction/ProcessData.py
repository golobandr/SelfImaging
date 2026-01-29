import threading
import datetime
import Calculate
import DataStructures as data
import DisplayData


def fromStructure(ipt):
    threads = []

    def fromLine(idx, idl):
        idl.start = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        idl.grating.coefficients = Calculate.gratingCoefficients(idl.grating, idl.add.accuracy)
        idl.beam.coefficients = Calculate.beamCoefficients(idl.beam, idl.psd.aperture, idl.add.accuracy)
        idl.psd.image = Calculate.outputDistribution(idl.grating, idl.beam, idl.psd)
        ipt.data[idx] = idl
        idl.end = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

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
