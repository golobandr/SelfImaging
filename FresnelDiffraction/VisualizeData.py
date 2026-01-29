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
                                    'FF Image', result.io.filedir, f'psd_image_{idx}.png',
                                    f'psd_image_scale_{idx}.png', f'psd_image_gray_{idx}.bmp',
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
                                            result.data[idx].psd.image.x.intensity, 'x',
                                            result.data[idx].psd.image.y.coordinate,
                                            result.data[idx].psd.image.y.intensity, 'y', result.io.filedir,
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
    if result.is_ok and ('distance' in result.dependencies.lower() or 'duty factor' in result.dependencies.lower()) \
            and len(result.data) > 2:
        z = np.zeros(len(result.data))
        x = result.data[0].psd.image.x.coordinate
        image = np.zeros((len(x), len(result.data)))
        for idx in range(len(result.data)):
            if 'distance' in result.dependencies.lower():
                z[idx] = result.data[idx].psd.distance
            elif 'duty factor' in result.dependencies.lower():
                z[idx] = result.data[idx].grating.duty_factor
            image[:, idx] = result.data[idx].psd.image.x.intensity
        DisplayData.image2D(image, z, x, 'Talbot carpet', result.io.filedir, 'carpet.png',
                            'carpet_scale.png', 'carpet_gray.bmp', True, True)
        dependencies['distance'] = {'z': z,
                                    'x': x,
                                    'image': image}
    return dependencies
