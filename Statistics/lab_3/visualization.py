import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List
import os


def setup_plot_style():
    """Настраивает стиль графиков"""
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12


def plot_scatter_with_correlation(Y: np.ndarray, X: np.ndarray,
                                 dependency_name: str, corr_coef: float = None):
    """
    Строит scatter plot с линией регрессии (Y по оси X, X по оси Y)
    
    Args:
        Y: значения по оси X (зависимая переменная)
        X: значения по оси Y (независимая переменная)
        dependency_name: название зависимости
        corr_coef: коэффициент корреляции (опционально)
    """
    plt.figure(figsize=(10, 6))
    
    # Scatter plot
    plt.scatter(Y, X, alpha=0.6, s=30)
    
    # Линия регрессии
    z = np.polyfit(Y, X, 1)
    p = np.poly1d(z)
    plt.plot(Y, p(Y), "r--", alpha=0.8, linewidth=2)
    
    plt.xlabel(f'Y ({dependency_name})')
    plt.ylabel('X ~ N(0,1)')
    plt.title(f'Зависимость: {dependency_name}' + 
              (f' (r = {corr_coef:.3f})' if corr_coef is not None else ''))
    plt.grid(True, alpha=0.3)
    
    # Сохраняем график
    filename = f'output_data/charts/scatter_{dependency_name}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def plot_histograms_comparison(df_original: pd.DataFrame, df_outliers: pd.DataFrame, 
                              dependency_name: str):
    """
    Сравнивает гистограммы до и после добавления выбросов
    
    Args:
        df_original: исходные данные
        df_outliers: данные с выбросами
        dependency_name: название зависимости
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Гистограмма исходных данных
    ax1.hist(df_original[dependency_name], bins=50, alpha=0.7, color='blue')
    ax1.set_title(f'Исходные данные: {dependency_name}')
    ax1.set_xlabel('Значения Y')
    ax1.set_ylabel('Частота')
    ax1.grid(True, alpha=0.3)
    
    # Гистограмма данных с выбросами
    ax2.hist(df_outliers[dependency_name], bins=50, alpha=0.7, color='red')
    ax2.set_title(f'С выбросами: {dependency_name}')
    ax2.set_xlabel('Значения Y')
    ax2.set_ylabel('Частота')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Сохраняем график
    filename = f'output_data/charts/histogram_comparison_{dependency_name}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def plot_correlation_comparison(results_df: pd.DataFrame):
    """
    Строит график сравнения коэффициентов корреляции
    
    Args:
        results_df: DataFrame с результатами корреляционного анализа
    """
    # Создаем сводную таблицу для визуализации
    pivot_df = results_df.pivot(index='dependency', columns='correlation_type', 
                               values='correlation_value')
    
    plt.figure(figsize=(12, 8))
    
    # Строим столбчатую диаграмму
    pivot_df.plot(kind='bar', ax=plt.gca())
    
    plt.title('Сравнение коэффициентов корреляции для различных зависимостей')
    plt.xlabel('Тип зависимости')
    plt.ylabel('Коэффициент корреляции')
    plt.xticks(rotation=45)
    plt.legend(title='Тип корреляции')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Сохраняем график
    filename = 'output_data/charts/correlation_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def plot_outlier_impact(comparison_df: pd.DataFrame):
    """
    Визуализирует влияние выбросов на коэффициенты корреляции
    
    Args:
        comparison_df: DataFrame с сравнением до/после выбросов
    """
    # Фильтруем только значимые изменения
    significant_changes = comparison_df[comparison_df['correlation_change_percent'].abs() > 1]
    
    if len(significant_changes) > 0:
        plt.figure(figsize=(12, 8))
        
        # Создаем индекс для группировки
        x_pos = np.arange(len(significant_changes))
        
        # Столбцы для исходных и измененных значений
        plt.bar(x_pos - 0.2, significant_changes['original_correlation'], 
                width=0.4, label='Исходные', alpha=0.7)
        plt.bar(x_pos + 0.2, significant_changes['outlier_correlation'], 
                width=0.4, label='С выбросами', alpha=0.7)
        
        # Настройки графика
        plt.xlabel('Зависимость и тип корреляции')
        plt.ylabel('Коэффициент корреляции')
        plt.title('Влияние выбросов на коэффициенты корреляции')
        
        # Подписи по оси X
        labels = [f"{row['dependency']}\n{row['correlation_type']}" 
                 for _, row in significant_changes.iterrows()]
        plt.xticks(x_pos, labels, rotation=45)
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Сохраняем график
        filename = 'output_data/charts/outlier_impact.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()


def create_all_visualizations(df_original: pd.DataFrame, df_outliers: pd.DataFrame, 
                             results_df: pd.DataFrame, comparison_df: pd.DataFrame):
    """
    Создает все визуализации для анализа
    
    Args:
        df_original: исходные данные
        df_outliers: данные с выбросами
        results_df: результаты корреляционного анализа
        comparison_df: сравнение до/после выбросов
    """
    setup_plot_style()
    
    # Создаем папку для графиков, если её нет
    os.makedirs('output_data/charts', exist_ok=True)
    
    # Scatter plots для всех зависимостей
    X = df_original['X'].values
    for dependency in df_original.columns:
        if dependency not in ['X', 'Z']:
            Y = df_original[dependency].values
            
            # Находим коэффициент корреляции Пирсона для подписи
            corr_coef = results_df[
                (results_df['dependency'] == dependency) &
                (results_df['correlation_type'] == 'pearson')
            ]['correlation_value'].values[0]
            
            plot_scatter_with_correlation(Y, X, dependency, corr_coef)
    
    # Гистограммы сравнения только для зависимостей с выбросами
    selected_dependencies = ['linear_a0.5', 'cubic']
    for dep in selected_dependencies:
        if dep in df_original.columns:
            plot_histograms_comparison(df_original, df_outliers, dep)
    
    # График сравнения корреляций
    plot_correlation_comparison(results_df)
    
    # График влияния выбросов
    plot_outlier_impact(comparison_df)
    
    print("Все визуализации успешно созданы и сохранены в output_data/charts/")


if __name__ == "__main__":
    # Пример использования
    from data_generator import generate_samples, create_dataframe_with_dependencies, add_outliers
    from correlation_analysis import analyze_all_correlations, compare_with_outliers
    
    # Генерируем тестовые данные
    X, Z = generate_samples(100)
    df_original = create_dataframe_with_dependencies(X, Z)
    
    # Создаем данные с выбросами
    df_outliers = df_original.copy()
    df_outliers['linear_a0.5'] = add_outliers(df_outliers['linear_a0.5'])
    
    # Анализируем корреляции
    results_df = analyze_all_correlations(df_original)
    comparison_df = compare_with_outliers(df_original, df_outliers)
    
    # Создаем визуализации
    create_all_visualizations(df_original, df_outliers, results_df, comparison_df)