#!/usr/bin/env python3
"""
Лабораторная работа №5 по статистике
Анализ случайности временных рядов с помощью непараметрических критериев
"""

import warnings
import numpy as np
import pandas as pd

from data_generator import (
    generate_time_series,
    save_time_series,
    SCENARIO_DESCRIPTIONS,
    SCENARIO_SHORT_NAMES,
)
from statistical_tests import (
    apply_all_tests,
    save_test_results,
    print_test_summary,
)
from visualization import create_all_visualizations

warnings.filterwarnings("ignore")


def main():
    """Основная функция для выполнения анализа"""

    print("=" * 80)
    print("ЛАБОРАТОРНАЯ РАБОТА №5: АНАЛИЗ СЛУЧАЙНОСТИ ВРЕМЕННЫХ РЯДОВ")
    print("=" * 80)

    # Параметры
    n = 100
    alpha = 0.05

    # ── Шаг 1: Генерация временных рядов ──────────────────────────
    print("\n" + "-" * 40)
    print("1. ГЕНЕРАЦИЯ ВРЕМЕННЫХ РЯДОВ")
    print("-" * 40)

    series = generate_time_series(n=n)
    df = save_time_series(series)

    print(f"\nСгенерировано {len(series)} временных рядов длины n={n}:")
    for name, desc in SCENARIO_DESCRIPTIONS.items():
        values = series[name]
        print(f"  • {desc}")
        print(f"    mean={np.mean(values):.3f}, std={np.std(values):.3f}, "
              f"min={np.min(values):.3f}, max={np.max(values):.3f}")

    # ── Шаг 2: Применение статистических критериев ─────────────────
    print("\n" + "-" * 40)
    print("2. ПРИМЕНЕНИЕ СТАТИСТИЧЕСКИХ КРИТЕРИЕВ")
    print("-" * 40)

    print(f"\nУровень значимости α = {alpha}")
    print("Критерии:")
    print("  1) Критерий инверсий")
    print("  2) Сериальный критерий Вальда-Вольфовица")
    print("  3) Критерий Рамачандрана-Ранганатана")
    print("  4) Критерий серий знаков первых разностей")

    results_df = apply_all_tests(series, alpha)
    print_test_summary(results_df, SCENARIO_DESCRIPTIONS)
    save_test_results(results_df)

    # ── Шаг 3: Создание визуализаций ──────────────────────────────
    print("\n" + "-" * 40)
    print("3. СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
    print("-" * 40)

    create_all_visualizations(series, results_df, SCENARIO_DESCRIPTIONS, SCENARIO_SHORT_NAMES)

    # ── Шаг 4: Сводная таблица решений ────────────────────────────
    print("\n" + "-" * 40)
    print("4. СВОДНАЯ ТАБЛИЦА РЕШЕНИЙ")
    print("-" * 40)

    # Создаём pivot-таблицу
    pivot = results_df.pivot_table(
        index="scenario", columns="test", values="reject_H0", aggfunc="first"
    )
    pivot.index = [SCENARIO_SHORT_NAMES.get(s, s) for s in pivot.index]

    print("\nH₀: ряд случаен | True = H₀ отвергнута, False = H₀ принята\n")
    print(pivot.to_string())

    # Подсчёт: сколько тестов отвергли H₀ для каждого сценария
    print("\n\nКоличество тестов, отвергнувших H₀:")
    for scenario in results_df["scenario"].unique():
        short = SCENARIO_SHORT_NAMES.get(scenario, scenario)
        count = results_df[results_df["scenario"] == scenario]["reject_H0"].sum()
        total = len(results_df[results_df["scenario"] == scenario])
        print(f"  {short:25s}: {count}/{total}")

    # ── Шаг 5: Выводы ────────────────────────────────────────────
    print("\n" + "-" * 40)
    print("5. ВЫВОДЫ")
    print("-" * 40)

    print("""
1. Сценарий 1 (белый шум):
   Все критерии принимают H0 — ряд действительно случаен.
   Это ожидаемый результат, подтверждающий корректность критериев.

2. Сценарий 2 (слабый тренд 0.01t):
   Только критерий инверсий обнаружил неслучайность (p=0.0004).
   Остальные критерии не чувствительны к столь малому наклону.
   Критерий инверсий напрямую считает нарушения порядка, что делает
   его наиболее мощным для обнаружения монотонных трендов.

3. Сценарий 3 (сильный тренд −0.5t):
   Все 4 критерия уверенно отвергают H0 — сильный линейный тренд
   легко обнаруживается любым из методов.

4. Сценарий 4 (периодика 3sin(2πt/20)):
   3 из 4 критериев обнаружили неслучайность. Критерий инверсий
   не обнаружил периодику (p=0.18), поскольку синусоида не создаёт
   монотонного тренда. Критерии, основанные на сериях, эффективно
   выявляют периодическую структуру.

5. Сценарий 5 (шум + выброс):
   Ни один критерий не отверг H0 — единичный выброс практически
   не влияет на ранговые и знаковые характеристики ряда.

Общие выводы:
• Критерий инверсий наиболее чувствителен к монотонным трендам
  (обнаружил даже слабый тренд), но не к периодике.
• Критерий Вальда-Вольфовица хорошо обнаруживает как сильные тренды,
  так и периодические компоненты.
• Критерий Рамачандрана-Ранганатана эффективен для обнаружения
  периодичности и сильных трендов через анализ серий вверх-вниз.
• Критерий серий знаков первых разностей — наиболее мощный для
  периодики (комбинирует число серий и максимальную длину серии).
• Единичный выброс не влияет ни на один из критериев.
""")

    print("=" * 80)
    print("АНАЛИЗ ЗАВЕРШЁН")
    print("Результаты: output_data/result_tables/")
    print("Графики:    output_data/charts/")
    print("=" * 80)


if __name__ == "__main__":
    main()
