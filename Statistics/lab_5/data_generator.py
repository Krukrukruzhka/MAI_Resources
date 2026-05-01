import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict


def generate_time_series(n: int = 100, random_state: int = 42) -> Dict[str, np.ndarray]:
    np.random.seed(random_state)
    t = np.arange(1, n + 1, dtype=float)

    # epsilon ~ N(0, 1) — стандартный нормальный шум
    eps_standard = np.random.normal(0, 1, n)

    # epsilon ~ N(0, 0.5) — нормальный шум с sigma=0.5
    eps_small = np.random.normal(0, 0.5, n)

    series = {}

    # 1) x(t) = epsilon (просто шум)
    series["scenario_1_noise"] = eps_standard.copy()

    # 2) x(t) = 0.01t + epsilon
    series["scenario_2_weak_trend"] = 0.01 * t + eps_standard

    # 3) x(t) = -0.5t + epsilon
    series["scenario_3_strong_trend"] = -0.5 * t + eps_standard

    # 4) x(t) = 3 sin(2 pi t / 20) + epsilon, epsilon ~ N(0, 0.5)
    #    Период T=20, на n=100 точках — 5 полных периодов
    # Деление на 20 нужно для того, чтобы при целых t sin(2π·t) не вырождался в 0
    series["scenario_4_periodic"] = 3 * np.sin(2 * np.pi * t / 20) + eps_small

    # 5) Сценарий 1 с выбросом: одно значение заменяем на 50
    scenario_5 = series["scenario_1_noise"].copy()
    outlier_index = n // 2  # индекс 50 (середина ряда)
    scenario_5[outlier_index] = 50.0
    series["scenario_5_outlier"] = scenario_5

    return series


def save_time_series(series: Dict[str, np.ndarray], output_dir: str = "input_data") -> None:
    """
    Сохраняет временные ряды в CSV-файлы.

    Args:
        series: словарь с временными рядами
        output_dir: директория для сохранения
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    # Сохраняем все ряды в один файл
    n = len(next(iter(series.values())))
    df = pd.DataFrame({"t": np.arange(1, n + 1)})

    for name, values in series.items():
        df[name] = values

    filepath = path / "time_series.csv"
    df.to_csv(filepath, index=False)
    print(f"Временные ряды сохранены в {filepath}")

    return df


# Описания сценариев для подписей на графиках и в таблицах
SCENARIO_DESCRIPTIONS = {
    "scenario_1_noise": "x(t) = ε, ε ~ N(0,1) — белый шум",
    "scenario_2_weak_trend": "x(t) = 0.01t + ε — слабый тренд",
    "scenario_3_strong_trend": "x(t) = −0.5t + ε — сильный тренд",
    "scenario_4_periodic": "x(t) = 3sin(2πt/20) + ε, ε ~ N(0,0.5) — периодика",
    "scenario_5_outlier": "x(t) = ε с выбросом (x[50]=50)",
}

SCENARIO_SHORT_NAMES = {
    "scenario_1_noise": "Белый шум",
    "scenario_2_weak_trend": "Слабый тренд",
    "scenario_3_strong_trend": "Сильный тренд",
    "scenario_4_periodic": "Периодика",
    "scenario_5_outlier": "Шум + выброс",
}


if __name__ == "__main__":
    series = generate_time_series()
    save_time_series(series)
    print("Генерация данных завершена успешно!")
