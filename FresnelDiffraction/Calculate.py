import numpy as np
import DataStructures as data
import math
import statistics
import scipy

width_init = 300


def beambandSpectrumIntensities(beam):
    beam_band = data.Spectrum()
    if beam.bandwidth == 0:
        beam_band.wavelength = beam.wavelength
        beam_band.intensity = 1
    else:
        delta_wl = beam.wavelength / 100
        wls_less = np.arange(beam.wavelength, beam.wavelength / (1 + 3 * beam.bandwidth) - delta_wl, -delta_wl)
        if 3 * beam.bandwidth >= 1:
            wls_more = np.arange(beam.wavelength, beam.wavelength * 100 + delta_wl, delta_wl)
        else:
            wls_more = np.arange(beam.wavelength, beam.wavelength / (1 - 3 * beam.bandwidth) + delta_wl, delta_wl)
        wls = np.sort(np.array(list(set(np.append(wls_less, wls_more)))))
        if np.min(wls) <= 0:
            wls = wls[wls > 0]
        if len(wls) == 1:
            wls = wls[0]
        beam_band.wavelength = wls
        beam_band.intensity = np.exp(-((wls - beam.wavelength) / (wls * beam.bandwidth)) ** 2)
        beam_band.intensity = beam_band.intensity / sum(beam_band.intensity)
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
            opt_coeff.append([grating.phase_depth, setCoefficientsForWL(grating)])
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
        return np.abs(u) ** 2

    def averagePixel(intensity, x, sd):
        distribution = data.Distribution()
        distribution.coordinate = x
        int_out = np.zeros(len(x))
        for i in range(len(x)):
            int_out[i] = statistics.mean(intensity[i * sd:(i + 1) * sd])
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

        return np.abs(u) ** 2

    def spectralDiffraction1D(bbi, n, cn, m, am, wl, angle, waist, wfc, a, distance, x):
        swl = bbi * np.abs(np.sqrt(2 * math.pi / complex(2 * math.pi * (1 + distance * wfc),
                                                         wl * distance * waist ** 2))) ** 2
        intensity = swl * diffraction1D(n, cn, m, am, wl, angle, waist, wfc, a, distance, x)
        return intensity

    pts = round(psd.aperture // psd.step) + 1
    psd.aperture = psd.step * pts
    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, round(pts * psd.div_factor))
    if psd.distance > 0:
        if beam.bandwidth == 0:
            intensity_x = spectralDiffraction1D(1, grating.coefficients.x.n, grating.coefficients.x.cn,
                                                beam.coefficients.x.n, beam.coefficients.x.cn,
                                                beam.wavelength, beam.angle.x, beam.waist.x, beam.curvature.x,
                                                beam.aperture.x, psd.distance, x)
            intensity_y = spectralDiffraction1D(1, grating.coefficients.y.n, grating.coefficients.y.cn,
                                                beam.coefficients.y.n, beam.coefficients.y.cn,
                                                beam.wavelength, beam.angle.y, beam.waist.y, beam.curvature.y,
                                                beam.aperture.y, psd.distance, x)
        else:
            intensity_x = np.zeros(len(x))
            intensity_y = np.zeros(len(x))
            if type([]) == type(grating.coefficients):
                for i in range(len(beam.band.wavelength)):
                    intensity_x += \
                        spectralDiffraction1D(beam.band.intensity[i],
                                              grating.coefficients[i][1].x.n, grating.coefficients[i][1].x.cn,
                                              beam.coefficients.x.n, beam.coefficients.x.cn, beam.band.wavelength[i],
                                              beam.angle.x, beam.waist.x, beam.curvature.x, beam.aperture.x,
                                              psd.distance, x)
                    intensity_y += \
                        spectralDiffraction1D(beam.band.intensity[i],
                                              grating.coefficients[i][1].y.n, grating.coefficients[i][1].y.cn,
                                              beam.coefficients.y.n, beam.coefficients.y.cn, beam.band.wavelength[i],
                                              beam.angle.y, beam.waist.x, beam.curvature.y, beam.aperture.y,
                                              psd.distance, x)
            else:
                for i in range(len(beam.band.wavelength)):
                    intensity_x += \
                        spectralDiffraction1D(beam.band.intensity[i],
                                              grating.coefficients.x.n, grating.coefficients.x.cn,
                                              beam.coefficients.x.n, beam.coefficients.x.cn, beam.band.wavelength[i],
                                              beam.angle.x, beam.waist.x, beam.curvature.x, beam.aperture.x,
                                              psd.distance, x)
                    intensity_y += \
                        spectralDiffraction1D(beam.band.intensity[i],
                                              grating.coefficients.y.n, grating.coefficients.y.cn,
                                              beam.coefficients.y.n, beam.coefficients.y.cn, beam.band.wavelength[i],
                                              beam.angle.y, beam.waist.x, beam.curvature.y, beam.aperture.y,
                                              psd.distance, x)
    else:
        if type([]) != type(grating.coefficients):
            intensity_x = diffraction1DAtZeroDistance(grating.coefficients.x.n, grating.coefficients.x.cn,
                                                      beam.waist.x, beam.aperture.x, x)
            intensity_y = diffraction1DAtZeroDistance(grating.coefficients.y.n, grating.coefficients.y.cn,
                                                      beam.waist.y, beam.aperture.y, x)
        else:
            intensity_x = np.zeros(len(x))
            intensity_y = np.zeros(len(x))
            for i in range(len(beam.band.wavelength)):
                intensity_x += beam.band.intensity[i] * \
                               diffraction1DAtZeroDistance(grating.coefficients[i][1].x.n,
                                                           grating.coefficients[i][1].x.cn,
                                                           beam.waist.x, beam.aperture.x, x)
                intensity_y += beam.band.intensity[i] * \
                               diffraction1DAtZeroDistance(grating.coefficients[i][1].y.n,
                                                           grating.coefficients[i][1].y.cn,
                                                           beam.waist.y, beam.aperture.y, x)

    x = np.linspace(-psd.aperture / 2, psd.aperture / 2, pts)
    intensity = data.Distribution2D()
    intensity.x = averagePixel(intensity_x, x, round(psd.div_factor))
    intensity.y = averagePixel(intensity_y, x, round(psd.div_factor))
    return intensity
