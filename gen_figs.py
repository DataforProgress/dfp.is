import pandas as pd
import os

# TODO: need to automate inclusion of files somehow? seems very doable
from questions.base_question import BaseQuestion
import questions.categorical

data_path = "data"
fig_path = "figs"
qs = pd.read_csv("data/qs_full.csv")

# Currently only have one survey I can use here
surveys = [("DataforProgressNationalIssuesSurveyWave4", "dfp_april2019_return.csv"),
           ("DfP:DemocraticPrimaryFirstDebateSurvey--FullDataset", "FIRSTDEBATE_DATA.csv"),
           ("DataforProgressYouGovBlue,Jan2019IssuesSurvey", "dfp_wave3_201901_final.csv")]


# iter over all surveys, over all questions, running gen_figs when possible (there is a type match)
for survey, survey_data in surveys:
    df = pd.read_csv(os.path.join(data_path, survey_data))
    for _, q in qs.iterrows():
        if q["alias"] in ("inputstate", "inputregstate"):
            continue
        if q["survey"] != survey:
            continue
        print(survey, q["alias"])
        # this is like a basic plugin framework, get everything that subclasses the Base, and check against
        # the valid_type method; if valid_type returns true, call gen_figs
        for c in BaseQuestion.__subclasses__():
            if c.valid_type(q):
                if not os.path.isdir(os.path.join(fig_path, survey + "_" + q["alias"])):
                    os.mkdir(os.path.join(fig_path, survey + "_" + q["alias"]))
                #else:
                #    continue

                # TODO: maybe clean up usage of rows/get_q util... should ideally be consistent
                # TODO: check that all aliases are in data file
                c(df, qs, survey, q["alias"]).gen_figs()


