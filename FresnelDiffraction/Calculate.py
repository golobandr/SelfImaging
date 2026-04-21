import numpy as np
import DataStructures as data
import math
import statistics

width_init = 300


def beambandSpectrumCoefficients(beam):
    beam_band = data.Spectrum()
    if beam.bandwidth == 0:
        beam_band.wavelength = beam.wavelength
        beam_band.intensity = 1
    else:
        delta_wl = beam.wavelength / 100
        wls_less = np.arange(beam.wavelength, beam.wavelength / (1 + 3 * beam.bandwidth) - delta_wl, -delta_wl)
        wls_more = np.arange(beam.wavelength, beam.wavelength / (1 - 3 * beam.bandwidth) + delta_wl, delta_wl)
        wls = np.sort(np.array(list(set(np.append(wls_less, wls_more)))))
        beam_band.wavelength = wls
        beam_band.intensity = np.exp(-((wls - beam.wavelength) / (wls * beam.bandwidth)) ** 2)
        beam_band.intensity = beam_band.intensity / sum(beam_band.intensity)
    return beam_band


def beamCoefficients(beam, aperture, accuracy):
    def setCoef(beam_a, a, function, coord_letter):
        coef = data.Coefficients()
        if beam_a != 0:
            width = width_init
            if 1 / beam_a > a:
                period = 20 / beam_a
            else:
                period = 20 * a
            coordinate = np.linspace(-period / 2, period / 2, num=2 * width + 1, endpoint=False)
            profile = np.zeros(2 * width + 1)
            for i in range(len(profile)):
                profile[i] = 0 if abs(coordinate[i]) > 1 / (2 * beam_a) else 1
            profile = profile / sum(profile)
            if function != '':
                function = function.replace(coord_letter, 'coordinate')
                phase = eval(function)
                profile = profile * np.exp(1j * phase)
            am = np.fft.fftshift(np.fft.fft(np.fft.fftshift(profile)))
            [coef.n, coef.cn, coef.sn] = fourierCoefficientsUpdate(am, width, period, accuracy)
        return coef

    coefficients = data.Distribution2D()
    coefficients.x = setCoef(beam.aperture.x, aperture, beam.aberration.x, 'x')
    coefficients.y = setCoef(beam.aperture.y, aperture, beam.aberration.y, 'y')
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


def gratingCoefficients(grating, accuracy):
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
        if 'cos' in grating.slit:
            width = width_init
            x = np.linspace(-grating.period / 2, grating.period / 2, num=2 * width + 1, endpoint=False)
            phase = grating.phase_depth * np.cos(2 * np.pi / grating.period * x)
            pit_re = np.cos(phase)
            pit_im = np.sin(phase)
            pit = pit_re + 1j * pit_im
            cn = np.fft.fftshift(np.fft.fft(np.fft.fftshift(pit)))
        else:
            tmp_grating = data.Grating()
            tmp_grating.period = grating.period
            tmp_grating.duty_factor = 1
            [cn_one, _] = fourierReCoefficients(tmp_grating)
            [cn_pit, width] = fourierReCoefficients(grating)
            cn = cn_one + (np.exp(1j * grating.phase_depth) - 1) * cn_pit
        return cn, width

    if not 'phase' in grating.slit:
        [cn, width] = fourierReCoefficients(grating)
    else:
        [cn, width] = fourierComplexCoefficients(grating)
    cn = cn / math.sqrt(sum(np.abs(cn) ** 2))
    coef = data.Coefficients()
    [coef.n, coef.cn, coef.sn] = fourierCoefficientsUpdate(cn, width, grating.period, accuracy)
    ret_val = data.Distribution2D()
    ret_val.x = coef
    if '1D' in grating.slit:
        ret_val.y = data.Coefficients()
    else:
        ret_val.y = coef
    return ret_val


