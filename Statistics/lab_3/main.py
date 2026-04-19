#!/usr/bin/env python3
"""
Лабораторная работа №3 по статистике
Анализ корреляционных зависимостей и влияние выбросов
"""

import pandas as pd
import numpy as np
from data_generator import generate_samples, create_dataframe_with_dependencies, add_outliers
from correlation_analysis import analyze_all_correlations, compare_with_outliers, save_correlation_results, print_correlation_summary
from visualization import create_all_visualizations


def main():
    """Основная функция для выполнения анализа"""
    print("=" * 80)
    print("ЛАБОРАТОРНАЯ РАБОТА №3: АНАЛИЗ КОРРЕЛЯЦИОННЫХ ЗАВИСИМОСТЕЙ")
    print("=" * 80)
    
    # Параметры анализа
    n_samples = 1000
    alpha = 0.05
    
    # Шаг 1: Генерация данных
    print("-" * 40, "1. ГЕНЕРАЦИЯ ДАННЫХ", sep='\n')
    X, Z = generate_samples(n_samples)
    df_original = create_dataframe_with_dependencies(X, Z)
    
    print(f"Сгенерировано {n_samples} наблюдений:")
    print(f"  X ~ N(0,1): mean={X.mean():.3f}, std={X.std():.3f}")
    print(f"  Z ~ N(5,2): mean={Z.mean():.3f}, std={Z.std():.3f}")
    print(f"  Создано {len(df_original.columns) - 2} зависимостей: {list(df_original.columns[2:])}")
    
    # Сохраняем исходные данные
    df_original.to_csv('input_data/original_data.csv', index=False)
    
    # Шаг 2: Добавление выбросов
    print("-" * 40, "2. ДОБАВЛЕНИЕ ВЫБРОСОВ", sep='\n')
    df_outliers = df_original.copy()

    df_outliers['linear_a0.5'] = add_outliers(df_outliers['linear_a0.5'])
    df_outliers['cubic'] = add_outliers(df_outliers['cubic'])
    # Квадратичная зависимость остается без выбросов (по условию задания)
    print("Выбросы добавлены к зависимостям:")
    print("  - linear_a0.5 (линейная с a=0.5)")
    print("  - cubic (кубическая)")
    df_outliers.to_csv('input_data/data_with_outliers.csv', index=False)
    
    # Шаг 3: Анализ корреляций для исходных данных
    print("-" * 40)
    print("3. АНАЛИЗ КОРРЕЛЯЦИЙ (ИСХОДНЫЕ ДАННЫЕ)")
    
    results_original = analyze_all_correlations(df_original, alpha)
    print_correlation_summary(results_original)
    save_correlation_results(results_original, 'correlation_analysis_original.csv')
    print("Результаты анализа сохранены в output_data/result_tables/correlation_analysis_original.csv")
    
    # Шаг 4: Анализ корреляций для данных с выбросами
    print("-" * 40)
    print("4. АНАЛИЗ КОРРЕЛЯЦИЙ (С ВЫБРОСАМИ)")
    
    results_outliers = analyze_all_correlations(df_outliers, alpha)
    print_correlation_summary(results_outliers)
    save_correlation_results(results_outliers, 'correlation_analysis_outliers.csv')
    print("Результаты анализа сохранены в output_data/result_tables/correlation_analysis_outliers.csv")
    
    # Шаг 5: Сравнение результатов
    print("-" * 40)
    print("5. СРАВНЕНИЕ РЕЗУЛЬТАТОВ ДО И ПОСЛЕ ВЫБРОСОВ")
    
    comparison_results = compare_with_outliers(df_original, df_outliers, alpha)
    
    # Выводим сводку по изменениям
    significant_changes = comparison_results[comparison_results['correlation_change_percent'].abs() > 1]
    
    if len(significant_changes) > 0:
        print("Значительные изменения коэффициентов корреляции (>1%):")
        for _, row in significant_changes.iterrows():
            print(f"  {row['dependency']} ({row['correlation_type']}): "
                  f"{row['original_correlation']:.4f} → {row['outlier_correlation']:.4f} "
                  f"(изменение: {row['correlation_change_percent']:.1f}%)")
    else:
        print("Значительных изменений коэффициентов корреляции не обнаружено")
    
    # Сохраняем результаты сравнения
    save_correlation_results(comparison_results, 'correlation_comparison.csv')
    print("✓ Результаты сравнения сохранены в output_data/result_tables/correlation_comparison.csv")
    
    # Шаг 6: Создание визуализаций
    print("-" * 40)
    print("6. СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
    create_all_visualizations(df_original, df_outliers, results_original, comparison_results)
    print("Все визуализации созданы и сохранены в output_data/charts/")
    
    # Шаг 7: Выводы
    print("-" * 40)
    print("7. ВЫВОДЫ")
    print("\nОсновные выводы по результатам анализа:")
    
    # Анализ влияния типа зависимости на корреляции
    linear_results = results_original[results_original['dependency'].str.startswith('linear')]
    cubic_result = results_original[results_original['dependency'] == 'cubic']
    quadratic_result = results_original[results_original['dependency'] == 'quadratic']
    
    print("\n1. Влияние типа зависимости на корреляции:")
    print(f"   - Линейные зависимости: коэффициенты корреляции от {linear_results['correlation_value'].min():.3f} до {linear_results['correlation_value'].max():.3f}")
    print(f"   - Кубическая зависимость: коэффициент Пирсона = {cubic_result[cubic_result['correlation_type'] == 'pearson']['correlation_value'].values[0]:.3f}")
    print(f"   - Квадратичная зависимость: коэффициент Пирсона = {quadratic_result[quadratic_result['correlation_type'] == 'pearson']['correlation_value'].values[0]:.3f}")
    
    # Анализ устойчивости коэффициентов к выбросам
    print("\n2. Устойчивость коэффициентов к выбросам:")
    for corr_type in ['pearson', 'spearman', 'kendall']:
        changes = comparison_results[comparison_results['correlation_type'] == corr_type]['correlation_change_percent'].abs()
        if len(changes) > 0:
            avg_change = changes.mean()
            print(f"   - {corr_type.capitalize()}: среднее изменение {avg_change:.1f}%")
    
    print("\n" + "=" * 80)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)
    
    print("\nСозданные файлы:")
    print("  input_data/original_data.csv - исходные данные")
    print("  input_data/data_with_outliers.csv - данные с выбросами")
    print("  output_data/result_tables/correlation_analysis_original.csv - анализ исходных данных")
    print("  output_data/result_tables/correlation_analysis_outliers.csv - анализ с выбросами")
    print("  output_data/result_tables/correlation_comparison.csv - сравнение результатов")
    print("  output_data/charts/ - графики и визуализации")


if __name__ == "__main__":
    main()