import abc


class BaseQuestion(abc.ABC):
    """
    This is the base question interface, all questions should inherit it.
    A question that inherits it will be automatically checked with the valid_type question in the gen_figs routine.
    """
    def __init__(self, df, qs, survey, survey_name, alias):
        """

        :param df: survey data frame
        :param qs: questions data frame
        :param survey: string id of the survey
        :param alias: alias of the categorical question
        """
        self.df = df
        self.qs = qs
        self.survey = survey
        self.survey_name = survey_name
        self.alias = alias

    @staticmethod
    def valid_type(q_row):
        """
        Checks if the question associated with q_row can be used with the gen_figs method implemented in this Question
        :param q_row: a pandas row from qs
        :return: True if this alias can be used with the gen_figs method implemented in this Question
        """
        return False

    @abc.abstractmethod
    def gen_figs(self):
        """
        Generates figures for this question type
        """
        pass
