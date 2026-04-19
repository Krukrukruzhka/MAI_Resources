import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from typing import Dict, Tuple, List


def calculate_correlations(X: np.ndarray, Y: np.ndarray) -> Dict[str, Tuple[float, float]]:
    """
    Вычисляет три коэффициента корреляции и их p-значения
    
    Args:
        X: первая переменная
        Y: вторая переменная
        
    Returns:
        Dict: словарь с коэффициентами и p-значениями
    """
    correlations = {}
    
    # Коэффициент корреляции Пирсона
    pearson_corr, pearson_p = pearsonr(X, Y)
    correlations['pearson'] = (pearson_corr, pearson_p)
    
    # Коэффициент корреляции Спирмана
    spearman_corr, spearman_p = spearmanr(X, Y)
    correlations['spearman'] = (spearman_corr, spearman_p)
    
    # Коэффициент корреляции Кендалла
    kendall_corr, kendall_p = kendalltau(X, Y)
    correlations['kendall'] = (kendall_corr, kendall_p)
    
    return correlations


def test_hypothesis(corr_value: float, p_value: float, dependency: str, alpha: float = 0.05) -> Tuple[bool, str]:
    """
    Проверяет гипотезу о корреляции с учетом типа зависимости
    
    Args:
        corr_value: значение коэффициента корреляции
        p_value: p-значение
        dependency: тип зависимости
        alpha: уровень значимости
        
    Returns:
        Tuple: (отвергается ли H₀, описание результата)
    """
    # Для Y = Z (linear_a0) корреляция должна быть незначимой
    if dependency == 'linear_a0':
        if p_value >= alpha:
            return False, f"H₀ не отвергается - корреляция незначима (p = {p_value:.4f} >= {alpha})"
        else:
            return True, f"ВНИМАНИЕ: H₀ отвергается, но для Y=Z это может быть ложное обнаружение (p = {p_value:.4f} < {alpha})"
    
    # Для других зависимостей используем стандартную проверку
    if p_value < alpha:
        return True, f"H₀ отвергается - корреляция значима (p = {p_value:.4f} < {alpha})"
    else:
        return False, f"H₀ не отвергается - корреляция незначима (p = {p_value:.4f} >= {alpha})"


def analyze_all_correlations(df: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """
    Анализирует корреляции для всех зависимостей в DataFrame
    
    Args:
        df: DataFrame с данными
        alpha: уровень значимости
        
    Returns:
        pd.DataFrame: таблица с результатами анализа
    """
    results = []
    
    # Базовые переменные
    X = df['X'].values
    Z = df['Z'].values
    
    # Анализируем корреляции для каждой зависимости
    for column in df.columns:
        if column not in ['X', 'Z']:
            Y = df[column].values
            
            # Вычисляем корреляции между Y и X
            correlations = calculate_correlations(Y, X)
            
            # Проверяем гипотезы для каждого коэффициента
            for corr_type, (corr_value, p_value) in correlations.items():
                reject_h0, hypothesis_result = test_hypothesis(corr_value, p_value, column, alpha)
                
                results.append({
                    'dependency': column,
                    'correlation_type': corr_type,
                    'correlation_value': corr_value,
                    'p_value': p_value,
                    'reject_h0': reject_h0,
                    'hypothesis_result': hypothesis_result
                })
    
    return pd.DataFrame(results)


def compare_with_outliers(df_original: pd.DataFrame, df_with_outliers: pd.DataFrame, 
                         alpha: float = 0.05) -> pd.DataFrame:
    """
    Сравнивает корреляции до и после добавления выбросов
    
    Args:
        df_original: исходные данные
        df_with_outliers: данные с выбросами
        alpha: уровень значимости
        
    Returns:
        pd.DataFrame: таблица сравнения
    """
    comparison_results = []
    
    # Анализируем корреляции для исходных данных
    original_results = analyze_all_correlations(df_original, alpha)
    
    # Анализируем корреляции для данных с выбросами
    outliers_results = analyze_all_correlations(df_with_outliers, alpha)
    
    # Объединяем результаты для сравнения
    for _, orig_row in original_results.iterrows():
        dep = orig_row['dependency']
        corr_type = orig_row['correlation_type']
        
        # Находим соответствующий результат для данных с выбросами
        outlier_row = outliers_results[
            (outliers_results['dependency'] == dep) & 
            (outliers_results['correlation_type'] == corr_type)
        ].iloc[0]
        
        # Вычисляем изменение коэффициента корреляции
        corr_change = outlier_row['correlation_value'] - orig_row['correlation_value']
        corr_change_percent = (corr_change / abs(orig_row['correlation_value'])) * 100 if orig_row['correlation_value'] != 0 else 0
        
        comparison_results.append({
            'dependency': dep,
            'correlation_type': corr_type,
            'original_correlation': orig_row['correlation_value'],
            'outlier_correlation': outlier_row['correlation_value'],
            'correlation_change': corr_change,
            'correlation_change_percent': corr_change_percent,
            'original_p_value': orig_row['p_value'],
            'outlier_p_value': outlier_row['p_value'],
            'original_hypothesis': orig_row['hypothesis_result'],
            'outlier_hypothesis': outlier_row['hypothesis_result']
        })
    
    return pd.DataFrame(comparison_results)


def save_correlation_results(results_df: pd.DataFrame, filename: str):
    """
    Сохраняет результаты корреляционного анализа в CSV
    
    Args:
        results_df: DataFrame с результатами
        filename: имя файла для сохранения
    """
    results_df.to_csv(f'output_data/result_tables/{filename}', index=False)


def print_correlation_summary(results_df: pd.DataFrame):
    """
    Выводит сводку по результатам корреляционного анализа
    
    Args:
        results_df: DataFrame с результатами
    """
    print("\n" + "="*80)
    print("СВОДКА КОРРЕЛЯЦИОННОГО АНАЛИЗА")
    print("="*80)
    
    for dependency in results_df['dependency'].unique():
        dep_results = results_df[results_df['dependency'] == dependency]
        
        print(f"\nЗависимость: {dependency}")
        print("-" * 40)
        
        for _, row in dep_results.iterrows():
            print(f"{row['correlation_type'].capitalize()}: {row['correlation_value']:.4f}")
            print(f"P-значение: {row['p_value']:.4f}")
            print(f"Гипотеза: {row['hypothesis_result']}")
            print()


if __name__ == "__main__":
    # Пример использования
    from data_generator import generate_samples, create_dataframe_with_dependencies
    
    X, Z = generate_samples(100)
    df = create_dataframe_with_dependencies(X, Z)
    
    results = analyze_all_correlations(df)
    print_correlation_summary(results)
    save_correlation_results(results, 'correlation_analysis.csv')