import pandas as pd
import os
from util import get_q
# TODO: need to automate inclusion of files somehow? seems very doable
from questions.base_question import BaseQuestion
import questions.categorical
# import questions.multiple_response

fig_path = "figs"
data_dir = "sg"


def gen_figs(survey_path, survey_name=""):
    print(survey_name)
    contents = [c for c in os.listdir(survey_path)]
    for c in contents:
        if os.path.isdir(os.path.join(survey_path, c)):
            gen_figs(os.path.join(survey_path, c), survey_name=survey_name + c)

    codebook_paths = [os.path.join(survey_path, c) for c in contents if "codebook" in c and "csv" in c]
    data_paths = [os.path.join(survey_path, c) for c in contents if "data" in c and "csv" in c]

    if len(codebook_paths) == 0 or len(data_paths) == 0:
        return

    survey = survey_name.replace(" ", "")
    # iter over all surveys, over all questions, running gen_figs when possible (there is a type match)
    for codebook_path, data_path in zip(codebook_paths, data_paths):
        cb = pd.read_csv(codebook_path)
        df = pd.read_csv(data_path)
        weight = [c for c in df.columns if "weight" in c]
        if len(weight) == 0:
            print("No weighting!")
            continue
        df = df.rename(columns={weight[0]: "weight"})
        for alias in cb["Variable"].unique():
            # this is like a basic plugin framework, get everything that subclasses the Base, and check against
            # the valid_type method; if valid_type returns true, call gen_figs
            for c in BaseQuestion.__subclasses__():
                q = get_q(cb, alias, ex_other=False)
                if not c.valid_type(q):
                    # TODO: fix question filtering; perhaps just by a simple mapping
                    continue
                if not os.path.isdir(os.path.join(fig_path, survey, alias, "csv")):
                    os.makedirs(os.path.join(fig_path, survey, alias, "csv"))
                if not os.path.isdir(os.path.join(fig_path, survey, alias, "png")):
                    os.makedirs(os.path.join(fig_path, survey, alias, "png"))
                    # TODO: make png construction completely seperate from csv construction -- should autogen from csvs
                    # picking format accordingly
                else:
                    continue
                # TODO: maybe clean up usage of rows/get_q util... should ideally be consistent
                # TODO: check that all aliases are in data file
                c(df, cb, survey, survey_name, alias).gen_figs()



gen_figs(data_dir, survey_name="")