import pandas as pd
import os

# TODO: need to automate inclusion of files somehow? seems very doable
import agree_disagree

from base_question import BaseQuestion


path = "figs"
qs = pd.read_csv("qs_full.csv")

# Currently only have one survey I can use here
surveys = [("DataforProgressNationalIssuesSurveyWave4", "dfp_april2019_return.csv")]

# iter over all surveys, over all questions, running gen_figs when possible (there is a type match)
for survey, survey_data in surveys:
    df = pd.read_csv("dfp_april2019_return.csv")
    for _, q in qs.iterrows():
        if q["survey"] != survey:
            continue
        # this is like a basic plugin framework, get everything that subclasses the Base, and check against
        # the valid_type method; if valid_type returns true, call gen_figs
        for c in BaseQuestion.__subclasses__():
            if c.valid_type(q):
                if not os.path.isdir(os.path.join(path, survey + "_" + q["alias"])):
                    os.mkdir(os.path.join(path, survey + "_" + q["alias"]))
                print(q["alias"])
                # TODO: maybe clean up usage of rows/get_q util... should ideally be consistent
                # TODO: check that all aliases are in data file
                c(df, qs, survey, q["alias"]).gen_figs()


