import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from typing import Dict

# Попытка импорта statsmodels для критерия Вальда-Вольфовица
try:
    from statsmodels.sandbox.stats.runs import runstest_1samp
    _HAS_STATSMODELS = True
except ImportError:
    _HAS_STATSMODELS = False


# ============================================================
# 1. Критерий инверсий
# ============================================================

def inversion_test(x: np.ndarray, alpha: float = 0.05) -> Dict:
    """
    Критерий инверсий для проверки случайности временного ряда.

    Инверсия — пара (i, j), где i < j, но x[i] > x[j].
    При случайном ряде число инверсий A приближённо нормально:
        E[A] = n(n-1)/4
        D[A] = n(n-1)(2n+5)/72

    H₀: ряд случаен (нет тренда)
    H₁: ряд не случаен (есть тренд)

    Args:
        x: временной ряд
        alpha: уровень значимости

    Returns:
        Dict с результатами теста
    """
    n = len(x)

    # Подсчёт числа инверсий
    A = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            if x[i] > x[j]:
                A += 1

    # Математическое ожидание и дисперсия
    E_A = n * (n - 1) / 4
    D_A = n * (n - 1) * (2 * n + 5) / 72

    # Z-статистика
    z = (A - E_A) / np.sqrt(D_A)

    # Двусторонний p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Критическое значение
    z_crit = stats.norm.ppf(1 - alpha / 2)

    return {
        "test_name": "Критерий инверсий",
        "statistic_name": "A (число инверсий)",
        "statistic_value": A,
        "expected_value": E_A,
        "variance": D_A,
        "z_statistic": z,
        "z_critical": z_crit,
        "p_value": p_value,
        "reject_H0": p_value < alpha,
        "conclusion": "Ряд НЕ случаен (тренд)" if p_value < alpha else "Ряд случаен",
    }


# ============================================================
# 2. Сериальный критерий Вальда-Вольфовица
# ============================================================

def wald_wolfowitz_test(x: np.ndarray, alpha: float = 0.05) -> Dict:
    """
    Сериальный критерий Вальда-Вольфовица (runs test).

    Серия — последовательность элементов, лежащих по одну сторону от медианы.
    Число серий R при случайном ряде приближённо нормально:
        E[R] = 2*n1*n2 / n + 1
        D[R] = 2*n1*n2*(2*n1*n2 - n) / (n²*(n-1))

    H₀: ряд случаен
    H₁: ряд не случаен

    Args:
        x: временной ряд
        alpha: уровень значимости

    Returns:
        Dict с результатами теста
    """
    n = len(x)
    median = np.median(x)

    # Бинаризация: выше медианы = 1, ниже = 0
    # Элементы, равные медиане, относим к «выше»
    binary = (x >= median).astype(int)

    # Подсчёт серий
    R = 1  # первый элемент — начало первой серии
    for i in range(1, n):
        if binary[i] != binary[i - 1]:
            R += 1

    # Число элементов выше и ниже медианы
    n1 = int(np.sum(binary))
    n2 = n - n1

    # Защита от вырожденного случая
    if n1 == 0 or n2 == 0:
        return {
            "test_name": "Критерий Вальда-Вольфовица",
            "statistic_name": "R (число серий)",
            "statistic_value": R,
            "expected_value": np.nan,
            "variance": np.nan,
            "z_statistic": np.nan,
            "z_critical": np.nan,
            "p_value": np.nan,
            "reject_H0": False,
            "conclusion": "Невозможно применить (все значения по одну сторону от медианы)",
        }

    # Математическое ожидание и дисперсия
    E_R = (2 * n1 * n2) / n + 1
    D_R = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n ** 2 * (n - 1))

    # Z-статистика
    z = (R - E_R) / np.sqrt(D_R) if D_R > 0 else 0.0

    # Двусторонний p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Критическое значение
    z_crit = stats.norm.ppf(1 - alpha / 2)

    return {
        "test_name": "Критерий Вальда-Вольфовица",
        "statistic_name": "R (число серий)",
        "statistic_value": R,
        "expected_value": E_R,
        "variance": D_R,
        "z_statistic": z,
        "z_critical": z_crit,
        "p_value": p_value,
        "reject_H0": p_value < alpha,
        "conclusion": "Ряд НЕ случаен" if p_value < alpha else "Ряд случаен",
    }


