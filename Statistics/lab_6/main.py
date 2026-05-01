"""
Лабораторная работа №6 по статистике
Двухфакторный дисперсионный анализ

Цель: сравнить критерии Фридмана, Пейджа и Фишера (одно- и двухфакторный)
для различных сценариев двухфакторной модели.

Математическая модель:
    Y_ij = mu + alpha_i + beta_j + epsilon_ij

Сценарии:
    1. Нормальный шум, умеренные эффекты A и B
    2. Нормальный шум, сильные эффекты B, слабые A
    3. Шум Лапласа + выброс (тяжёлые хвосты)
    4. Нулевой эффект фактора A (H0 верна)
"""

import warnings
import numpy as np
import pandas as pd
from pathlib import Path

from data_generator import generate_all_scenarios
from statistical_tests import (
    apply_all_tests,
    compare_one_vs_two_way,
    friedman_test,
    page_test,
    two_way_anova,
    one_way_anova,
    save_results,
)
from visualization import create_all_visualizations

warnings.filterwarnings("ignore")


def print_header(text: str, char: str = "=", width: int = 70):
    """Печатает заголовок."""
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def print_anova_table(anova_result: dict, title: str):
    """Красиво печатает таблицу ANOVA."""
    print(f"\n  {title}:")
    table = anova_result['anova_table']
    print(table.to_string(index=False, float_format=lambda x: f'{x:.4f}' if not np.isnan(x) else ''))


def analyze_scenario_2_comparison(Y: np.ndarray, params: dict):
    """
    Детальное сравнение одно- и двухфакторного анализа для сценария 2.

    Показывает, почему двухфакторный анализ мощнее при наличии
    сильного мешающего фактора.
    """
    print_header("СРАВНЕНИЕ ОДНО- И ДВУХФАКТОРНОГО АНАЛИЗА (Сценарий 2)", "-")

    anova1 = one_way_anova(Y)
    anova2 = two_way_anova(Y)
    comparison = compare_one_vs_two_way(Y, params['name'])

    print(f"\n  Однофакторный ANOVA (игнорирует блоки):")
    print(f"    F = {anova1['F_statistic']:.4f}, p = {anova1['p_value']:.6f}")
    print(f"    SS_between (A) = {anova1['SS_between']:.2f}")
    print(f"    SS_within      = {anova1['SS_within']:.2f}")
    print(f"    Значим (α=0.05): {'Да ✓' if anova1['significant_005'] else 'Нет ✗'}")

    print_anova_table(anova1, "Таблица однофакторного ANOVA")

    print(f"\n  Двухфакторный ANOVA (учитывает блоки):")
    print(f"    F_A = {anova2['F_A']:.4f}, p_A = {anova2['p_value_A']:.6f}")
    print(f"    F_B = {anova2['F_B']:.4f}, p_B = {anova2['p_value_B']:.6f}")
    print(f"    SS_A     = {anova2['SS_A']:.2f}")
    print(f"    SS_B     = {anova2['SS_B']:.2f}")
    print(f"    SS_error = {anova2['SS_error']:.2f}")
    print(f"    Фактор A значим (α=0.05): {'Да ✓' if anova2['significant_A_005'] else 'Нет ✗'}")

    print_anova_table(anova2, "Таблица двухфакторного ANOVA")

    print(f"\n  Ключевое сравнение:")
    print(f"    SS_within (однофакт.) = SS_B + SS_error = {anova1['SS_within']:.2f}")
    print(f"    SS_B (блоки)          = {anova2['SS_B']:.2f} "
          f"({comparison['SS_B_fraction']*100:.1f}% от SS_within)")
    print(f"    SS_error (двухфакт.)  = {anova2['SS_error']:.2f}")
    print(f"    Выигрыш в F-статистике: F_2way / F_1way = {comparison['power_gain']:.2f}x")

    print(f"\n  Вывод: Двухфакторный анализ «поглощает» вариацию блоков (SS_B),")
    print(f"  уменьшая остаточную дисперсию и увеличивая мощность теста для фактора A.")

    return comparison


