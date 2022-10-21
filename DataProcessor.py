import csv

import numpy as np
from matplotlib import pyplot as plt

from CONST_VALUES import ConstantsValues


class Record:
    last_id = 0

    def __init__(self, **kwargs):
        self.id = ConstantsValues.LAST_ID
        ConstantsValues.LAST_ID += 1
        for argument, value in kwargs.items():
            setattr(self, argument.replace(" ", "_"), value)


class DataParser:
    def __init__(self, file_name, order_by=None):
        with open(file_name, 'rt') as file:
            data = csv.reader(file, delimiter=',')
            if order_by:
                data = sorted(data, key=lambda row: row[order_by], reverse=False)
            self.headers = [header.replace(" ", "_") for header in data[-1]]

            def generate_template_for_args(record_raw_data):
                template = {}
                for i, elem in enumerate(record_raw_data):
                    try:
                        template.update({self.headers[i]: float(elem)})
                    except ValueError:
                        template.update({self.headers[i]: elem})
                return template

            self.records = [Record(**generate_template_for_args(raw_record)) for raw_record in data[:-1]]

    def get_stats_for_field(self, field_name) -> dict:

        values = [float(getattr(record, field_name)) for record in self.records]
        return {"median": np.median(values), "average": np.average(values),
                "min_value": min(values), "max_value": max(values), "range": np.ptp(values),
                "standard_deviation": np.std(values), "variance": np.var(values),
                "90_perc": np.percentile(values, 90), "histogram": np.histogram(values)}

    def clean_data(self, interesting_columns: list):
        for i, header in enumerate(self.headers):
            if i in interesting_columns:
                if type(getattr(self.records[0], header)) is float:
                    median = self.get_stats_for_field(header)["median"]
                    border_1 = median * (1 - ConstantsValues.DISTANCE_TOLERANCE)
                    border_2 = median * (1 + ConstantsValues.DISTANCE_TOLERANCE)
                    self.records = [record for record in self.records if border_1 < getattr(record, header) < border_2]

    @classmethod
    def ncorrelate(cls, a, b):
        '''Funkcja zwraca unormowaną wartość korelacji'''
        a = (a - np.mean(a)) / (np.std(a) * len(a))
        b = (b - np.mean(b)) / np.std(b)
        return np.correlate(a, b)[0]

    def get_all_correlations(self, interesting_fields: list):
        interesting_headers = []
        for i, header in enumerate(self.headers):
            if i in interesting_fields:
                interesting_headers.append(header)
        for k in interesting_headers:
            v = [getattr(record, k) for record in self.records]
            for k_1 in interesting_headers:
                v_2 = [getattr(record, k_1) for record in self.records]
                correlation = self.ncorrelate(v, v_2)
                if correlation >= 0.5 or correlation <= -0.5:
                    print("strong correlation\n")
                elif 0.2 >= correlation >= -0.2:
                    print("weak correlation\n")
                else:
                    print("medium correlation\n")
                print(f"{k} correlates to {k_1} by {correlation}\n")

    def get_pdfs(self, interesting_fields: list):
        interesting_headers = []
        for i, header in enumerate(self.headers):
            if i in interesting_fields:
                interesting_headers.append(header)
        for header in interesting_headers:
            data_set = [getattr(record, header) for record in self.records]
            stats = self.get_stats_for_field(header)
            plt.hist(data_set, 100)
            plt.title('Histogram dla: ' + header)
            plt.xlabel('Przedział')
            plt.ylabel('Liczba obserwacji')
            name = header.replace("/", "_")
            plt.savefig(f'{name}.pdf')
            self.append_pdf(f"{name}-stats.pdf", str(stats))

    @classmethod
    def append_pdf(cls, file_name, text):
        from fpdf import FPDF

        pdf = FPDF()

        pdf.add_page()

        pdf.set_font("Arial", size=15)

        # create a cell
        cells = 1
        for elem in text.split(","):
            pdf.cell(200, 10, txt=elem,
                     ln=cells, align='C')
            cells += 1

        pdf.output(file_name)
