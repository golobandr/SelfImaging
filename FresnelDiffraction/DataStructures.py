import numpy as np


class Beam:
    intensity = 0
    waist = None
    curvature = None
    angle = None
    wavelength = None
    aperture = None
    bandwidth = 0
    band = None
    aberration = None
    coefficients = None
    pulse_time = 0
    chirp = 0


class Grating:
    slit = "1D, square"
    period = None
    depth = None
    index = None
    duty_factor = None
    phase_depth = None
    coefficients = None


class Coefficients:
    n = np.zeros(1)
    cn = np.ones(1)
    sn = np.ones(1)
    wavelength = 0


class Distribution:
    coordinate = None
    intensity = None


class TimeDistribution:
    time = None
    coordinate = None
    intensity = None


class Spectrum:
    wavelength = np.ones(1)
    amplitude = np.ones(1, dtype=complex)
    delta = None


class Distribution2D:
    x = None
    y = None


class Distribution2DTime:
    x = None
    y = None
    t = None


class XYData:
    x = 0
    y = 0


class XYDataString:
    x = ''
    y = ''


class Psd:
    distance = None
    aperture = None
    step = None
    div_factor = 1
    image = None
    time = 0
    timestep = 0


class Add:
    accuracy = 0.005
    dependency = 0
    debug = False
    save = False


class Io:
    date = None
    filedir = None
    workdir = None
    filename = 0
    outputfile = None


class CopyData:
    grating = None
    beam = None
    beamband = None


class OutputData:
    is_ok = True
    message = ''
    data = None
    io = None
    dependencies = None
    copy_grating = False
    copy_beam = False
    copy_beam_band = False
    copy_data = CopyData()


class OutputDataLine:
    is_ok = True
    message = ''
    beam = None
    grating = None
    psd = None
    dependencies = None
    start = None
    end = None


class text:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
