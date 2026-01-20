import numpy as np
import DataStructures as data
import math
import statistics


def gratingCoefficients(grating, accuracy):
    def fourierReCoefficients(grating):
        width = 300
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
            width = 300
            x = np.linspace(-grating.period / 2, grating.period / 2, 2 * width + 2)
            x = x[0: 2 * width + 1]
            phase = grating.phase_depth * np.cos(2 * np.pi / grating.period * x)
            pit_re = np.cos(phase)
            pit_im = np.sin(phase)
            pit = pit_re + 1j * pit_im
            cn = np.fft.fftshift(np.fft.fft(pit))
        else:
            tmp_grating = data.Grating()
            tmp_grating.period = grating.period
            tmp_grating.duty_factor = 1
            [cn_one, _] = fourierReCoefficients(tmp_grating)
            [cn_pit, width] = fourierReCoefficients(grating)
            cn = cn_one + (np.exp(1j * grating.phase_depth) - 1) * cn_pit
        return cn, width

    def edgeCalculate(spectrum, accuracy):
        edges = 10 ** np.linspace(-20, 0, 21)
        [N, _] = np.histogram(spectrum, bins=edges)
        counts = N * edges[:len(N)]
        counts = counts / sum(counts)
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

    def fourierCoefficientsUpdate(cn, width, accuracy):
        spectrum = np.abs(cn) ** 2
        cn = cn / np.sqrt(np.sum(spectrum))
        spectrum = spectrum / np.max(spectrum)
        edge = edgeCalculate(spectrum, accuracy)
        cn_u = np.zeros(len(cn), dtype=complex)
        f_u = np.zeros(len(cn))
        s_u = np.zeros(len(cn))
        i = 0
        for f in range(-width, width + 1):
            n = f + width
            if spectrum[n] > edge:
                f_u[i] = f
                cn_u[i] = cn[n]
                s_u[i] = spectrum[n]
                i += 1
        f_u = f_u[:i]
        cn_u = cn_u[:i]
        s_u = s_u[:i]
        return [f_u, cn_u, s_u]

    if not 'phase' in grating.slit:
        [cn, width] = fourierReCoefficients(grating)
    else:
        [cn, width] = fourierComplexCoefficients(grating)
    cn = cn / math.sqrt(sum(np.abs(cn) ** 2))
    coef = data.Coefficients()
    [coef.n, coef.cn, coef.sn] = fourierCoefficientsUpdate(cn, width, accuracy)
    ret_val = data.Distribution2D()
    ret_val.x = coef
    if '1D' in grating.slit:
        ret_val.y = data.Coefficients()
    else:
        ret_val.y = coef
    return ret_val


def outputDistribution(grating, beam, psd):
    def normalIntensity(u):
        intensity = np.abs(u) ** 2
        # intensity = intensity / max(intensity)
        return intensity

    def diffraction1DAtZeroDistance(n, cn, p, waist, x):
        u = np.zeros(len(x), dtype=complex)
        f = 1j * 2 * math.pi * n / p
        for i in range(len(x)):
            u[i] = sum(cn * np.exp(x[i] * f))
        u = u * np.exp(-(x * waist) ** 2)
        return normalIntensity(u)

    def averagePixel(intensity, x, sd):
        distribution = data.Distribution()
        distribution.coordinate = x
        int_out = np.zeros(len(x))
        for i in range(len(x)):
            int_out[i] = statistics.mean(intensity[i * sd:(i + 1) * sd])
        distribution.intensity = int_out
        return distribution

    def diffraction1D(n, cn, p, wl, angle, waist, wfc, distance, x):
        a = ((math.pi ** 2 * 2 * wl * distance) /
             complex(wl * distance * waist ** 2, -2 * math.pi * (1 + wfc * distance)))
        n = n / p
        x = -1 / (wl * distance) * x - math.sin(angle) / (2 * wl)
        u = np.zeros(len(x), dtype=complex)
        for i in range(len(x)):
            exp_a = np.exp(-a * (x[i] + n) ** 2)
            u[i] = np.sum(exp_a * cn)
        return normalIntensity(u)

    pts = round(psd.aperture // psd.step) + 1
    psd.aperture = psd.step * pts
    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, round(pts * psd.div_factor))
    if psd.distance > 0:
        intensity_x = diffraction1D(grating.coefficients.x.n, grating.coefficients.x.cn, grating.period,
                                    beam.wavelength, beam.angle.x, beam.waist.x, beam.curvature.x, psd.distance, x)
        intensity_y = diffraction1D(grating.coefficients.y.n, grating.coefficients.y.cn, grating.period,
                                    beam.wavelength, beam.angle.y, beam.waist.y, beam.curvature.y, psd.distance, x)
    else:
        intensity_x = diffraction1DAtZeroDistance(grating.coefficients.x.n, grating.coefficients.x.cn,
                                                  grating.period, beam.waist.x, x)
        intensity_y = diffraction1DAtZeroDistance(grating.coefficients.y.n, grating.coefficients.y.cn,
                                                  grating.period, beam.waist.y, x)
    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, pts)
    intensity = data.Distribution2D()
    intensity.x = averagePixel(intensity_x, x, round(psd.div_factor))
    intensity.y = averagePixel(intensity_y, x, round(psd.div_factor))
    return intensity
