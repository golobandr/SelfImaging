import matplotlib.pyplot as plt
import os
from PIL import Image
import numpy as np


def twoSpectra(f0, s0, l0, f1, s1, l1, wd, fn):
    plt.bar(f0, s0, label=l0)
    plt.bar(f1, s1, label=l1)
    plt.xlabel('n')
    plt.ylabel('S, arb.un.')
    plt.yscale('log')
    plt.title('Spectrum')
    plt.legend()
    plt.savefig(os.path.join(wd, fn))
    plt.close()


def oneSpectrumCont(f, s, l, wd, fn):
    plt.plot(f, s, label=l)
    plt.xlabel('f')
    plt.ylabel('S, arb.un.')
    plt.yscale('log')
    plt.title('Spectrum')
    plt.legend()
    plt.savefig(os.path.join(wd, fn))
    plt.close()


def intensity(f, s, l, wd, fn):
    # plt.figure(2)
    plt.plot(f, s, label=l)
    plt.xlabel('x, mm')
    plt.ylabel('I, arb.un.')
    plt.title('Intensity')
    plt.legend()
    plt.savefig(os.path.join(wd, fn))
    plt.close()


def intensities(f, s, l, f1, s1, l1, wd, fn):
    # plt.figure(2)
    plt.plot(f, s, label=l)
    plt.plot(f1, s1, label=l1)
    plt.xlabel('x, mm')
    plt.ylabel('I, arb.un.')
    plt.title('Intensity')
    plt.legend()
    plt.savefig(os.path.join(wd, fn))
    plt.close()


def calculationError(error, n, ymin, wd, fn):
    error = error / np.max(error)
    plt.plot(n, error, '-o', markersize=8, markeredgecolor='blue',
             markerfacecolor=[0.5, 0.5, 1], color='blue')
    plt.xlabel('Step division')
    plt.ylabel('Error, a.u.')
    plt.yscale('log')
    plt.grid(True)
    plt.xlim([min(n), max(n)])
    plt.ylim([ymin, 1])
    plt.savefig(os.path.join(wd, fn))
    plt.close()


def image2D(image, x, y, title_str, wd, fn, fn1, fn2, is_d, is_s):
    image = image / image.max()
    if is_d and is_s:
        plt.figure(figsize=(8, 8), dpi=300)
        plt.imshow(image, extent=(x.min(), x.max(), y.min(), y.max()),
                   cmap='hot', interpolation='nearest', origin='lower',
                   aspect='auto')
        plt.colorbar()
        plt.title(title_str)
        plt.savefig(os.path.join(wd, fn1))
        plt.close()
        image = (image * 255).astype(np.uint8)
        Image.fromarray(image).save(os.path.join(wd, fn2), 'BMP')
    if is_s:
        plt.imsave(os.path.join(str(wd), 'hot_' + fn), image, cmap='hot')
        plt.imsave(os.path.join(str(wd), 'jet_' + fn), image, cmap='jet')
