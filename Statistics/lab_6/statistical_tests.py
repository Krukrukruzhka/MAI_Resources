"""
Статистические критерии для двухфакторного дисперсионного анализа.

Реализованы:
    - Критерий Фридмана (непараметрический, двухфакторный)
    - Критерий Пейджа (непараметрический, двухфакторный, упорядоченная альтернатива)
    - Критерий Фишера двухфакторный (параметрический, ANOVA без повторений)
    - Критерий Фишера однофакторный (параметрический, one-way ANOVA)
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional


# ============================================================
# Критерий Фридмана
# ============================================================

def friedman_test(Y: np.ndarray) -> Dict:
    """
    Критерий Фридмана для двухфакторного анализа.

    Проверяет H0: эффекты всех уровней фактора A одинаковы.
    Непараметрический аналог двухфакторного ANOVA.

    Args:
        Y: матрица наблюдений (n x k), строки — блоки, столбцы — уровни A

    Returns:
        Dict с результатами теста
    """
    n, k = Y.shape

    # Ранжируем внутри каждого блока (строки)
    ranks = np.zeros_like(Y, dtype=float)
    for j in range(n):
        ranks[j, :] = stats.rankdata(Y[j, :])

    # Суммы рангов по столбцам (уровням A)
    R = ranks.sum(axis=0)  # длина k

    # Среднее ранга
    R_mean = (k + 1) / 2

    # Статистика Фридмана
    SS_treatments = n * np.sum((R / n - R_mean) ** 2)
    chi2_stat = 12 * n / (k * (k + 1)) * np.sum((R / n - R_mean) ** 2)

    # Степени свободы
    df = k - 1

    # p-value из распределения хи-квадрат
    p_value = 1 - stats.chi2.cdf(chi2_stat, df)

    # Также используем scipy для проверки
    scipy_stat, scipy_p = stats.friedmanchisquare(*[Y[:, i] for i in range(k)])

    return {
        'test_name': 'Критерий Фридмана',
        'statistic': chi2_stat,
        'p_value': p_value,
        'df': df,
        'rank_sums': R,
        'rank_means': R / n,
        'scipy_statistic': scipy_stat,
        'scipy_p_value': scipy_p,
        'significant_005': p_value < 0.05,
        'significant_001': p_value < 0.01,
    }


# ============================================================
# Критерий Пейджа
# ============================================================

def page_test(Y: np.ndarray) -> Dict:
    """
    Критерий Пейджа для упорядоченной альтернативы.

    Проверяет H0: эффекты всех уровней фактора A одинаковы
    против H1: эффекты монотонно возрастают (alpha_1 <= alpha_2 <= ... <= alpha_k,
    хотя бы одно неравенство строгое).

    Args:
        Y: матрица наблюдений (n x k), столбцы должны быть упорядочены
           по предполагаемому возрастанию эффекта

    Returns:
        Dict с результатами теста
    """
    n, k = Y.shape

    # Ранжируем внутри каждого блока
    ranks = np.zeros_like(Y, dtype=float)
    for j in range(n):
        ranks[j, :] = stats.rankdata(Y[j, :])

    # Суммы рангов по столбцам
    R = ranks.sum(axis=0)

    # Статистика Пейджа: L = sum(i * R_i), i = 1, 2, ..., k
    i_values = np.arange(1, k + 1)
    L = np.sum(i_values * R)

    # Ожидаемое значение и дисперсия при H0
    E_L = n * k * (k + 1) ** 2 / 4
    Var_L = n * k ** 2 * (k + 1) * (k ** 2 - 1) / 144

    # Z-статистика (нормальное приближение)
    Z = (L - E_L) / np.sqrt(Var_L)

    # Односторонний p-value (правый хвост, т.к. H1: возрастание)
    p_value = 1 - stats.norm.cdf(Z)

    return {
        'test_name': 'Критерий Пейджа',
        'L_statistic': L,
        'E_L': E_L,
        'Var_L': Var_L,
        'Z_statistic': Z,
        'p_value': p_value,
        'rank_sums': R,
        'significant_005': p_value < 0.05,
        'significant_001': p_value < 0.01,
    }


# ============================================================
# Двухфакторный критерий Фишера (ANOVA без повторений)
# ============================================================

def two_way_anova(Y: np.ndarray) -> Dict:
    """
    Двухфакторный дисперсионный анализ (ANOVA без повторений).

    Модель: Y_ij = mu + alpha_i + beta_j + epsilon_ij

    Args:
        Y: матрица наблюдений (n x k), строки — блоки (B), столбцы — уровни A

    Returns:
        Dict с результатами ANOVA
    """
    n, k = Y.shape
    N = n * k

    # Общее среднее
    Y_bar = Y.mean()

    # Средние по столбцам (уровни A)
    Y_bar_col = Y.mean(axis=0)  # длина k

    # Средние по строкам (блоки B)
    Y_bar_row = Y.mean(axis=1)  # длина n

    # Суммы квадратов
    SS_total = np.sum((Y - Y_bar) ** 2)
    SS_A = n * np.sum((Y_bar_col - Y_bar) ** 2)       # эффект фактора A
    SS_B = k * np.sum((Y_bar_row - Y_bar) ** 2)       # эффект фактора B (блоков)
    SS_error = SS_total - SS_A - SS_B                   # остаточная

    # Степени свободы
    df_A = k - 1
    df_B = n - 1
    df_error = (k - 1) * (n - 1)
    df_total = N - 1

    # Средние квадраты
    MS_A = SS_A / df_A if df_A > 0 else 0
    MS_B = SS_B / df_B if df_B > 0 else 0
    MS_error = SS_error / df_error if df_error > 0 else 0

    # F-статистики
    F_A = MS_A / MS_error if MS_error > 0 else np.inf
    F_B = MS_B / MS_error if MS_error > 0 else np.inf

    # p-values
    p_value_A = 1 - stats.f.cdf(F_A, df_A, df_error)
    p_value_B = 1 - stats.f.cdf(F_B, df_B, df_error)

    # Таблица ANOVA
    anova_table = pd.DataFrame({
        'Источник': ['Фактор A', 'Фактор B (блоки)', 'Остаток', 'Итого'],
        'SS': [SS_A, SS_B, SS_error, SS_total],
        'df': [df_A, df_B, df_error, df_total],
        'MS': [MS_A, MS_B, MS_error, np.nan],
        'F': [F_A, F_B, np.nan, np.nan],
        'p-value': [p_value_A, p_value_B, np.nan, np.nan],
    })

    return {
        'test_name': 'Двухфакторный критерий Фишера (ANOVA)',
        'F_A': F_A,
        'p_value_A': p_value_A,
        'F_B': F_B,
        'p_value_B': p_value_B,
        'SS_A': SS_A,
        'SS_B': SS_B,
        'SS_error': SS_error,
        'SS_total': SS_total,
        'MS_A': MS_A,
        'MS_B': MS_B,
        'MS_error': MS_error,
        'df_A': df_A,
        'df_B': df_B,
        'df_error': df_error,
        'anova_table': anova_table,
        'significant_A_005': p_value_A < 0.05,
        'significant_A_001': p_value_A < 0.01,
        'significant_B_005': p_value_B < 0.05,
        'significant_B_001': p_value_B < 0.01,
    }


# ============================================================
# Однофакторный критерий Фишера (one-way ANOVA)
# ============================================================

def one_way_anova(Y: np.ndarray) -> Dict:
    """
    Однофакторный дисперсионный анализ (one-way ANOVA).

    Игнорирует блочную структуру, рассматривает только фактор A.

    Args:
        Y: матрица наблюдений (n x k), столбцы — уровни A

    Returns:
        Dict с результатами ANOVA
    """
    n, k = Y.shape
    N = n * k

    # Общее среднее
    Y_bar = Y.mean()

    # Средние по столбцам (уровни A)
    Y_bar_col = Y.mean(axis=0)

    # Суммы квадратов
    SS_between = n * np.sum((Y_bar_col - Y_bar) ** 2)  # межгрупповая
    SS_within = np.sum((Y - Y_bar_col[np.newaxis, :]) ** 2)  # внутригрупповая
    SS_total = np.sum((Y - Y_bar) ** 2)

    # Степени свободы
    df_between = k - 1
    df_within = N - k
    df_total = N - 1

    # Средние квадраты
    MS_between = SS_between / df_between if df_between > 0 else 0
    MS_within = SS_within / df_within if df_within > 0 else 0

    # F-статистика
    F_stat = MS_between / MS_within if MS_within > 0 else np.inf

    # p-value
    p_value = 1 - stats.f.cdf(F_stat, df_between, df_within)

    # Проверка через scipy
    groups = [Y[:, i] for i in range(k)]
    scipy_F, scipy_p = stats.f_oneway(*groups)

    # Таблица ANOVA
    anova_table = pd.DataFrame({
        'Источник': ['Фактор A (межгрупп.)', 'Внутригрупп.', 'Итого'],
        'SS': [SS_between, SS_within, SS_total],
        'df': [df_between, df_within, df_total],
        'MS': [MS_between, MS_within, np.nan],
        'F': [F_stat, np.nan, np.nan],
        'p-value': [p_value, np.nan, np.nan],
    })

    return {
        'test_name': 'Однофакторный критерий Фишера (one-way ANOVA)',
        'F_statistic': F_stat,
        'p_value': p_value,
        'SS_between': SS_between,
        'SS_within': SS_within,
        'SS_total': SS_total,
        'MS_between': MS_between,
        'MS_within': MS_within,
        'df_between': df_between,
        'df_within': df_within,
        'scipy_F': scipy_F,
        'scipy_p': scipy_p,
        'anova_table': anova_table,
        'significant_005': p_value < 0.05,
        'significant_001': p_value < 0.01,
    }


# ============================================================
# Применение всех тестов к сценариям
# ============================================================

def apply_all_tests(scenarios: Dict) -> pd.DataFrame:
    """
    Применяет все критерии ко всем сценариям.

    Args:
        scenarios: словарь {scenario_key: (Y, params)}

    Returns:
        pd.DataFrame со сводной таблицей результатов
    """
    results = []

    for scenario_key, (Y, params) in scenarios.items():
        scenario_name = params['name']
        n, k = Y.shape

        print(f"\n{'='*60}")
        print(f"  {scenario_name}: {params['description']}")
        print(f"{'='*60}")

        # --- Критерий Фридмана (все сценарии) ---
        friedman = friedman_test(Y)
        print(f"\n  Критерий Фридмана:")
        print(f"    χ² = {friedman['statistic']:.4f}, df = {friedman['df']}, "
              f"p = {friedman['p_value']:.6f}")
        print(f"    Суммы рангов: {friedman['rank_sums']}")
        print(f"    Значим (α=0.05): {'Да ✓' if friedman['significant_005'] else 'Нет ✗'}")

        results.append({
            'scenario': scenario_name,
            'test': 'Фридман',
            'statistic': friedman['statistic'],
            'p_value': friedman['p_value'],
            'significant_005': friedman['significant_005'],
            'significant_001': friedman['significant_001'],
            'details': f"χ²={friedman['statistic']:.4f}, df={friedman['df']}",
        })

        # --- Критерий Пейджа (только сценарии 1 и 2) ---
        if scenario_key in ['scenario_1', 'scenario_2']:
            page = page_test(Y)
            print(f"\n  Критерий Пейджа:")
            print(f"    L = {page['L_statistic']:.2f}, Z = {page['Z_statistic']:.4f}, "
                  f"p = {page['p_value']:.6f}")
            print(f"    Суммы рангов: {page['rank_sums']}")
            print(f"    Значим (α=0.05): {'Да ✓' if page['significant_005'] else 'Нет ✗'}")

            results.append({
                'scenario': scenario_name,
                'test': 'Пейдж',
                'statistic': page['L_statistic'],
                'p_value': page['p_value'],
                'significant_005': page['significant_005'],
                'significant_001': page['significant_001'],
                'details': f"L={page['L_statistic']:.2f}, Z={page['Z_statistic']:.4f}",
            })

        # --- Двухфакторный Фишер (все сценарии) ---
        anova2 = two_way_anova(Y)
        print(f"\n  Двухфакторный Фишер (ANOVA):")
        print(f"    Фактор A: F = {anova2['F_A']:.4f}, p = {anova2['p_value_A']:.6f} "
              f"{'✓' if anova2['significant_A_005'] else '✗'}")
        print(f"    Фактор B: F = {anova2['F_B']:.4f}, p = {anova2['p_value_B']:.6f} "
              f"{'✓' if anova2['significant_B_005'] else '✗'}")
        print(f"    SS_A={anova2['SS_A']:.2f}, SS_B={anova2['SS_B']:.2f}, "
              f"SS_error={anova2['SS_error']:.2f}")

        results.append({
            'scenario': scenario_name,
            'test': 'Фишер 2-факт. (A)',
            'statistic': anova2['F_A'],
            'p_value': anova2['p_value_A'],
            'significant_005': anova2['significant_A_005'],
            'significant_001': anova2['significant_A_001'],
            'details': f"F_A={anova2['F_A']:.4f}, SS_A={anova2['SS_A']:.2f}",
        })

        results.append({
            'scenario': scenario_name,
            'test': 'Фишер 2-факт. (B)',
            'statistic': anova2['F_B'],
            'p_value': anova2['p_value_B'],
            'significant_005': anova2['significant_B_005'],
            'significant_001': anova2['significant_B_001'],
            'details': f"F_B={anova2['F_B']:.4f}, SS_B={anova2['SS_B']:.2f}",
        })

        # --- Однофакторный Фишер (только сценарий 2) ---
        if scenario_key == 'scenario_2':
            anova1 = one_way_anova(Y)
            print(f"\n  Однофакторный Фишер (one-way ANOVA):")
            print(f"    F = {anova1['F_statistic']:.4f}, p = {anova1['p_value']:.6f} "
                  f"{'✓' if anova1['significant_005'] else '✗'}")
            print(f"    SS_between={anova1['SS_between']:.2f}, "
                  f"SS_within={anova1['SS_within']:.2f}")
            print(f"    Сравнение с scipy: F={anova1['scipy_F']:.4f}, p={anova1['scipy_p']:.6f}")

            results.append({
                'scenario': scenario_name,
                'test': 'Фишер 1-факт.',
                'statistic': anova1['F_statistic'],
                'p_value': anova1['p_value'],
                'significant_005': anova1['significant_005'],
                'significant_001': anova1['significant_001'],
                'details': f"F={anova1['F_statistic']:.4f}, SS_b={anova1['SS_between']:.2f}, SS_w={anova1['SS_within']:.2f}",
            })

    results_df = pd.DataFrame(results)
    return results_df


def compare_one_vs_two_way(Y: np.ndarray, scenario_name: str) -> Dict:
    """
    Сравнивает однофакторный и двухфакторный анализ для одних данных.

    Args:
        Y: матрица наблюдений (n x k)
        scenario_name: название сценария

    Returns:
        Dict с результатами сравнения
    """
    anova1 = one_way_anova(Y)
    anova2 = two_way_anova(Y)

    # Ключевое различие: в однофакторном SS_within включает и SS_B, и SS_error
    # В двухфакторном SS_error = SS_within - SS_B
    comparison = {
        'scenario': scenario_name,
        'one_way_F': anova1['F_statistic'],
        'one_way_p': anova1['p_value'],
        'one_way_SS_within': anova1['SS_within'],
        'two_way_F_A': anova2['F_A'],
        'two_way_p_A': anova2['p_value_A'],
        'two_way_SS_error': anova2['SS_error'],
        'two_way_SS_B': anova2['SS_B'],
        'SS_B_fraction': anova2['SS_B'] / anova1['SS_within'] if anova1['SS_within'] > 0 else 0,
        'power_gain': (anova2['F_A'] / anova1['F_statistic']
                       if anova1['F_statistic'] > 0 else np.inf),
    }

    return comparison


def save_results(results_df: pd.DataFrame, anova_tables: Dict):
    """Сохраняет результаты в CSV файлы."""
    from pathlib import Path

    output_dir = Path("output_data/result_tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Сводная таблица
    results_df.to_csv(output_dir / 'test_results_summary.csv', index=False)
    print(f"\nСводная таблица сохранена: {output_dir / 'test_results_summary.csv'}")

    # Таблицы ANOVA для каждого сценария
    for name, table in anova_tables.items():
        filepath = output_dir / f'anova_{name}.csv'
        table.to_csv(filepath, index=False)
        print(f"Таблица ANOVA сохранена: {filepath}")


if __name__ == "__main__":
    # Тестовый запуск
    from data_generator import generate_all_scenarios

    scenarios = generate_all_scenarios()
    results_df = apply_all_tests(scenarios)
    print("\n\nСводная таблица результатов:")
    print(results_df.to_string(index=False))
