import DataStructures as data
import numpy as np
import DisplayData


def images(result):
    for idx in range(len(result.data)):
        if result.data[idx].is_ok:
            if result.data[idx].add.save:
                pts = len(result.data[idx].psd.image.x.coordinate)
                image = np.zeros((pts, pts))
                for i in range(pts):
                    for j in range(pts):
                        image[i, j] = result.data[idx].psd.image.x.intensity[i] * \
                                      result.data[idx].psd.image.y.intensity[j]
                DisplayData.image2D(image, result.data[idx].psd.image.x.coordinate,
                                    result.data[idx].psd.image.y.coordinate,
                                    'FF Image', result.io.filedir, f'psd_image_{idx}',
                                    result.data[idx].add.debug, result.data[idx].add.save)
                if result.data[idx].beam.angle.y != 0 or result.data[idx].beam.angle.x != 0 or \
                        result.data[idx].beam.curvature.y != 0 or result.data[idx].beam.curvature.x != 0:
                    phase_x = result.data[idx].psd.image.x.coordinate * np.sin(result.data[idx].beam.angle.x) + \
                              result.data[idx].psd.image.x.coordinate ** 2 * result.data[idx].beam.curvature.x
                    phase_y = result.data[idx].psd.image.y.coordinate * np.sin(result.data[idx].beam.angle.y) + \
                              result.data[idx].psd.image.y.coordinate ** 2 * result.data[idx].beam.curvature.y
                    phase_x /= np.max(phase_x)
                    phase_y /= np.max(phase_y)
                    pts = len(result.data[idx].psd.image.x.coordinate)
                    image = np.zeros((pts, pts))
                    for i in range(pts):
                        for j in range(pts):
                            image[i, j] = phase_x[i] * phase_y[j]
                    DisplayData.image2D(image, result.data[idx].psd.image.x.coordinate,
                                        result.data[idx].psd.image.y.coordinate,
                                        'WF', result.io.filedir, f'wf_image_{idx}',
                                        result.data[idx].add.debug, result.data[idx].add.save)
                if result.data[idx].add.debug:
                    DisplayData.twoSpectra(result.data[idx].grating.coefficients.x.n,
                                           result.data[idx].grating.coefficients.x.sn, 'x',
                                           result.data[idx].grating.coefficients.y.n,
                                           result.data[idx].grating.coefficients.y.sn, 'y', result.io.filedir,
                                           f'grating_spectrum_{idx}.png')
                    DisplayData.twoSpectra(result.data[idx].beam.coefficients.x.n,
                                           result.data[idx].beam.coefficients.x.sn, 'x',
                                           result.data[idx].beam.coefficients.y.n,
                                           result.data[idx].beam.coefficients.y.sn, 'y', result.io.filedir,
                                           f'beam_spectrum_{idx}.png')
                    DisplayData.intensities(result.data[idx].psd.image.x.coordinate,
                                            result.data[idx].psd.image.x.intensity /
                                            np.max(result.data[idx].psd.image.x.intensity), 'x',
                                            result.data[idx].psd.image.y.coordinate,
                                            result.data[idx].psd.image.y.intensity /
                                            np.max(result.data[idx].psd.image.y.intensity), 'y', result.io.filedir,
                                            f'psd_1d_distribution_{idx}.png')
        else:
            print('    ' + data.text.RED + f'Line {idx + 1} visualization skipped since input data is '
                                           f'incorrect and no calculation provided' + data.text.END)


