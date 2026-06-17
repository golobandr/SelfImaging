import numpy as np
import DataStructures as data
import math
import statistics
import scipy

width_init = 300
const_lightspeed = 299_792_458_000  # in mm/s


def beambandSpectrumIntensities(beam):
    beam_band = data.Spectrum()
    if beam.bandwidth == 0 and beam.pulse_time == 0:
        beam_band.wavelength = beam.wavelength * np.ones(1)
        beam_band.amplitude = np.ones(1)
        beam_band.delta = beam.wavelength
    else:
        delta_wl = beam.wavelength / 100
        beam_band.delta = delta_wl
        d_omega = max(beam.bandwidth,
                      beam.wavelength * beam.pulse_time / const_lightspeed * math.sqrt(1 + beam.chirp ** 2))
        wls_less = np.arange(beam.wavelength, beam.wavelength / (1 + 3 * d_omega) - delta_wl, -delta_wl)
        if 3 * d_omega >= 1:
            wls_more = np.arange(beam.wavelength, beam.wavelength * 100 + delta_wl, delta_wl)
        else:
            wls_more = np.arange(beam.wavelength, beam.wavelength / (1 - 3 * d_omega) + delta_wl, delta_wl)
        wls = np.sort(np.array(list(set(np.append(wls_less, wls_more)))))
        if np.min(wls) <= 0:
            wls = wls[wls > 0]
        if len(wls) == 1:
            wls = wls[0]
        beam_band.wavelength = wls
        if beam.pulse_time != 0:
            amplitude = np.exp(-(const_lightspeed * (beam.wavelength - wls) /
                                 (beam.pulse_time * beam.wavelength * wls)) ** 2 / (2 * (1 + 1j * beam.chirp)))
        else:
            amplitude = np.ones(len(wls))
        if beam.bandwidth != 0:
            amplitude *= np.exp(-((beam.wavelength / wls - 1) / beam.bandwidth) ** 2 / 2)
        intensity = amplitude ** 2
        beam_band.amplitude = amplitude / math.sqrt(sum(intensity))
    return beam_band


def beamCoefficients(beam, accuracy):
    def setCoef(beam_a, function, coord_letter):
        coef = data.Coefficients()
        if function != '':
            width = width_init
            coordinate = np.linspace(-0.5 / beam_a, 0.5 / beam_a, num=2 * width + 1, endpoint=False)
            function = function.replace(coord_letter, 'coordinate')
            phase = eval(function)
            am = np.fft.fftshift(np.fft.fft(np.exp(1j * phase)))
            [coef.n, coef.cn, coef.sn] = fourierCoefficientsUpdate(am, width, 1 / beam_a, accuracy / 100)
        return coef

    coefficients = data.Distribution2D()
    coefficients.x = setCoef(beam.aperture.x, beam.aberration.x, 'x')
    coefficients.y = setCoef(beam.aperture.y, beam.aberration.y, 'y')
    return coefficients


def fourierCoefficientsUpdate(cn, width, period, accuracy):
    def edgeCalculate(spectrum, accuracy):
        edges = 10 ** np.linspace(-20, 0, 21)
        [N, _] = np.histogram(spectrum, bins=edges)
        counts = N * edges[:len(N)]
        counts = counts / np.sum(counts)
        acc = np.zeros(len(counts))
        for i in range(len(N)):
            acc[i] = np.sum(counts[:i + 1])
        index = 0
        for i in range(len(N) - 2, 1, -1):
            if acc[i] < accuracy and sum(N[i:]) > 20:
                index = i
                break
        edge = edges[index]
        return edge

    f = np.linspace(-width, width, 2 * width + 1)
    spectrum = np.abs(cn) ** 2
    cn = cn / np.sqrt(np.sum(spectrum))
    spectrum = spectrum / np.max(spectrum)
    edge = edgeCalculate(spectrum, accuracy)
    cn_u = np.zeros(len(cn), dtype=complex)
    f_u = np.zeros(len(cn))
    s_u = np.zeros(len(cn))
    i = 0
    for n in range(len(f)):
        if spectrum[n] > edge:
            f_u[i] = f[n]
            cn_u[i] = cn[n]
            s_u[i] = spectrum[n]
            i += 1
    f_u = f_u[:i] / period
    cn_u = cn_u[:i]
    s_u = s_u[:i]
    return [f_u, cn_u, s_u]


