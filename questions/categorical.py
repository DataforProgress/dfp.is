from util import *

from dfpvizpy.dfpvizpy import dfpPartisan
from questions.base_question import BaseQuestion

dfCat = sns.color_palette(["#124073", "#A8BF14", "#B71D1A", "#BF7A00", "#b3b3b3", "#000000", "#BC4A11"])

# TODO: figure out how to grab these demos across surveys easily

splits = [
    ("gender", None),
    ("GENDER_4", None),
    ("race4", None),
    ("age5", None),
    ("educ4", None),
    ("pid3", 3),
    ("ideo3", None),
    ("urbancity", None),
    ("ideo5", None),
    ("ideo3", None),
    ("ideo7", None),
    ("urban", None),
    ("HOME_OWN", None),
    ("OPIOID", None)
]

class FiveCatQuestion(BaseQuestion):
    """
    A question with a five category scale in the order "Strongly", "Somewhat", "Neither", "Somewhat", "Strongly"
    """
    @staticmethod
    def valid_type(q_row):
        res_pattern = ["Strongly", "Somewhat", "Neither", "Somewhat", "Strongly"]
        if q_row["type"] == "categorical" and all(r in q for q, r in zip(q_row["categories"].split(";"), res_pattern)):
            return True
        return False

    def gen_figs(self):
        basic(self.df, self.qs, self.survey, self.alias,  q_inc=5, palette=dfpPartisan)
        for split_alias, s_inc in splits:
            full_split(self.df, self.qs, self.survey, self.alias, split_alias, q_inc=5, s_inc=s_inc,
                       palette=dfpPartisan)
            net_split(self.df, self.qs, self.survey, self.alias, split_alias, q_inc=5, s_inc=s_inc)


class CatQuestion(BaseQuestion):
    """
    Any non-FiveCat categorical question
    """
    @staticmethod
    def valid_type(q_row):
        # inputregstate is too big
        if q_row["type"] == "categorical" and not FiveCatQuestion.valid_type(q_row):
            return True
        return False

    def gen_figs(self):
        basic(self.df, self.qs, self.survey, self.alias)
        for split_alias, s_inc in splits:
            full_split(self.df, self.qs, self.survey, self.alias, split_alias, s_inc=s_inc)



def basic(df, qs, survey, question_alias, q_inc=None, path="figs", ylim=None, palette=dfCat):
    """
    Plot a basic percent respondents by category bar chart
    :param df: survey data frame
    :param qs: questions data frame
    :param survey: string id of the survey
    :param question_alias: alias of the categorical question
    :param q_inc: either int of responses up to q_inc or list of indices of responses to include
    :param path: path to dir for this question
    :param ylim: y-limit
    """
    if isinstance(q_inc, int):
        q_inc = list(range(q_inc))

    q_info, q_responses = get_q(qs, survey, question_alias, inc=q_inc, wrap_len=14, ex_other=False)

    data = []
    for j, part in enumerate(q_responses):
        mean, std = getMSE(df, question_alias, [j + 1], "weight")
        data.append([part, mean * 100.])

    data = pd.DataFrame.from_records(data, columns=["Response", "Perc"])
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax = sns.barplot(x="Response", y="Perc", data=data, ax=ax, palette=palette)
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x() + p.get_width() / 2., height + 0.5, '{:1.2f}%'.format(height), ha="center")
    
    save_fig(survey, q_info["survey_name"], q_info["name"], path, question_alias, "base",
             ax, "Percent Respondents", data, ylim=ylim)