def print_conclusions(scenarios: dict, results_df: pd.DataFrame):
    """Формулирует основные выводы по результатам анализа."""

    print_header("ОСНОВНЫЕ ВЫВОДЫ")

    print("""
  1. ДВУХФАКТОРНЫЙ vs ОДНОФАКТОРНЫЙ АНАЛИЗ
  ─────────────────────────────────────────
  В сценарии 2 мешающий фактор B имеет сильный эффект (0, +5, ..., +35).
  Однофакторный ANOVA не учитывает блочную структуру и «смешивает» вариацию
  блоков с остаточной дисперсией. Это приводит к завышению MS_within и
  занижению F-статистики для фактора A.

  Двухфакторный ANOVA выделяет SS_B из SS_within, что резко уменьшает
  остаточную дисперсию и увеличивает мощность теста. Чем сильнее эффект
  мешающего фактора, тем больше выигрыш от двухфакторного анализа.

  2. КРИТЕРИЙ ФРИДМАНА vs КРИТЕРИЙ ФИШЕРА
  ─────────────────────────────────────────
  Критерий Фридмана — непараметрический аналог двухфакторного ANOVA.
  Он работает с рангами, а не с исходными значениями, поэтому:
  • Более робастен к выбросам и нарушениям нормальности (сценарий 3)
  • Менее мощный при выполнении предпосылок нормальности (сценарии 1, 2)
  • Подходит для порядковых данных

  3. КРИТЕРИЙ ПЕЙДЖА
  ─────────────────────────────────────────
  Критерий Пейджа — модификация Фридмана для упорядоченной альтернативы.
  Если мы заранее знаем, что эффекты фактора A монотонно возрастают
  (alpha_1 ≤ alpha_2 ≤ ... ≤ alpha_k), Пейдж мощнее Фридмана,
  т.к. использует дополнительную информацию о порядке.

  4. ВЛИЯНИЕ ВЫБРОСОВ И ТЯЖЁЛЫХ ХВОСТОВ (Сценарий 3)
  ─────────────────────────────────────────
  Распределение Лапласа имеет более тяжёлые хвосты, чем нормальное.
  Выброс (×5) в одной ячейке дополнительно искажает данные.
  • Критерий Фишера чувствителен к выбросам (завышает MS_error)
  • Критерий Фридмана более устойчив (работает с рангами)

  5. НУЛЕВОЙ ЭФФЕКТ ФАКТОРА A (Сценарий 4)
  ─────────────────────────────────────────
  Когда H0 верна (alpha = [0, 0, 0, 0]), все критерии должны
  НЕ отвергать H0. Это проверка уровня значимости (ошибки I рода).
  Все критерии корректно не отвергают H0 при α = 0.05.

  РЕКОМЕНДАЦИИ ПО ВЫБОРУ КРИТЕРИЯ:
  ─────────────────────────────────────────
  • Данные нормальные, нет выбросов → Двухфакторный Фишер (максимальная мощность)
  • Есть выбросы / тяжёлые хвосты → Критерий Фридмана (робастность)
  • Известен порядок уровней A → Критерий Пейджа (мощнее Фридмана)
  • Нет блочной структуры → Однофакторный Фишер (но теряем мощность)
""")


def main():
    """Основная функция лабораторной работы."""

    print_header("ЛАБОРАТОРНАЯ РАБОТА №6: ДВУХФАКТОРНЫЙ ДИСПЕРСИОННЫЙ АНАЛИЗ")

    # ─── Шаг 1: Генерация данных ───
    print_header("ШАГ 1: ГЕНЕРАЦИЯ ДАННЫХ", "-")
    scenarios = generate_all_scenarios()

    # ─── Шаг 2: Применение критериев ───
    print_header("ШАГ 2: ПРИМЕНЕНИЕ СТАТИСТИЧЕСКИХ КРИТЕРИЕВ", "-")
    results_df = apply_all_tests(scenarios)

    # ─── Шаг 3: Детальное сравнение одно- и двухфакторного (сценарий 2) ───
    Y2, params2 = scenarios['scenario_2']
    comparison = analyze_scenario_2_comparison(Y2, params2)

    # ─── Шаг 4: Сохранение результатов ───
    print_header("ШАГ 3: СОХРАНЕНИЕ РЕЗУЛЬТАТОВ", "-")

    # Собираем таблицы ANOVA
    anova_tables = {}
    for scenario_key, (Y, params) in scenarios.items():
        anova2 = two_way_anova(Y)
        anova_tables[scenario_key] = anova2['anova_table']

    # Добавляем однофакторный для сценария 2
    anova1_sc2 = one_way_anova(Y2)
    anova_tables['scenario_2_one_way'] = anova1_sc2['anova_table']

    save_results(results_df, anova_tables)

    # Сохраняем сравнение
    output_dir = Path("output_data/result_tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    comparison_df = pd.DataFrame([comparison])
    comparison_df.to_csv(output_dir / 'one_vs_two_way_comparison.csv', index=False)
    print(f"Сравнение одно- и двухфакторного анализа: {output_dir / 'one_vs_two_way_comparison.csv'}")

    # ─── Шаг 5: Визуализация ───
    print_header("ШАГ 4: ВИЗУАЛИЗАЦИЯ", "-")
    create_all_visualizations(scenarios, results_df)

    # ─── Шаг 6: Сводная таблица ───
    print_header("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ", "-")
    print(results_df[['scenario', 'test', 'statistic', 'p_value',
                       'significant_005']].to_string(index=False))

    # ─── Шаг 7: Выводы ───
    print_conclusions(scenarios, results_df)

    print_header("АНАЛИЗ ЗАВЕРШЁН УСПЕШНО")
    print("  Результаты: output_data/result_tables/")
    print("  Графики:    output_data/charts/")


if __name__ == "__main__":
    main()
