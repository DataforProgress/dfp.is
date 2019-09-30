from util import *

dfCat = sns.color_palette(["#124073", "#A8BF14", "#B71D1A", "#BF7A00", "#b3b3b3", "#000000", "#BC4A11"])

# TODO: could handle stacking vs not stacking here, by switching based on # of splits; categeorical array *looks* like many split variable
def basic(data, survey, survey_name, question_name, question_alias, path="figs", ylim=None, palette=dfCat):
    # data = pd.DataFrame.from_records(data, columns=[q["Name"].iloc[0], "Response"])

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax = sns.barplot(x=question_name, y="Response", data=data, ax=ax, palette=palette)
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x() + p.get_width() / 2., height + 0.5, '{:1.2f}%'.format(height), ha="center")

    save_fig(survey, survey_name, question_name, path, question_alias, "base",
             ax, "Percent Respondents", data, ylim=ylim)


def full_split(data, survey, survey_name, question_name, question_alias, split_name, split_alias,
               path="figs", ylim=None, palette=dfCat):

    try:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax = sns.barplot(x=split_name, y="Response", hue=question_name,
                         data=data, ax=ax, palette=palette)
    except TypeError:
        return
    except ValueError:
        return

    save_fig(survey, survey_name, question_name,
             path, question_alias, split_alias + "_fs", ax, "Percent Respondents", data,
             legend_kw={"loc": "center", "bbox_to_anchor": (0.5, -0.15), "ncol": len(data)}, ylim=ylim)


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
    survey_name = survey
    if isinstance(q_inc, int):
        q_inc = list(range(q_inc))
    if isinstance(s_inc, int):
        s_inc = list(range(s_inc))

    # TODO: add bootstrapped point estimates of net support split
    # should probably auto-detect this somehow? TODO: think about handling columns like this better? OOP solves?
    cols = [[1, 2], [4, 5]]

    q = get_q(qs, question_alias, inc=q_inc, wrap_len=14, ex_other=True)
    s = get_q(qs, split_alias, inc=s_inc, wrap_len=30, ex_other=ex_other)

    if len(s) == 0:
        return

    data = []
    for i, sr in enumerate(s["Response"]):
        s_df = df[(df[split_alias] == i + 1)]
        mean, std = getMSE(s_df, question_alias, cols[0], "weight", valuesO=cols[1])
        data.append([sr + "\n(n=%d)" % len(s_df.index) if legend_n else s, mean * 100.])

    data = pd.DataFrame.from_records(data, columns=[s["Name"].iloc[0], "Response"])
    if data.empty:
        return

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax = sns.barplot(x=s["Name"].iloc[0], y="Response", data=data, ax=ax, palette=palette)

    save_fig(survey, survey_name, q["Name"].iloc[0], path, question_alias, split_alias + "_ns",
             ax, "Net Support", data, ylim=ylim)