def gratingCoefficients(grating, wl, accuracy):
    def rect(x):
        y = np.zeros(len(x))
        for i in range(len(x)):
            if abs(x[i]) <= 0.5:
                y[i] = 1
        return y

    def lens(x, r):
        y = np.sqrt(r ** 2 - x ** 2)
        y = y - y[0]
        return -y

    def fourierReCoefficients(grating):
        width = width_init
        if 'delta' in grating.slit:
            cn_re = np.ones(2 * width + 1) / (2 * width + 1)
        elif 'cos' in grating.slit:
            width = 1
            cn_re = 0.5 * np.ones(2 * width + 1)
            cn_re[width] = 1
        else:
            n = np.linspace(-width, width, 2 * width + 1)
            cn_re = grating.duty_factor * np.sinc(n * grating.duty_factor)
        return cn_re, width

    def fourierComplexCoefficients(grating):
        width = width_init
        x = np.linspace(-grating.period / 2, grating.period / 2, num=2 * width + 1, endpoint=False)
        if 'cos' in grating.slit:
            phase = np.cos(2 * np.pi / grating.period * x)
        elif 'lens' in grating.slit:
            lens_r = grating.depth + grating.period ** 2 / (4 * grating.depth)
            phase = lens(x, lens_r)
        else:
            phase = rect(x / (grating.period * grating.duty_factor))
        pit = np.exp(1j * grating.phase_depth * phase)
        cn = np.fft.fftshift(np.fft.fft(np.fft.fftshift(pit)))
        return cn, width

    def setCoefficientsForWL(tmp_grating):
        if not 'phase' in tmp_grating.slit:
            [cn, width] = fourierReCoefficients(grating)
        else:
            [cn, width] = fourierComplexCoefficients(tmp_grating)
        cn = cn / math.sqrt(sum(np.abs(cn) ** 2))
        coef = data.Coefficients()
        [coef.n, coef.cn, coef.sn] = fourierCoefficientsUpdate(cn, width, tmp_grating.period, accuracy)
        ret_val = data.Distribution2D()
        ret_val.x = coef
        if '1D' in tmp_grating.slit:
            ret_val.y = data.Coefficients()
        else:
            ret_val.y = coef
        return ret_val

    if not 'phase' in grating.slit or type(wl) != type(np.zeros(1)):
        return setCoefficientsForWL(grating)
    else:
        opt_coeff = []
        for wavelength in wl:
            if math.isnan(grating.index[1]):
                pd = (grating.index[0] - 1) * grating.depth / wavelength
            else:
                pd = (grating.index[0] + grating.index[1] * wavelength - 1) * grating.depth / wavelength
            grating.phase_depth = 2 * math.pi * pd
            opt_coeff.append(setCoefficientsForWL(grating))
        return opt_coeff


