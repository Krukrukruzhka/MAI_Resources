"""
Генератор данных для двухфакторного дисперсионного анализа.

Математическая модель отклика:
    Y_ij = mu + alpha_i + beta_j + epsilon_ij

где:
    mu       — общее среднее
    alpha_i  — эффект главного фактора A (i = 1..k)
    beta_j   — эффект мешающего фактора B (j = 1..n)
    epsilon  — случайная ошибка
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple


def generate_two_factor_data(
    mu: float,
    alpha: np.ndarray,
    beta: np.ndarray,
    noise_func,
    k: int,
    n: int,
    random_state: int = 42
) -> np.ndarray:
    """
    Генерирует матрицу наблюдений Y (k x n) по двухфакторной модели.

    Args:
        mu: общее среднее
        alpha: массив эффектов фактора A (длина k)
        beta: массив эффектов фактора B (длина n)
        noise_func: функция генерации шума, принимает (k, n) и возвращает матрицу
        k: число уровней фактора A
        n: число уровней фактора B (блоков)

    Returns:
        np.ndarray: матрица наблюдений размера (n, k) — строки = блоки, столбцы = уровни A
    """
    np.random.seed(random_state)

    # Матрица эффектов: mu + alpha_i + beta_j
    effects = mu + alpha[np.newaxis, :] + beta[:, np.newaxis]  # (n, k)

    # Случайные ошибки
    epsilon = noise_func(n, k)

    Y = effects + epsilon
    return Y


def normal_noise(mean: float = 0, std: float = 1.5):
    """Возвращает функцию генерации нормального шума."""
    def _noise(n, k):
        return np.random.normal(loc=mean, scale=std, size=(n, k))
    return _noise


def laplace_noise(mean: float = 0, scale: float = 1.5):
    """Возвращает функцию генерации шума с распределением Лапласа (тяжёлые хвосты)."""
    def _noise(n, k):
        return np.random.laplace(loc=mean, scale=scale, size=(n, k))
    return _noise


def generate_scenario_1(random_state: int = 42) -> Tuple[np.ndarray, Dict]:
    """
    Сценарий 1: Нормальный шум, умеренные эффекты A и B.

    B: 0, +2, +4, +6, +8, +10, +12, +14
    A: 0, +3, +6, +9
    epsilon: N(0, 1.5)
    mu: 20
    """
    params = {
        'name': 'Сценарий 1',
        'description': 'Нормальный шум (σ=1.5), эффекты A=[0,3,6,9], B=[0,2,...,14], μ=20',
        'mu': 20,
        'alpha': np.array([0, 3, 6, 9]),
        'beta': np.array([0, 2, 4, 6, 8, 10, 12, 14]),
        'noise_type': 'N(0, 1.5)',
        'k': 4,
        'n': 8,
    }

    Y = generate_two_factor_data(
        mu=params['mu'],
        alpha=params['alpha'],
        beta=params['beta'],
        noise_func=normal_noise(0, 1.5),
        k=params['k'],
        n=params['n'],
        random_state=random_state
    )

    return Y, params


def generate_scenario_2(random_state: int = 43) -> Tuple[np.ndarray, Dict]:
    """
    Сценарий 2: Нормальный шум, сильные эффекты B, слабые эффекты A.

    B: 0, +5, +10, +15, +20, +25, +30, +35
    A: 0, +2, +4, +6
    epsilon: N(0, 2)
    mu: 20
    """
    params = {
        'name': 'Сценарий 2',
        'description': 'Нормальный шум (σ=2), эффекты A=[0,2,4,6], B=[0,5,...,35], μ=20',
        'mu': 20,
        'alpha': np.array([0, 2, 4, 6]),
        'beta': np.array([0, 5, 10, 15, 20, 25, 30, 35]),
        'noise_type': 'N(0, 2)',
        'k': 4,
        'n': 8,
    }

    Y = generate_two_factor_data(
        mu=params['mu'],
        alpha=params['alpha'],
        beta=params['beta'],
        noise_func=normal_noise(0, 2.0),
        k=params['k'],
        n=params['n'],
        random_state=random_state
    )

    return Y, params


def generate_scenario_3(random_state: int = 44) -> Tuple[np.ndarray, Dict]:
    """
    Сценарий 3: Шум Лапласа (тяжёлые хвосты) + выброс.

    B: 0, +2, +4, +6, +8, +10, +12, +14
    A: 0, +3, +6, +9
    epsilon: Laplace(0, 1.5) + выброс в ячейке (блок 3, уровень A=2) * 5
    mu: 20
    """
    params = {
        'name': 'Сценарий 3',
        'description': 'Шум Лапласа + выброс в ячейке (блок=3, A=2)×5, эффекты A=[0,3,6,9], B=[0,2,...,14], μ=20',
        'mu': 20,
        'alpha': np.array([0, 3, 6, 9]),
        'beta': np.array([0, 2, 4, 6, 8, 10, 12, 14]),
        'noise_type': 'Laplace(0, 1.5) + выброс',
        'k': 4,
        'n': 8,
    }

    Y = generate_two_factor_data(
        mu=params['mu'],
        alpha=params['alpha'],
        beta=params['beta'],
        noise_func=laplace_noise(0, 1.5),
        k=params['k'],
        n=params['n'],
        random_state=random_state
    )

    # Добавляем выброс: третий блок (индекс 2), второй уровень A (индекс 1)
    # Увеличиваем значение в 5 раз
    Y[2, 1] *= 5
    params['outlier'] = {'block': 2, 'level_a': 1, 'multiplier': 5}

    return Y, params


def generate_scenario_4(random_state: int = 45) -> Tuple[np.ndarray, Dict]:
    """
    Сценарий 4: Нулевой эффект фактора A (H0 верна).

    B: 0, +2, +4, +6, +8, +10, +12, +14
    A: 0, 0, 0, 0
    epsilon: N(0, 1.5)
    mu: 20
    """
    params = {
        'name': 'Сценарий 4',
        'description': 'Нормальный шум (σ=1.5), A=[0,0,0,0] (нет эффекта), B=[0,2,...,14], μ=20',
        'mu': 20,
        'alpha': np.array([0, 0, 0, 0]),
        'beta': np.array([0, 2, 4, 6, 8, 10, 12, 14]),
        'noise_type': 'N(0, 1.5)',
        'k': 4,
        'n': 8,
    }

    Y = generate_two_factor_data(
        mu=params['mu'],
        alpha=params['alpha'],
        beta=params['beta'],
        noise_func=normal_noise(0, 1.5),
        k=params['k'],
        n=params['n'],
        random_state=random_state
    )

    return Y, params


def matrix_to_dataframe(Y: np.ndarray, k: int, n: int) -> pd.DataFrame:
    """
    Преобразует матрицу наблюдений в DataFrame.

    Args:
        Y: матрица (n, k)
        k: число уровней фактора A
        n: число уровней фактора B (блоков)

    Returns:
        pd.DataFrame с колонками: block, level_A, value
    """
    rows = []
    for j in range(n):
        for i in range(k):
            rows.append({
                'block': j + 1,
                'level_A': i + 1,
                'value': Y[j, i]
            })
    return pd.DataFrame(rows)


def save_scenario_data(Y: np.ndarray, params: Dict, filename: str):
    """Сохраняет данные сценария в CSV."""
    input_dir = Path("input_data")
    input_dir.mkdir(parents=True, exist_ok=True)

    df = matrix_to_dataframe(Y, params['k'], params['n'])
    filepath = input_dir / filename
    df.to_csv(filepath, index=False)
    print(f"  Данные сохранены: {filepath}")

    # Также сохраняем матричный вид
    matrix_df = pd.DataFrame(
        Y,
        index=[f"Block_{j+1}" for j in range(params['n'])],
        columns=[f"A_{i+1}" for i in range(params['k'])]
    )
    matrix_filepath = input_dir / filename.replace('.csv', '_matrix.csv')
    matrix_df.to_csv(matrix_filepath)
    print(f"  Матрица сохранена: {matrix_filepath}")

    return df


def generate_all_scenarios() -> Dict[str, Tuple[np.ndarray, Dict]]:
    """Генерирует данные для всех 4 сценариев."""
    scenarios = {}

    print("Генерация данных для сценариев двухфакторного анализа:")
    print("=" * 60)

    for i, gen_func in enumerate([
        generate_scenario_1,
        generate_scenario_2,
        generate_scenario_3,
        generate_scenario_4
    ], start=1):
        Y, params = gen_func()
        scenario_key = f"scenario_{i}"
        scenarios[scenario_key] = (Y, params)

        print(f"\n{params['name']}: {params['description']}")
        print(f"  Размер матрицы: {Y.shape} (блоков × уровней A)")
        print(f"  Диапазон значений: [{Y.min():.2f}, {Y.max():.2f}]")
        print(f"  Среднее: {Y.mean():.2f}")

        save_scenario_data(Y, params, f"{scenario_key}.csv")

    return scenarios


if __name__ == "__main__":
    scenarios = generate_all_scenarios()
    print("\nГенерация данных завершена!")
