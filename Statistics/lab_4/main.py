import warnings

import pandas as pd
import numpy as np
from statistical_analysis import apply_statistical_tests, analyze_variance_impact
from statistical_visualizations import create_statistical_visualizations

warnings.filterwarnings("ignore")


def main():
    """Основная функция для выполнения анализа"""
    
    print("=== АНАЛИЗ СТАТИСТИЧЕСКИХ КРИТЕРИЕВ ДЛЯ МНОГОВЫБОРОЧНЫХ ТЕСТОВ ===\n")
    
    # 1. Применяем статистические тесты
    print("1. Применение статистических критериев...")
    results = apply_statistical_tests()
    
    # 2. Анализируем влияние дисперсии
    print("\n2. Анализ влияния дисперсии на dataset_2...")
    variance_results = analyze_variance_impact()
    
    # 3. Создаем визуализации
    print("\n3. Создание визуализаций...")
    create_statistical_visualizations()
    
    # 4. Выводим основные выводы
    print("\n4. Основные выводы:")
    print("-" * 50)
    
    for _, row in results.iterrows():
        dataset = row['dataset']
        desc = row['description']
        
        print(f"\n{dataset.upper()}: {desc}")
        print(f"  Фишер: p = {row['p_value_fisher']:.4f} {'✓' if row['fisher_significant'] else '✗'}")
        print(f"  Краскел-Уоллис: p = {row['p_value_kruskal']:.4f} {'✓' if row['kruskal_significant'] else '✗'}")
        print(f"  Джонкхиер: p = {row['p_value_jonckheere']:.4f} {'✓' if row['jonckheere_significant'] else '✗'}")
        
        # Интерпретация
        if row['fisher_significant'] or row['kruskal_significant']:
            print("  Вывод: Статистически значимые различия между группами")
        else:
            print("  Вывод: Нет статистически значимых различий между группами")
    
    print("\n" + "="*50)
    print("Анализ завершен успешно!")
    print("Результаты сохранены в output_data/")

if __name__ == "__main__":
    main()