def outputDistribution(grating, beam, psd):
    def diffraction1DAtZeroDistance(n, cn, m, am, waist, x):
        u = np.zeros(len(x), dtype=complex)
        y = 1j * 2 * math.pi * x
        for i in range(len(x)):
            for j in range(len(m)):
                for k in range(len(n)):
                    u[i] += cn[k] * am[j] * np.exp(-y[i] * (n[k] + m[j]))
        u = u * np.exp(-(x * waist) ** 2 / 2)
        return np.abs(u) ** 2

    def averagePixel(intensity, x, sd):
        distribution = data.Distribution()
        distribution.coordinate = x
        int_out = np.zeros(len(x))
        for i in range(len(x)):
            int_out[i] = statistics.mean(intensity[i * sd:(i + 1) * sd])
        distribution.intensity = int_out
        return distribution

    def diffraction1D(n, cn, m, am, wl, angle, waist, wfc, distance, x):
        a = ((math.pi ** 2 * 2 * wl * distance) /
             complex(wl * distance * waist ** 2, -2 * math.pi * (1 + wfc * distance)))
        x = -1 / (wl * distance) * x - math.sin(angle) / (2 * wl)
        u = np.zeros(len(x), dtype=complex)
        for i in range(len(x)):
            for j in range(len(m)):
                for k in range(len(n)):
                    exp_a = np.exp(-a * (x[i] + n[k] + m[j]) ** 2)
                    u[i] += exp_a * cn[k] * am[j]
        return np.abs(u) ** 2

    pts = round(psd.aperture // psd.step) + 1
    psd.aperture = psd.step * pts
    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, round(pts * psd.div_factor))
    if psd.distance > 0:
        if beam.bandwidth == 0:
            intensity_x = diffraction1D(grating.coefficients.x.n, grating.coefficients.x.cn,
                                        beam.coefficients.x.n, beam.coefficients.x.cn,
                                        beam.wavelength, beam.angle.x, beam.waist.x, beam.curvature.x, psd.distance, x)
            intensity_y = diffraction1D(grating.coefficients.y.n, grating.coefficients.y.cn,
                                        beam.coefficients.y.n, beam.coefficients.y.cn,
                                        beam.wavelength, beam.angle.y, beam.waist.y, beam.curvature.y, psd.distance, x)
        else:
            intensity_x = np.zeros(len(x))
            intensity_y = np.zeros(len(x))
            for i in range(len(beam.band.wavelength)):
                # s_wl = beam.band.intensity[i] * \
                #        np.abs(np.sqrt(2 * math.pi /
                #                       complex(2 * math.pi * (1 + psd.distance * beam.curvature.x),
                #                               beam.band.wavelength[i] * psd.distance * beam.waist.x ** 2))) ** 2
                intensity_tmp = diffraction1D(grating.coefficients.x.n, grating.coefficients.x.cn,
                                              beam.coefficients.x.n, beam.coefficients.x.cn,
                                              beam.band.wavelength[i], beam.angle.x, beam.waist.x, beam.curvature.x,
                                              psd.distance, x)
                intensity_x += beam.band.intensity[i] * intensity_tmp
                # s_wl = beam.band.intensity[i] * \
                #        np.abs(np.sqrt(2 * math.pi /
                #                       complex(2 * math.pi * (1 + psd.distance * beam.curvature.y),
                #                               beam.band.wavelength[i] * psd.distance * beam.waist.y ** 2))) ** 2
                intensity_tmp = diffraction1D(grating.coefficients.y.n, grating.coefficients.y.cn,
                                              beam.coefficients.y.n, beam.coefficients.y.cn,
                                              beam.band.wavelength[i], beam.angle.y, beam.waist.x, beam.curvature.y,
                                              psd.distance, x)
                intensity_y += beam.band.intensity[i] * intensity_tmp

    else:
        intensity_x = diffraction1DAtZeroDistance(grating.coefficients.x.n, grating.coefficients.x.cn,
                                                  beam.coefficients.x.n, beam.coefficients.x.cn,
                                                  beam.waist.x, x)
        intensity_y = diffraction1DAtZeroDistance(grating.coefficients.y.n, grating.coefficients.y.cn,
                                                  beam.coefficients.y.n, beam.coefficients.y.cn,
                                                  beam.waist.y, x)

    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, pts)
    intensity = data.Distribution2D()
    intensity.x = averagePixel(intensity_x, x, round(psd.div_factor))
    intensity.y = averagePixel(intensity_y, x, round(psd.div_factor))
    return intensity
