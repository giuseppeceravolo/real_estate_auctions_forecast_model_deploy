import pandas as pd
import numpy as np


class AuctionsDataFrame:
    def __init__(self, records):
        """
            Please note that here we assume that 'records' contains the columns names in its first row
        """
        self.dataframe = pd.DataFrame.from_records(records)
        self.dataframe.columns = self.dataframe.loc[0].tolist()
        self.dataframe = self.dataframe[1:]

    def cleaning_currency_format(self):
        """
            Here we delete the currency ('€') and correctly format thousands and decimals separators
        """
        for column in self.dataframe.columns.values:
            if self.dataframe[column].str.contains('€').sum() > 0:
                self.dataframe[column] = self.dataframe[column].apply(lambda x: x.replace('€ ', ''))
                self.dataframe[column] = self.dataframe[column].apply(lambda x: x.replace('.', ''))
                self.dataframe[column] = self.dataframe[column].apply(lambda x: x.replace(',', '.'))

    def drop_rows(self, columns, value):
        if isinstance(columns, list) and isinstance(columns[0], str):
            for col in columns:
                self.dataframe = self.dataframe.loc[self.dataframe[col] != value]
        elif isinstance(columns, str):
            self.dataframe = self.dataframe.loc[self.dataframe[columns] != value]
        else:
            raise Exception("The attribute columns must be either a string or a list of string.")

    def to_numeric(self, columns):
        if isinstance(columns, list) and isinstance(columns[0], str):
            for col in columns:
                self.dataframe[col] = pd.to_numeric(self.dataframe[col], errors='coerce')
        elif isinstance(columns, str):
            self.dataframe[columns] = pd.to_numeric(self.dataframe[columns], errors = 'coerce')
        else:
            raise Exception("The attribute columns must be either a string or a list of string.")

    def filter_columns(self, columns):
        self.dataframe = self.dataframe[columns]

    def dropna(self, columns):
        self.dataframe.dropna(subset=columns, how='any', inplace=True)

    def add_sconto_between(self, wrt, var):
        """
            A new column is added to the dataframe as: "Sconto tra wrt e var" =  (wrt - var) / wrt
        """
        variable_name = "Sconto tra " + wrt + " e " + var
        self.dataframe[variable_name] = pd.to_numeric((self.dataframe[wrt] - self.dataframe[var]) / self.dataframe[wrt])
        return variable_name

    def log_transform(self, columns):
        if isinstance(columns, list) and isinstance(columns[0], str):
            for col in columns:
                self.dataframe[col] = np.log(self.dataframe[col] + 1)
        elif isinstance(columns, str):
            self.dataframe[columns] = np.log(self.dataframe[columns] + 1)
        else:
            raise Exception("The attribute columns must be either a string or a list of string.")

    def prepare_for_evaluation(self):
        """
            Please note that the first column (the ids) has to be dropped before calling this method
        """
        return np.array(self.dataframe[self.dataframe.columns.values[1:]]).reshape(-1, self.dataframe.shape[1] - 1)

    def get_ids_list(self):
        return self.dataframe['Id Immobile'].tolist()

    def check_probability_column(self):
        assert "Probability" in self.dataframe.columns.values, "The AuctionsDataframe has no Probability column."

    def get_probability_by_id(self, Id):
        self.check_probability_column()
        return self.dataframe['Probability'].loc[self.dataframe['Id Immobile'] == Id].values[0]

    def compute_and_store_probability(self, model):
        self.dataframe['Probability'] = model.predict_proba(self.prepare_for_evaluation())[:, 0]