import numpy as np
import pandas as pd
import os

import matplotlib.pyplot as plt
from dfpvizpy.dfpvizpy import dfpSave
import matplotlib.font_manager as fm
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import seaborn as sns

import textwrap

font = ImageFont.truetype('Montserrat-Regular.ttf', 12)
monserratReg = fm.FontProperties(fname='Montserrat-Regular.ttf')

def getMSE(df, qCol, valuesS, weightCol, valuesO=None):
    """

    :param df: survey data frame
    :param qCol: question column of interest
    :param valuesS: list of values to sum
    :param weightCol: column of weights for summing
    :param valuesO: optional column to subtract out, for calculating net values
    :return: pandas series of estimated mean and standard deviation
    """
    df = df[np.isfinite(df[weightCol])]
    Nwt = (df[weightCol].sum() ** 2) / np.sum(df[weightCol].values**2)
    if valuesO:
        MeanS = df[df[qCol].isin(valuesS)][weightCol].sum()/df[weightCol].sum()
        MeanO = df[df[qCol].isin(valuesO)][weightCol].sum()/df[weightCol].sum()
        Mean = MeanS-MeanO
        surveyStdvs = np.sqrt((MeanS*(1.-MeanS)+MeanO*(1.-MeanO)+2.*MeanO*MeanS)/Nwt)
    else:
        Mean = df[df[qCol].isin(valuesS)][weightCol].sum()/df[weightCol].sum()
        surveyStdvs = np.sqrt(Mean*(1.-Mean)/Nwt)

    if surveyStdvs == 0.:
        surveyStdvs = 1.

    return pd.Series({"Mean": Mean, "Std": surveyStdvs})


def get_q(qs, survey, alias, inc=None, wrap_len=None, ex_other=True):
    """
    Get a dict of representation of a question and a filtered list of the question responses
    :param qs: questions data frame
    :param survey: string id of the survey
    :param alias: alias of the categorical question
    :param inc: either int of responses up to inc or list of indices of responses to include (exclude others)
    :param wrap_len: length to wrap the responses or None if no wrap
    :param ex_other: exclude "Other" from returned responses
    :return: a dict of representation of a question and a filtered list of the question responses
    """
    #TODO: add ability to order responses with inc or some such
    #TODO: can use index instead of alias to grab row and then use .to_dict, much cleaner
    df = qs.loc[(qs["alias"] == alias) & (qs["survey"] == survey)]
    info = {k: v for k, v in zip(df.keys(), df.values[0])}
    if wrap_len is not None:
        wrapper = textwrap.TextWrapper(width=wrap_len)
        responses = ["\n".join(wrapper.wrap(cat)) for i, cat in enumerate(info["categories"].split(";"))
                     if ((ex_other is False) or cat != "Other") and ((inc is None) or (i in inc))]
    else:
        responses = [cat for i, cat in enumerate(info["categories"].split(";"))
                     if ((ex_other is False) or cat != "Other") and ((inc is None) or (i in inc))]
    return info, responses


def save_fig(survey, survey_name, title, path, alias, suffix, ax, ylabel, ylim=None, legend_kw=None):
    """
    Saves a figure in appropriate dir with passed settings
    :param survey: string survey code
    :param survey_name: string survey name for citation
    :param title: title of the plot
    :param path: path to write to
    :param alias: alias of question
    :param suffix: suffix to append to file name string
    :param ax: axis to save
    :param ylabel: y-label
    :param ylim: y-limit
    :param legend_kw: kwargs to pass to ax.legend(...)
    """
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    if ylim is not None:
        ax.set_ylim(ylim)
    if legend_kw is not None:
        ax.legend(**legend_kw)
    fname = os.path.join(path, survey + "_" + alias, alias + "_" + suffix + ".png")
    dfpSave(fname, [ax], despineX=True)
    img = Image.open(fname)
    width, height = img.size
    draw = ImageDraw.Draw(img)
    # TODO: fix dates in R data
    draw.text((20, height - 30),
              "Source: %s fielded by YouGov Blue.\n"
              "Responses are weighted to represent the population of registered voters." % survey_name,
              (0, 0, 0), font=font)
    img.save(fname)
