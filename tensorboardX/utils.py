# Functions for converting
def figure_to_image(figures, close=True):
    """Render matplotlib figure to numpy format.

    Note that this requires the ``matplotlib`` package.

    Args:
        figure (matplotlib.pyplot.figure) or list of figures: figure or a list of figures
        close (bool): Flag to automatically close the figure

    Returns:
        numpy.array: image in [CHW] order
    """
    import numpy as np
    try:
        import matplotlib.pyplot as plt
        import matplotlib.backends.backend_agg as plt_backend_agg
    except ModuleNotFoundError:
        print('please install matplotlib')

    def render_to_rgb(figure):
        canvas = plt_backend_agg.FigureCanvasAgg(figure)
        canvas.draw()
        data = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8)
        w, h = figure.canvas.get_width_height()
        image_hwc = data.reshape([h, w, 4])[:, :, 0:3]
        image_chw = np.moveaxis(image_hwc, source=2, destination=0)
        if close:
            plt.close(figure)
        return image_chw

    if not isinstance(figures, list):
        image = render_to_rgb(figures)
        return image
    else:
        images = [render_to_rgb(figure) for figure in figures]
        return np.stack(images)


def graphviz_to_image():
    pass


def _prepare_image(I, dataformats='NCHW'):
    import numpy as np
    # convert [N]CHW image to HWC
    assert isinstance(
        I, np.ndarray), 'plugin error, should pass numpy array here'
    assert I.ndim == 2 or I.ndim == 3 or I.ndim == 4
    if I.ndim == 4:  # NCHW
        if I.shape[1] == 1:  # N1HW
            I = np.concatenate((I, I, I), 1)  # N3HW
        assert I.shape[1] == 3
        I = make_grid(I)  # 3xHxW
    if I.ndim == 3 and I.shape[0] == 1:  # 1xHxW
        I = np.concatenate((I, I, I), 0)  # 3xHxW
    if I.ndim == 2:  # HxW
        I = np.expand_dims(I, 0)  # 1xHxW
        I = np.concatenate((I, I, I), 0)  # 3xHxW
    I = I.transpose(1, 2, 0)  # HWC

    return I


def _prepare_video(V, dataformats):
    import numpy as np
    b, c, t, h, w = V.shape

    if V.dtype == np.uint8:
        V = np.float32(V) / 255.

    def is_power2(num):
        return num != 0 and ((num & (num - 1)) == 0)

    # pad to nearest power of 2, all at once
    if not is_power2(V.shape[0]):
        len_addition = int(2**V.shape[0].bit_length() - V.shape[0])
        V = np.concatenate(
            (V, np.zeros(shape=(len_addition, c, t, h, w))), axis=0)

    b = V.shape[0]
    n_rows = 2**((b.bit_length() - 1) // 2)
    n_cols = b // n_rows

    V = np.reshape(V, newshape=(n_rows, n_cols, c, t, h, w))
    V = np.transpose(V, axes=(3, 0, 4, 1, 5, 2))
    V = np.reshape(V, newshape=(t, n_rows * h, n_cols * w, c))

    return V


def make_grid(I, ncols=8):
    import numpy as np
    assert isinstance(
        I, np.ndarray), 'plugin error, should pass numpy array here'
    assert I.ndim == 4 and I.shape[1] == 3
    nimg = I.shape[0]
    H = I.shape[2]
    W = I.shape[3]
    ncols = min(nimg, ncols)
    nrows = int(np.ceil(float(nimg) / ncols))
    canvas = np.zeros((3, H * nrows, W * ncols))
    i = 0
    for y in range(nrows):
        for x in range(ncols):
            if i >= nimg:
                break
            canvas[:, y * H:(y + 1) * H, x * W:(x + 1) * W] = I[i]
            i = i + 1
    return canvas

    # if modality == 'IMG':
    #     if x.dtype == np.uint8:
    #         x = x.astype(np.float32) / 255.0


def convert_to_NCHW(tensor, input_format):  # tensor: numpy array
    input_format = input_format.upper()

    if len(input_format) == 4:
        print(tensor.shape)
        index = [input_format.find(c) for c in 'NCHW']
        return tensor.transpose(index)

    if len(input_format) == 3:
        index = [input_format.find(c) for c in 'CHW']

        return tensor

    if len(input_format) == 2:
        index = [input_format.find(c) for c in 'HW']
        tensor = tensor.transpose(index)
        tensor = np.expand_dims(tensor, 0)  # 1xHxW
        tensor = np.expand_dims(tensor, 0)  # 1x1xHxW
        return tensor

# #NCDHW