# ============================================================
# 3. Критерий Рамачандрана-Ранганатана
# ============================================================

def ramachandran_ranganathan_test(x: np.ndarray, alpha: float = 0.05) -> Dict:
    """
    Критерий Рамачандрана-Ранганатана для проверки случайности.

    Основан на числе «восходящих серий» (runs up).
    Восходящая серия — максимальная подпоследовательность x[i] < x[i+1] < ... < x[i+k].
    Число восходящих серий S при случайном ряде приближённо нормально:
        E[S] = (2n - 1) / 3
        D[S] = (16n - 29) / 90

    H₀: ряд случаен
    H₁: ряд не случаен

    Args:
        x: временной ряд
        alpha: уровень значимости

    Returns:
        Dict с результатами теста
    """
    n = len(x)

    # Подсчёт числа восходящих серий (runs up and down)
    S = 1  # первый элемент начинает первую серию
    for i in range(1, n - 1):
        # Новая серия начинается, когда меняется направление
        if (x[i] - x[i - 1]) * (x[i + 1] - x[i]) < 0:
            S += 1
        elif x[i] == x[i - 1] or x[i + 1] == x[i]:
            # Равные элементы тоже могут прерывать серию
            S += 1

    # Математическое ожидание и дисперсия числа серий вверх-вниз
    E_S = (2 * n - 1) / 3
    D_S = (16 * n - 29) / 90

    # Z-статистика
    z = (S - E_S) / np.sqrt(D_S) if D_S > 0 else 0.0

    # Двусторонний p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Критическое значение
    z_crit = stats.norm.ppf(1 - alpha / 2)

    return {
        "test_name": "Критерий Рамачандрана-Ранганатана",
        "statistic_name": "S (число серий вверх-вниз)",
        "statistic_value": S,
        "expected_value": E_S,
        "variance": D_S,
        "z_statistic": z,
        "z_critical": z_crit,
        "p_value": p_value,
        "reject_H0": p_value < alpha,
        "conclusion": "Ряд НЕ случаен" if p_value < alpha else "Ряд случаен",
    }


# ============================================================
# 4. Критерий серий знаков первых разностей
# ============================================================

def sign_difference_series_test(x: np.ndarray, alpha: float = 0.05) -> Dict:
    """
    Критерий серий знаков первых разностей.

    Вычисляем первые разности d[i] = x[i+1] - x[i] и их знаки:
        s[i] = +1 если d[i] > 0, -1 если d[i] < 0, 0 если d[i] = 0.
    Серия — последовательность одинаковых знаков.
    Число серий R и максимальная длина серии L_max проверяются:
        E[R] = (2(n-1) - 1) / 3
        D[R] = (16(n-1) - 29) / 90

    Также проверяется максимальная длина серии:
        L_max < L_crit, где L_crit ≈ ceil(log2(n-1)) при α=0.05

    H₀: ряд случаен
    H₁: ряд не случаен (есть тренд или периодичность)

    Args:
        x: временной ряд
        alpha: уровень значимости

    Returns:
        Dict с результатами теста
    """
    n = len(x)

    # Первые разности
    diffs = np.diff(x)

    # Знаки первых разностей (исключаем нулевые)
    signs = np.sign(diffs)
    # Заменяем нули на предыдущий знак (или +1 если первый)
    for i in range(len(signs)):
        if signs[i] == 0:
            signs[i] = signs[i - 1] if i > 0 else 1

    m = len(signs)  # m = n - 1

    # Подсчёт числа серий
    R = 1
    series_lengths = [1]
    for i in range(1, m):
        if signs[i] != signs[i - 1]:
            R += 1
            series_lengths.append(1)
        else:
            series_lengths[-1] += 1

    # Максимальная длина серии
    L_max = max(series_lengths) if series_lengths else 0

    # Математическое ожидание и дисперсия числа серий
    E_R = (2 * m - 1) / 3
    D_R = (16 * m - 29) / 90

    # Z-статистика для числа серий
    z_R = (R - E_R) / np.sqrt(D_R) if D_R > 0 else 0.0

    # p-value для числа серий
    p_value_R = 2 * (1 - stats.norm.cdf(abs(z_R)))

    # Критическое значение для максимальной длины серии
    L_crit = int(np.ceil(np.log2(m))) if m > 0 else 1

    # Критическое значение z
    z_crit = stats.norm.ppf(1 - alpha / 2)

    # Итоговое решение: отвергаем H₀, если хотя бы один из критериев сработал
    reject_by_R = p_value_R < alpha
    reject_by_L = L_max >= L_crit

    reject_H0 = reject_by_R or reject_by_L

    conclusion_parts = []
    if reject_by_R:
        conclusion_parts.append(f"число серий R={R} (p={p_value_R:.4f})")
    if reject_by_L:
        conclusion_parts.append(f"макс. длина серии L={L_max} ≥ L_crit={L_crit}")

    if reject_H0:
        conclusion = "Ряд НЕ случаен: " + "; ".join(conclusion_parts)
    else:
        conclusion = f"Ряд случаен (R={R}, L_max={L_max} < L_crit={L_crit})"

    return {
        "test_name": "Критерий серий знаков первых разностей",
        "statistic_name": "R (число серий) / L_max",
        "statistic_value": R,
        "expected_value": E_R,
        "variance": D_R,
        "z_statistic": z_R,
        "z_critical": z_crit,
        "p_value": p_value_R,
        "reject_H0": reject_H0,
        "L_max": L_max,
        "L_crit": L_crit,
        "reject_by_R": reject_by_R,
        "reject_by_L": reject_by_L,
        "conclusion": conclusion,
    }


