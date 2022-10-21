
from DataProcessor import DataParser

if __name__ == '__main__':
    dp = DataParser("data.csv", order_by=3)
    columns_numbers = [5, 6, 7, 8, 9]
    dp.clean_data(columns_numbers)
    dp.get_all_correlations(columns_numbers)
    dp.get_pdfs(columns_numbers)

