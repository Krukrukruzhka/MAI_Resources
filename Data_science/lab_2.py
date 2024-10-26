import math
import pandas as pd

from matplotlib import pyplot as plt
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier


data = pd.read_csv("res/input/lab_2_titanic.csv")

print("\nUnique values in columns")
for column in data.columns:
    tabs = '\t' * math.ceil((3 * 4 - len(column) - 1) / 4)
    print(f"\t{column}: {tabs}{data[column].unique()}")

data['sex'] = data['sex'].apply(lambda val: 1 if val == 'male' else 0)
data['age'] = data['age'].apply(lambda val: 1 if val == 'adult' else 0)
data['survived'] = data['survived'].apply(lambda val: 1 if val == 'yes' else 0)

classes = {
    "1st": 1,
    "2nd": 0.5,
    "3rd": -0.5,
    "crew": -1
}
data['class'] = data['class'].apply(lambda val: classes[val])

model = DecisionTreeClassifier()
model.fit(X=data[['class', 'age', 'sex']], y=data['survived'])

fig = plt.figure(figsize=(10, 5))
_ = tree.plot_tree(
    model,
    feature_names=['class', 'age', 'sex'],
    filled=True
)
plt.show()
