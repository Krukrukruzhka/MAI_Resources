import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.mixture import GaussianMixture


def preprocessing(data: pd.DataFrame) -> None:
    data['target'] = data['target'].astype(int)


def show_centroids(data: pd.DataFrame, labels: np.ndarray, centers: np.ndarray, method: str):
    n = len(data.columns) - 1
    print(f'{method} method', '\n', centers, end='\n'*2)

    fig, axes = plt.subplots(nrows=n - 1, ncols=n - 1, figsize=(14, 6))
    for i in range(1, n):
        for j in range(i):
            axes[i - 1][j].scatter(data.iloc[:, i], data.iloc[:, j], c=labels)
            axes[i - 1][j].scatter(centers[:, i], centers[:, j], s=300, c='red', marker='X')
    fig.suptitle(f'Centroids using {method} method')
    plt.show()


def use_kmeans(data: pd.DataFrame, clusters_count: int, seed: int):
    assert 'target' in data.columns, "Column 'target' not exists in dataset"

    kmeans = KMeans(n_clusters=clusters_count, random_state=seed)
    kmeans.fit(data.drop('target', axis=1))

    show_centroids(data=data, labels=kmeans.labels_, centers=kmeans.cluster_centers_, method='K-Means')

    return kmeans.labels_


def use_EM(data: pd.DataFrame, clusters_count: int, seed: int):
    assert 'target' in data.columns, "Column 'target' not exists in dataset"

    em = GaussianMixture(n_components=clusters_count, random_state=seed)
    em.fit(data.drop('target', axis=1))

    labels = em.predict(data.drop('target', axis=1))
    show_centroids(data=data, labels=labels, centers=em.means_, method='EM')

    return labels


def convert_predictions(prediction: np.ndarray) -> np.ndarray:
    vals = {
        0: 2,
        1: 0,
        2: 1
    }
    return np.array([vals[val] for val in prediction])


if __name__ == "__main__":
    # Load and preprocessing data
    iris_data = load_iris()  # Can't convert iris.arff to iris.xlsx, so I try load this dataset from sklearn
    iris_data = pd.DataFrame(data=np.c_[iris_data['data'], iris_data['target']],
                             columns=iris_data['feature_names'] + ['target'])
    preprocessing(iris_data)

    # Base analyse
    print(iris_data.describe(), end="\n"*3)
    show_centroids(data=iris_data, labels=iris_data['target'], centers=iris_data.groupby('target').mean().to_numpy(), method="None")

    # Model predictions
    kmeans_predict = convert_predictions(use_kmeans(iris_data, 3, 10))
    em_predict = convert_predictions(use_EM(iris_data, 3, 10))

    print(f"\nBase labels\n{iris_data['target'].to_numpy()}\n")
    print(f"EM labels\n{em_predict}\n")
    print(f"K-Mean labels\n{kmeans_predict}\n")