def dependencies(result):
    dependencies = {}
    if result.is_ok and 'error' in result.dependencies and len(result.data) > 3:
        i_error = np.zeros(len(result.data) - 1)
        n_error = np.zeros(len(result.data) - 1)
        for idx in range(len(result.data) - 1):
            n_error[idx] = result.data[idx].psd.div_factor
            i_diff = np.abs(result.data[idx].psd.image.x.intensity - result.data[idx + 1].psd.image.x.intensity)
            i_error[idx] = sum(i_diff)
        DisplayData.calculationError(i_error, n_error, 1E-4, result.io.filedir, 'error_distribution.png')
        dependencies['error'] = {'n': n_error,
                                 'data': i_error}
    if result.is_ok and (result.dependencies != '') and len(result.data) > 2:
        z = np.arange(len(result.data), dtype=float)
        x = result.data[0].psd.image.x.coordinate
        image_x = np.zeros((len(x), len(result.data)))
        image_y = np.zeros((len(x), len(result.data)))
        image_x_n = np.zeros((len(x), len(result.data)))
        image_y_n = np.zeros((len(x), len(result.data)))
        for idx in range(len(result.data)):
            image_x[:, idx] = result.data[idx].psd.image.x.intensity * result.data[idx].beam.intensity
            image_y[:, idx] = result.data[idx].psd.image.y.intensity * result.data[idx].beam.intensity
            if result.data[idx].beam.intensity != 0:
                image_x_n[:, idx] = ((result.data[idx].psd.image.x.intensity -
                                      np.min(result.data[idx].psd.image.x.intensity)) /
                                     np.max(result.data[idx].psd.image.x.intensity))
                image_y_n[:, idx] = ((result.data[idx].psd.image.y.intensity -
                                      np.min(result.data[idx].psd.image.y.intensity)) /
                                     np.max(result.data[idx].psd.image.y.intensity))
            else:
                image_x_n[:, idx] = result.data[idx].psd.image.x.intensity * result.data[idx].beam.intensity
                image_y_n[:, idx] = result.data[idx].psd.image.y.intensity * result.data[idx].beam.intensity
            if 'distance' in result.dependencies.lower():
                z[idx] = result.data[idx].psd.distance
            elif 'duty factor' in result.dependencies.lower():
                z[idx] = result.data[idx].grating.duty_factor
            elif 'x curvature' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.curvature.x
            elif 'y curvature' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.curvature.y
            elif 'x aperture' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.aperture.x
            elif 'y aperture' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.aperture.y
            elif 'x waist' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.waist.x / 2
            elif 'y waist' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.waist.y / 2
            elif 'bandwidth' in result.dependencies.lower():
                z[idx] = result.data[idx].beam.bandwidth * 100

        if 'distance' in result.dependencies.lower() or 'duty factor' in result.dependencies.lower() or \
                'bandwidth' in result.dependencies.lower():
            DisplayData.image2D(image_x, z, x, 'Talbot carpet', result.io.filedir, 'carpet_x',
                                False, True)
            DisplayData.image2D(image_y, z, x, 'Talbot carpet', result.io.filedir, 'carpet_y',
                                False, True)
            DisplayData.image2D(image_x_n, z, x, 'Talbot carpet', result.io.filedir, 'carpet_x_n',
                                False, True)
            DisplayData.image2D(image_y_n, z, x, 'Talbot carpet', result.io.filedir, 'carpet_y_n',
                                False, True)
        elif 'x ' in result.dependencies.lower():
            DisplayData.image2D(image_x, z, x, 'Talbot carpet', result.io.filedir, 'carpet',
                                False, True)
            DisplayData.image2D(image_x_n, z, x, 'Talbot carpet', result.io.filedir, 'carpet_n',
                                False, True)
        elif 'y ' in result.dependencies.lower():
            DisplayData.image2D(image_y, z, x, 'Talbot carpet', result.io.filedir, 'carpet',
                                False, True)
            DisplayData.image2D(image_y_n, z, x, 'Talbot carpet', result.io.filedir, 'carpet_n',
                                False, True)
        dependencies[result.dependencies.lower()] = {'z': z,
                                                     'x': x,
                                                     'image_x': image_x,
                                                     'image_y': image_y}
    return dependencies


def convertScale(image):
    image = np.log10(image / image.max() * 1E5 + 1)
    return image / image.max()