# ============================================================
# Применение всех тестов к набору временных рядов
# ============================================================

def apply_all_tests(
    series: Dict[str, np.ndarray], alpha: float = 0.05
) -> pd.DataFrame:
    """
    Применяет все 4 критерия ко всем временным рядам.

    Args:
        series: словарь {название_сценария: массив_значений}
        alpha: уровень значимости

    Returns:
        pd.DataFrame: сводная таблица результатов
    """
    tests = [
        ("Критерий инверсий", inversion_test),
        ("Критерий Вальда-Вольфовица", wald_wolfowitz_test),
        ("Критерий Рамачандрана-Ранганатана", ramachandran_ranganathan_test),
        ("Критерий серий знаков первых разностей", sign_difference_series_test),
    ]

    rows = []
    for scenario_name, x in series.items():
        for test_name, test_func in tests:
            result = test_func(x, alpha)
            rows.append(
                {
                    "scenario": scenario_name,
                    "test": test_name,
                    "statistic": result["statistic_value"],
                    "expected": result["expected_value"],
                    "z_statistic": result["z_statistic"],
                    "p_value": result["p_value"],
                    "reject_H0": result["reject_H0"],
                    "conclusion": result["conclusion"],
                }
            )

    return pd.DataFrame(rows)


def save_test_results(results_df: pd.DataFrame, filename: str = "test_results.csv") -> None:
    """
    Сохраняет результаты тестов в CSV.

    Args:
        results_df: DataFrame с результатами
        filename: имя файла
    """
    output_dir = Path("output_data/result_tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    results_df.to_csv(filepath, index=False)
    print(f"Результаты тестов сохранены в {filepath}")


def print_test_summary(results_df: pd.DataFrame, scenario_descriptions: Dict[str, str]) -> None:
    """
    Выводит сводку результатов тестов в консоль.

    Args:
        results_df: DataFrame с результатами
        scenario_descriptions: описания сценариев
    """
    scenarios = results_df["scenario"].unique()

    for scenario in scenarios:
        desc = scenario_descriptions.get(scenario, scenario)
        print(f"\n{'─' * 60}")
        print(f"  {desc}")
        print(f"{'─' * 60}")

        scenario_results = results_df[results_df["scenario"] == scenario]
        for _, row in scenario_results.iterrows():
            symbol = "✗ H₀ отвергнута" if row["reject_H0"] else "✓ H₀ принята"
            p_str = f"p={row['p_value']:.4f}" if not np.isnan(row["p_value"]) else "p=N/A"
            print(f"  {row['test']:45s} | {p_str:12s} | {symbol}")


if __name__ == "__main__":
    from data_generator import generate_time_series, SCENARIO_DESCRIPTIONS

    series = generate_time_series()
    results = apply_all_tests(series)
    print_test_summary(results, SCENARIO_DESCRIPTIONS)
    save_test_results(results)
    print("\nТестирование завершено!")