def outputDistribution(grating, beam, psd):
    def diffraction1DAtZeroDistance(n, cn, waist, a, x):
        u = np.zeros(len(x), dtype=complex)
        y = 1j * 2 * math.pi * x
        a_max = max(x)
        if a != 0:
            a_max = 1 / (2 * a)
        for i in range(len(x)):
            if abs(x[i]) <= a_max:
                for k in range(len(n)):
                    u[i] += cn[k] * np.exp(-y[i] * n[k])
        u = u * np.exp(-(x * waist) ** 2 / 2)
        return u

    def averagePixel(intensity, x, sd):
        if intensity.shape == x.shape:
            distribution = data.Distribution()
            int_out = np.zeros(len(x))
            for i in range(len(x)):
                int_out[i] = statistics.mean(intensity[i * sd:(i + 1) * sd])
        else:
            distribution = data.TimeDistribution()
            int_out = np.zeros((len(x), intensity.shape[1]))
            for j in range(intensity.shape[1]):
                for i in range(len(x)):
                    int_out[i, j] = statistics.mean(intensity[i * sd:(i + 1) * sd, j])
        distribution.coordinate = x
        distribution.intensity = int_out
        return distribution

    def diffraction1D(n, cn, m, am, wl, angle, waist, wfc, a, distance, x):
        b = 1 / (waist ** 2 / 2 + 1j * math.pi * (wfc + 1 / distance) / wl)
        bs = 1 / np.sqrt(b)
        x = -(x / distance + 0.5 * math.sin(angle)) / wl
        u = np.zeros(len(x), dtype=complex)
        for i in range(len(x)):
            for j in range(len(m)):
                for k in range(len(n)):
                    c = 1j * math.pi * (x[i] + n[k] + m[j])
                    exp_a = np.exp(b * c ** 2) * cn[k] * am[j]
                    if a != 0:
                        cb = c * b
                        exp_a *= 0.5 * (scipy.special.erf(bs * (1 / (2 * a) - cb)) +
                                        scipy.special.erf(bs * (1 / (2 * a) + cb)))
                    u[i] += exp_a
        return u

    def spectralDiffraction1D(bba, n, cn, m, am, wl, angle, waist, wfc, a, distance, x):
        swl = np.exp(1j * 2 * math.pi * distance / wl) * \
              np.sqrt(2 * math.pi / (2 * math.pi * (1 + distance * wfc) + 1j * wl * distance * waist ** 2))
        if distance == 0:
            u = swl * bba * diffraction1DAtZeroDistance(n, cn, waist, a, x)
        else:
            u = swl * bba * diffraction1D(n, cn, m, am, wl, angle, waist, wfc, a, distance, x)
        return u

    pts = round(psd.aperture // psd.step) + 1
    psd.aperture = psd.step * pts
    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, round(pts * psd.div_factor))
    intensity_x = np.zeros(len(x))
    intensity_y = np.zeros(len(x))
    if type([]) != type(grating.coefficients):
        nx, cnx = grating.coefficients.x.n, grating.coefficients.x.cn
        ny, cny = grating.coefficients.y.n, grating.coefficients.y.cn
    else:
        nx, cnx = grating.coefficients[0].x.n, grating.coefficients[0].x.cn
        ny, cny = grating.coefficients[0].y.n, grating.coefficients[0].y.cn
    if psd.time != 0:
        amplitude_x = np.zeros((len(x), len(beam.band.wavelength)), dtype=complex)
        amplitude_y = np.zeros((len(x), len(beam.band.wavelength)), dtype=complex)
    else:
        amplitude_x = 0
        amplitude_y = 0
    for i in range(len(beam.band.wavelength)):
        if type([]) == type(grating.coefficients):
            nx, cnx = grating.coefficients[i].x.n, grating.coefficients[i].x.cn
            ny, cny = grating.coefficients[i].y.n, grating.coefficients[i].y.cn
        ax = spectralDiffraction1D(beam.band.amplitude[i], nx, cnx, beam.coefficients.x.n, beam.coefficients.x.cn,
                                   beam.band.wavelength[i], beam.angle.x, beam.waist.x, beam.curvature.x,
                                   beam.aperture.x, psd.distance, x)
        ay = spectralDiffraction1D(beam.band.amplitude[i], ny, cny, beam.coefficients.y.n, beam.coefficients.y.cn,
                                   beam.band.wavelength[i], beam.angle.y, beam.waist.x, beam.curvature.y,
                                   beam.aperture.y, psd.distance, x)
        intensity_x += np.abs(ax) ** 2
        intensity_y += np.abs(ay) ** 2
        if psd.time != 0:
            amplitude_x[:, i] = ax[:]
            amplitude_y[:, i] = ay[:]
    if psd.time != 0:
        time = np.arange(0, psd.time, psd.time_step)
        utx = np.zeros((len(x), len(time)), dtype=complex)
        uty = np.zeros((len(x), len(time)), dtype=complex)
        omega = 2 * math.pi * const_lightspeed / beam.band.wavelength
        for j in range(len(time)):
            for i in range(len(omega)):
                exp_wt = np.exp(-1j * omega[i] * time[j])
                utx[:, j] += exp_wt * amplitude_x[:, i]
                uty[:, j] += exp_wt * amplitude_y[:, i]
        itx = np.abs(utx) ** 2
        ity = np.abs(uty) ** 2
    else:
        itx = 0
        ity = 0
        time = 0
    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, pts)
    if psd.time != 0:
        intensity = data.Distribution2DTime()
    else:
        intensity = data.Distribution2D()
    intensity.x = averagePixel(intensity_x, x, round(psd.div_factor))
    intensity.y = averagePixel(intensity_y, x, round(psd.div_factor))
    if psd.time != 0:
        i = data.Distribution2D()
        i.x = averagePixel(itx, x, round(psd.div_factor))
        i.x.time = time
        i.y = averagePixel(ity, x, round(psd.div_factor))
        i.y.time = time
        intensity.t = i
    return intensity
