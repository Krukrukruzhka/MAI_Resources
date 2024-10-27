import pandas as pd

from sklearn.naive_bayes import GaussianNB


def data_preprocessing_nominal(data: pd.DataFrame):
    classes = {"hot": 2, "mild": 1, "cool": 0}
    data['temperature'] = data['temperature'].apply(lambda val: classes[val])
    classes = {"sunny": 2, "overcast": 1, "rainy": 0}
    data['outlook'] = data['outlook'].apply(lambda val: classes[val])
    classes = {"high": 2, "normal": 1, "low": 0}
    data['humidity'] = data['humidity'].apply(lambda val: classes[val])
    classes = {True: 1, False: 0}
    data['windy'] = data['windy'].apply(lambda val: classes[val])

    if 'play' in data:
        data['play'] = data['play'].apply(lambda val: 1 if val == 'yes' else 0)


def data_preprocessing_numeric(data: pd.DataFrame):
    classes = {"sunny": 2, "overcast": 1, "rainy": 0}
    data['outlook'] = data['outlook'].apply(lambda val: classes[val])
    classes = {True: 1, False: 0}
    data['windy'] = data['windy'].apply(lambda val: classes[val])

    if 'play' in data:
        data['play'] = data['play'].apply(lambda val: 1 if val == 'yes' else 0)


if __name__ == "__main__":
    path = "res/output/lab_1.1.xlsx"
    writer = pd.ExcelWriter(path, engine='xlsxwriter')

    # Data with nominal data
    nominal_data = pd.read_excel("res/input/weather.nominal.xlsx")  # changed cell B8 (from cool to mild)
    predict_data = pd.read_excel("res/input/weather.nominal.predict.xlsx")
    res_data = predict_data.copy()

    data_preprocessing_nominal(nominal_data)
    data_preprocessing_nominal(predict_data)

    model = GaussianNB()
    model.fit(nominal_data[['outlook', 'temperature', 'humidity', 'windy']], nominal_data['play'])

    res_data['play'] = model.predict(predict_data)
    res_data['play'] = res_data['play'].apply(lambda val: 'yes' if val else 'no')
    res_data.to_excel(writer, sheet_name="Nominal")

    # Data with numerical rows
    numeric_data = pd.read_excel("res/input/weather.numeric.xlsx")  # changed cell B8 (from 64 to 75)
    predict_data = pd.read_excel("res/input/weather.numeric.predict.xlsx")
    res_data = predict_data.copy()

    data_preprocessing_numeric(numeric_data)
    data_preprocessing_numeric(predict_data)

    model = GaussianNB()
    model.fit(numeric_data[['outlook', 'temperature', 'humidity', 'windy']], numeric_data['play'])

    res_data['play'] = model.predict(predict_data)
    res_data['play'] = res_data['play'].apply(lambda val: 'yes' if val else 'no')
    res_data.to_excel(writer, sheet_name="Numeric")

    writer.close()