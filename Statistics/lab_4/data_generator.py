import numpy as np
import pandas as pd


def generate_normal_distribution(mean, std, n=30):
    return np.random.normal(loc=mean, scale=std, size=n)

def create_dataset(sample1, sample2, sample3, file_path):
    max_length = max(len(sample1), len(sample2), len(sample3))

    # Создаем DataFrame с выравниванием по максимальной длине
    df = pd.DataFrame({
        'sample_1': np.pad(sample1, (0, max_length - len(sample1)), constant_values=np.nan),
        'sample_2': np.pad(sample2, (0, max_length - len(sample2)), constant_values=np.nan),
        'sample_3': np.pad(sample3, (0, max_length - len(sample3)), constant_values=np.nan)
    })

    df.to_csv(file_path, index=False)
    print(f"Датасет сохранен в файл: {file_path}")


# Пример использования
if __name__ == "__main__":

    # Первый датасет
    sample1 = generate_normal_distribution(mean=10, std=2)
    sample2 = generate_normal_distribution(mean=12, std=2)
    sample3 = generate_normal_distribution(mean=14, std=2)

    create_dataset(sample1, sample2, sample3, 'input_data/dataset_1.csv')

    # Четвертый датасет
    sample1 = generate_normal_distribution(mean=10, std=2)
    sample2 = generate_normal_distribution(mean=12, std=2)
    sample3 = generate_normal_distribution(mean=14, std=2)
    
    # Добавляем выбросы: в группу 1 - очень большой выброс, в группу 3 - очень маленький выброс
    sample1[10] = sample1[10] * np.std(sample1) * 5  # Очень большой выброс в группе 1
    sample3[-1] = sample3[-1] / (np.std(sample3) * 5)  # Очень маленький выброс в группе 3

    create_dataset(sample1, sample2, sample3, 'input_data/dataset_4.csv')

    # Второй датасет
    sample1 = generate_normal_distribution(mean=10, std=1)
    sample2 = generate_normal_distribution(mean=11, std=3)
    sample3 = generate_normal_distribution(mean=12, std=5)

    create_dataset(sample1, sample2, sample3, 'input_data/dataset_2.csv')

    # Третий датасет
    sample1 = generate_normal_distribution(mean=0, std=1)
    sample2 = generate_normal_distribution(mean=0, std=1)
    sample3 = generate_normal_distribution(mean=0, std=1)

    create_dataset(sample1, sample2, sample3, 'input_data/dataset_3.csv')
    
    print("Выборка 1 (mean=0, std=1):", sample1[:5])
    print("Выборка 2 (mean=5, std=2):", sample2[:5])
    print("Выборка 3 (mean=-3, std=0.5):", sample3[:5])