def full_split(df, qs, survey, question_alias, split_alias, q_inc=None, s_inc=None,
               ex_other=True, path="figs", ylim=None, legend_n=True, palette=dfCat):
    """
    Plot a percent respondents by category bar chart split by some other categorical variable, the split_alias
    :param df: survey data frame
    :param qs: questions data frame
    :param survey: string id of the survey
    :param question_alias: alias of the categorical question
    :param split_alias: alias of the categorical split question
    :param q_inc: either int of responses up to q_inc or list of indices of responses to include
    :param s_inc: either int of responses up to q_inc or list of indices of responses to include
    :param ex_other: exclude "Other" response
    :param path: path to dir for this question
    :param ylim: y-limit
    :param legend_n: whether to add the n to the legend of the plot
    :param palette: the palette to use for coloring the plot
    """
    if isinstance(q_inc, int):
        q_inc = list(range(q_inc))
    if isinstance(s_inc, int):
        s_inc = list(range(s_inc))

    q_info, q_responses = get_q(qs, survey, question_alias, inc=q_inc, wrap_len=14, ex_other=False)
    s_info, s_responses = get_q(qs, survey, split_alias, inc=s_inc, wrap_len=30, ex_other=ex_other)
    if s_info is None:
        return

    data = []
    for i, s in enumerate(s_responses):
        for j, q in enumerate(q_responses):
            s_df = df[(df[split_alias] == i + 1)]
            mean, std = getMSE(s_df, question_alias, [j + 1], "weight")
            data.append([s + "\n(n=%d)" % len(s_df.index) if legend_n else s, q, mean * 100.])

    data = pd.DataFrame.from_records(data, columns=[s_info["name"], q_info["name"], "Response"])
    if data.empty:
        return

    try:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax = sns.barplot(x=s_info["name"], y="Response", hue=q_info["name"],
                         data=data, ax=ax, palette=palette)
    except TypeError:
        return
    except ValueError:
        return

    print(q_info["survey_name"], q_info["name"])

    save_fig(survey, q_info["survey_name"], q_info["name"],
             path, question_alias, split_alias + "_fs", ax, "Percent Respondents", data,
             legend_kw={"loc": "center", "bbox_to_anchor": (0.5, -0.15), "ncol": len(q_responses)}, ylim=ylim)


def net_split(df, qs, survey, question_alias, split_alias, q_inc=None, s_inc=None,
              ex_other=True, path="figs", ylim=(-100, 100), legend_n=True, palette=dfCat):
    """
    WARNING: ONLY WORKS FOR 5 CATEGORY QUESTIONS AT PRESENT, HENCE NOT CALLED FOR CAT
    Bins categories into agree/disagree and subtract disagree from agree to plot net agree bar chart
    :param df: survey data frame
    :param qs: questions data frame
    :param survey: string id of the survey
    :param question_alias: alias of the categorical question
    :param split_alias: alias of the categorical split question
    :param q_inc: either int of responses up to q_inc or list of indices of responses to include
    :param s_inc: either int of responses up to q_inc or list of indices of responses to include
    :param ex_other: exclude "Other" response
    :param path: path to dir for this question
    :param ylim: y-limit
    :param legend_n: whether to add the n to the legend of the plot
    :param palette: the palette to use for coloring the plot
    """
    if isinstance(q_inc, int):
        q_inc = list(range(q_inc))
    if isinstance(s_inc, int):
        s_inc = list(range(s_inc))

    # TODO: add bootstrapped point estimates of net support split
    # should probably auto-detect this somehow? TODO: think about handling columns like this better? OOP solves?
    cols = [[1, 2], [4, 5]]

    q_info, q_responses = get_q(qs, survey, question_alias, inc=q_inc, wrap_len=14, ex_other=True)
    s_info, s_responses = get_q(qs, survey, split_alias, inc=s_inc, wrap_len=30, ex_other=ex_other)

    if s_info is None:
        return

    data = []
    for i, s in enumerate(s_responses):
        s_df = df[(df[split_alias] == i + 1)]
        mean, std = getMSE(s_df, question_alias, cols[0], "weight", valuesO=cols[1])
        data.append([s + "\n(n=%d)" % len(s_df.index) if legend_n else s, mean * 100.])

    data = pd.DataFrame.from_records(data, columns=[s_info["name"], "Net Support"])
    if data.empty:
        return

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax = sns.barplot(x=s_info["name"], y="Net Support", data=data, ax=ax, palette=palette)

    save_fig(survey, q_info["survey_name"], q_info["name"], path, question_alias, split_alias + "_ns",
             ax, "Net Support", data, ylim=ylim)
