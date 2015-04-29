"""
The class Histo provides an interface to generate and sample probability
distributions represented as histograms.
"""
import random
from bisect import bisect_right, bisect_left
from random import randint

# WFPadTools imports
from obfsproxy.transports.wfpadtools import const
import obfsproxy.common.log as logging


log = logging.get_obfslogger()


class Histogram:
    """Provides methods to generate and sample histograms of prob distributions."""

    def __init__(self, hist, interpolate=True, removeTokens=False):
        """Initialize an histogram.

        `hist` is a dictionary. The keys are labels of an histogram. They represent
        the value of the rightmost endpoint of the right-open interval of the bin. The
        dictionary value corresponding to that key is a count of tokens representing
        the frequency in the histogram.

        For example, the histogram:
         5-                                                     __
         4-                  __                                |  |
         3-        __       |  |                __             |  |
         2-       |  |      |  |               |  |            |  |
         1-       |  |      |  |               |  |            |  |
                [0, x_0) [x_0, x_1), ..., [x_(n-1), x_n), [x_n, infinite)

        Would be represented with the following dictionary:

            h = {'x_0': 3, 'x_1': 4, ..., 'x_n': 3, INF_LABEL: 5}

        `interpolate` indicates whether the value is sampled uniformly
        from the interval defined by the bin (e.g., U([x_0, x_1)) or the value
        of the label is returned. In case of a discrete histogram we would have:

         5-                                                     __
         4-                  __                                |  |
         3-        __       |  |                __             |  |
         2-       |  |      |  |               |  |            |  |
         1-       |  |      |  |               |  |            |  |
                  x_0       x_1      ...       x_n           infinite

        `removeToks` indicates that every time a sample is drawn from the histrogram,
        we remove one token from the count (the values in the dictionary). We keep a
        copy of the initial value of the histogram to re assign it when the histogram
        runs out of tokens.

        We assume all values in the dictionary are positive integers and
        that there is at least a non-zero value. For efficiency, we assume the labels
        are floats that have been truncated up to some number of decimals. Normally, the
        labels will be seconds and since we want a precision of milliseconds, the float
        is truncated up to the 3rd decimal position with for example round(x_i, 3).
        """
        self.hist = hist
        # store labels in a list for fast search over keys
        self.labels = sorted(self.hist.keys())
        if const.INF_LABEL in self.labels:
            self.labels = self.labels[1:] + self.labels[:1]
        self.n = len(self.labels)
        self.template_sum = sum(self.hist.values())
        self.sum_counts = self.template_sum
        self.interpolate = interpolate
        self.removeTokens = removeTokens
        self.template = dict(hist)

    def getLabelFromFloat(self, f):
        """Return the label for the interval to which `f` belongs."""
        return self.labels[bisect_left(self.labels, f, hi=self.n-1)]

    def removeToken(self, f):
        # TODO: move the if below to the calls to the function `removeToken`
        if self.removeTokens:
            label = self.getLabelFromFloat(f)
            pos_counts = [l for l in self.labels if self.hist[l] > 0]
            # else remove tokens from label or the next non-empty label on the left
            # if there is none, continue removing tokens on the right.
            if label not in pos_counts:
                i = bisect_right(pos_counts, label, hi=len(pos_counts)-1)
                label = pos_counts[i]
            self.hist[label] -= 1
            self.sum_counts -= 1
            # if histogram is empty, refill the histogram
            if self.sum_counts == 0:
                self.refillHistogram()

    def dumpHistogram(self):
        """Print the values for the histogram."""
        log.debug("Dumping histogram:")
        if self.interpolate:
            log.debug("[0, %s), %s", self.labels[0], self.hist[self.labels[0]])
            for labeli, labeli1 in zip(self.labels[0:-2], self.labels[1:-1]):
                log.debug("[%s, %s), %s", labeli, labeli1, self.hist[labeli1])
            log.debug("[%s, infinite), %s", self.labels[-2], self.hist[self.labels[-1]])
        else:
            for label, count in self.hist:
                log.debug("(%s, %s)", label, count)

    def refillHistogram(self):
        """Copy the template histo."""
        self.hist = dict(self.template)
        self.sum_counts = self.template_sum
        log.debug("[histo] Refilled histogram: %s" % (self.hist))

    def randomSample(self):
        """Draw and return a sample from the histogram."""
        prob = randint(1, self.sum_counts) if self.sum_counts > 0 else 0
        for i, label_i in enumerate(self.labels):
            prob -= self.hist[label_i]
            if prob > 0:
                continue
            if not self.interpolate or i == self.n - 1:
                return label_i
            label_i_1 = 0 if i == 0 else self.labels[i - 1]
            return label_i + (label_i_1 - label_i) * random.random()


def uniform(x):
    return new({x: 1}, interpolate=False, removeTokens=False)


# Alias class name in order to provide a more intuitive API.
new = Histogram
