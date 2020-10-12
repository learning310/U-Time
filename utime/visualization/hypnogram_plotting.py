import matplotlib.pyplot as plt
import numpy as np
from utime import Defaults


def get_reordered_hypnogram(hyp_array, annotation_dict, order):
    """
    Takes a ndarray-like hypnogram 'hyp_array' of integers and returns a re-leveled version
    according to 'order'. The 'order' should be specified as a list of sleep stage strings.
    The mapping between the integers in 'hyp_array' and the string representation in 'order' should be
    given by a dict 'annotation_dict' with integer key pointing to string sleep stages.

    E.g. an input array [0, 0, 1, 2, 3, 4] with order ['W', 'REM', 'N1', 'N2', 'N3'] and annotation_dict
    {0: "W", 1: "N1", 2: "N2", 3: "N3", 4: "REM"} would produce the output:

    >> array([0, 0, 2, 3, 4, 1])
    """
    str_to_int_map = {value: key for key, value in annotation_dict.items()}
    int_order = [str_to_int_map[key] for key in order]
    mapper = np.vectorize({
        original_int: reordered_int for original_int, reordered_int in zip(int_order, range(len(int_order)))
    }.get)
    return mapper(hyp_array)


def plot_hypnogram(hyp_array,
                   true_hyp_array=None,
                   seconds_per_epoch=30,
                   annotation_dict=None,
                   order=("N3", "N2", "N1", "REM", "W")):
    """
    Plot a ndarray hypnogram of integers, 'hyp_array', optionally on top of an expert annotated hypnogram
    'true_hyp_array'.

    Args:
        hyp_array:         ndarray, shape [N]
        true_hyp_array:    ndarray, shape [N] (optional, default=None)
        seconds_per_epoch: integer, default=30
        annotation_dict:   dict, integer -> stage string mapping
        order:             list-like of strings, order of sleep stages on plot y-axis

    Returns:
        fig, axes
    """
    rows = 1 if true_hyp_array is None else 2
    hight = 3 if true_hyp_array is None else 6
    fig, axes = plt.subplots(nrows=rows, figsize=(10, hight), sharex=True, sharey=True)
    if not isinstance(axes, (list, np.ndarray)):
        axes = [axes]

    # Map classes to default string classes
    annotation_dict = annotation_dict or Defaults.get_class_int_to_stage_string()
    hyp_array = get_reordered_hypnogram(hyp_array, annotation_dict, order)

    x_hours = np.array([seconds_per_epoch * i for i in range(len(hyp_array))]) / 3600
    axes[0].step(x_hours, hyp_array, where='post', color="black", label="Predicted hypnogram")

    # Set ylabels
    for ax in axes:
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels(order)
        ax.set_ylabel("Sleep Stage", size=16, labelpad=12)
        ax.tick_params(axis='both', which='major', labelsize=14)
    axes[-1].set_xlabel("Time (hours)", size=16, labelpad=12)
    axes[-1].set_xlim(0, x_hours[-1])

    fig.tight_layout()
    if true_hyp_array is not None:
        true_hyp_array = get_reordered_hypnogram(true_hyp_array, annotation_dict, order)
        axes[1].step(x_hours, true_hyp_array, where='post', color="darkred", label="Expert's hypnogram")

        lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
        lines, labels = [sum(l, []) for l in zip(*lines_labels)]
        l = fig.legend(lines, labels, loc='center', bbox_to_anchor=(0.5, 0.96), ncol=2, fontsize=14)
        l.get_frame().set_linewidth(0)
        fig.subplots_adjust(hspace=0.1, top=0.92)
    return fig, axes
