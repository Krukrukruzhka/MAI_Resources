import numpy as np
import pandas as pd
from typing import Tuple, Dict, List


def generate_samples(n: int = 1000, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Генерирует две независимые выборки X и Z
    
    Args:
        n: размер выборки
        random_state: seed для воспроизводимости
        
    Returns:
        Tuple: (X, Z) где X ~ N(0,1), Z ~ N(5,2)
    """
    np.random.seed(random_state)
    
    X = np.random.normal(0, 1, n)  # N(0,1)
    Z = np.random.normal(5, 2, n)  # N(5,2)
    
    return X, Z


def calculate_linear_dependency(X: np.ndarray, Z: np.ndarray, a: float) -> np.ndarray:
    """
    Вычисляет линейную зависимость Y = aX + (1-a)Z
    
    Args:
        X: первая выборка
        Z: вторая выборка
        a: коэффициент линейной комбинации
        
    Returns:
        np.ndarray: значения Y
    """
    return a * X + (1 - a) * Z


def calculate_cubic_dependency(X: np.ndarray, Z: np.ndarray) -> np.ndarray:
    """
    Вычисляет кубическую зависимость Y = 0.05X³ + 4Z
    
    Args:
        X: первая выборка
        Z: вторая выборка
        
    Returns:
        np.ndarray: значения Y
    """
    return 0.05 * (X ** 3) + 4 * Z


def calculate_quadratic_dependency(X: np.ndarray, Z: np.ndarray) -> np.ndarray:
    """
    Вычисляет квадратичную зависимость Y = X² + Z
    
    Args:
        X: первая выборка
        Z: вторая выборка
        
    Returns:
        np.ndarray: значения Y
    """
    return X ** 2 + Z


def add_outliers(data: np.ndarray, n_outliers: int = 2, multiplier: float = 10) -> np.ndarray:
    """
    Добавляет выбросы в данные
    
    Args:
        data: исходные данные
        n_outliers: количество выбросов
        multiplier: множитель для создания выбросов
        
    Returns:
        np.ndarray: данные с выбросами
    """
    data_with_outliers = data.copy()
    
    # Выбираем случайные индексы для выбросов
    outlier_indices = np.random.choice(len(data), n_outliers, replace=False)
    
    # Создаем выбросы как экстремальные значения
    for idx in outlier_indices:
        # Увеличиваем значение в multiplier раз
        data_with_outliers[idx] = data[idx] * multiplier
    
    return data_with_outliers


def create_all_dependencies(X: np.ndarray, Z: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Создает все типы зависимостей для анализа
    
    Args:
        X: первая выборка
        Z: вторая выборка
        
    Returns:
        Dict: словарь с различными зависимостями Y
    """
    dependencies = {}
    
    # Линейные зависимости с разными коэффициентами
    a_values = [0, 0.25, 0.5, 0.75, 1]
    for a in a_values:
        dependencies[f'linear_a{a}'] = calculate_linear_dependency(X, Z, a)
    
    # Кубическая зависимость
    dependencies['cubic'] = calculate_cubic_dependency(X, Z)
    
    # Квадратичная зависимость
    dependencies['quadratic'] = calculate_quadratic_dependency(X, Z)
    
    return dependencies


def create_dataframe_with_dependencies(X: np.ndarray, Z: np.ndarray) -> pd.DataFrame:
    """
    Создает DataFrame со всеми зависимостями
    
    Args:
        X: первая выборка
        Z: вторая выборка
        
    Returns:
        pd.DataFrame: DataFrame с исходными данными и зависимостями
    """
    dependencies = create_all_dependencies(X, Z)
    
    # Создаем DataFrame
    df = pd.DataFrame({
        'X': X,
        'Z': Z
    })
    
    # Добавляем все зависимости
    for dep_name, dep_values in dependencies.items():
        df[dep_name] = dep_values
    
    return df


def save_data_to_csv(df: pd.DataFrame, filename: str):
    """
    Сохраняет данные в CSV файл
    
    Args:
        df: DataFrame с данными
        filename: имя файла для сохранения
    """
    df.to_csv(f'input_data/{filename}', index=False)


if __name__ == "__main__":
    # Пример использования
    X, Z = generate_samples(1000)
    df = create_dataframe_with_dependencies(X, Z)
    save_data_to_csv(df, 'generated_data.csv')
    print("Данные успешно сгенерированы и сохранены")