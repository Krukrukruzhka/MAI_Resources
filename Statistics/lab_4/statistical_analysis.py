import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import f_oneway, kruskal, friedmanchisquare
import os
from pathlib import Path

def apply_statistical_tests():
    """Применяет статистические критерии к датасетам"""
    
    # Создаем папку для результатов, если её нет
    output_dir = Path("output_data/result_tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        'dataset_1': 'input_data/dataset_1.csv',
        'dataset_2': 'input_data/dataset_2.csv', 
        'dataset_3': 'input_data/dataset_3.csv',
        'dataset_4': 'input_data/dataset_4.csv'
    }
    
    # Описания датасетов
    dataset_descriptions = {
        'dataset_1': 'Нормальные распределения: mean=10,12,14; std=2',
        'dataset_2': 'Нормальные распределения: mean=10,11,12; std=1,3,5',
        'dataset_3': 'Стандартные нормальные распределения: mean=0; std=1',
        'dataset_4': 'Нормальные распределения с выбросами: mean=10,12,14; std=2'
    }
    
    results = []
    
    for dataset_name, file_path in datasets.items():
        print(f"Анализ {dataset_name}...")
        
        # Читаем данные
        df = pd.read_csv(file_path)
        
        # Убираем NaN значения
        sample1 = df['sample_1'].dropna().values
        sample2 = df['sample_2'].dropna().values
        sample3 = df['sample_3'].dropna().values
        
        # Основные статистики
        stats_summary = {
            'dataset': dataset_name,
            'description': dataset_descriptions[dataset_name],
            'n1': len(sample1),
            'n2': len(sample2),
            'n3': len(sample3),
            'mean1': np.mean(sample1),
            'mean2': np.mean(sample2),
            'mean3': np.mean(sample3),
            'std1': np.std(sample1, ddof=1),
            'std2': np.std(sample2, ddof=1),
            'std3': np.std(sample3, ddof=1),
            'var1': np.var(sample1, ddof=1),
            'var2': np.var(sample2, ddof=1),
            'var3': np.var(sample3, ddof=1)
        }
        
        # 1. Критерий Фишера (ANOVA)
        try:
            f_stat, p_value_f = f_oneway(sample1, sample2, sample3)
            stats_summary['f_statistic'] = f_stat
            stats_summary['p_value_fisher'] = p_value_f
            stats_summary['fisher_significant'] = p_value_f < 0.05
        except Exception as e:
            stats_summary['f_statistic'] = None
            stats_summary['p_value_fisher'] = None
            stats_summary['fisher_significant'] = None
        
        # 2. Критерий Краскела-Уоллиса
        try:
            h_stat, p_value_kw = kruskal(sample1, sample2, sample3)
            stats_summary['h_statistic'] = h_stat
            stats_summary['p_value_kruskal'] = p_value_kw
            stats_summary['kruskal_significant'] = p_value_kw < 0.05
        except Exception as e:
            stats_summary['h_statistic'] = None
            stats_summary['p_value_kruskal'] = None
            stats_summary['kruskal_significant'] = None
        
        # 3. Критерий Джонкхиера (Jonckheere-Terpstra)
        # Для этого критерия нужно создать ранжированные данные
        try:
            # Объединяем все выборки с метками групп
            all_data = np.concatenate([sample1, sample2, sample3])
            groups = np.concatenate([
                np.ones(len(sample1)),  # группа 1
                np.ones(len(sample2)) * 2,  # группа 2
                np.ones(len(sample3)) * 3   # группа 3
            ])
            
            # Сортируем данные по возрастанию
            sorted_indices = np.argsort(all_data)
            sorted_groups = groups[sorted_indices]
            
            # Вычисляем статистику Джонкхиера
            jt_stat = 0
            n_total = len(all_data)
            
            for i in range(n_total):
                for j in range(i+1, n_total):
                    if sorted_groups[i] < sorted_groups[j]:
                        jt_stat += 1
                    elif sorted_groups[i] > sorted_groups[j]:
                        jt_stat -= 1
            
            # Нормализация статистики
            n1, n2, n3 = len(sample1), len(sample2), len(sample3)
            N = n1 + n2 + n3
            
            # Ожидаемое значение
            E_jt = (n1*n2 + n1*n3 + n2*n3) / 2
            
            # Дисперсия
            var_jt = (n1*n2*n3*(N+1) - n1*n2*n3*(n1*n2 + n1*n3 + n2*n3)/(N*(N-1))) / 12
            
            # Z-статистика
            if var_jt > 0:
                z_jt = (jt_stat - E_jt) / np.sqrt(var_jt)
                # Двусторонний p-value
                p_value_jt = 2 * (1 - stats.norm.cdf(abs(z_jt)))
            else:
                z_jt = 0
                p_value_jt = 1.0
            
            stats_summary['jt_statistic'] = jt_stat
            stats_summary['z_jt'] = z_jt
            stats_summary['p_value_jonckheere'] = p_value_jt
            stats_summary['jonckheere_significant'] = p_value_jt < 0.05
            
        except Exception as e:
            stats_summary['jt_statistic'] = None
            stats_summary['z_jt'] = None
            stats_summary['p_value_jonckheere'] = None
            stats_summary['jonckheere_significant'] = None
        
        results.append(stats_summary)
        print(f"  - Фишер: p={stats_summary.get('p_value_fisher', 'N/A'):.4f}")
        print(f"  - Краскел-Уоллис: p={stats_summary.get('p_value_kruskal', 'N/A'):.4f}")
        print(f"  - Джонкхиер: p={stats_summary.get('p_value_jonckheere', 'N/A'):.4f}")
    
    # Сохраняем результаты в CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_dir / 'statistical_tests_results.csv', index=False)
    
    # Создаем сводную таблицу для отчета
    summary_df = results_df[['dataset', 'description', 'p_value_fisher', 'p_value_kruskal', 
                           'p_value_jonckheere', 'fisher_significant', 'kruskal_significant', 
                           'jonckheere_significant']].copy()
    
    summary_df.to_csv(output_dir / 'tests_summary.csv', index=False)
    
    print(f"\nРезультаты сохранены в {output_dir}/")
    return results_df

def analyze_variance_impact():
    """Анализирует влияние дисперсии на dataset_2"""
    
    # Читаем dataset_2
    df = pd.read_csv('input_data/dataset_2.csv')
    
    sample1 = df['sample_1'].dropna().values
    sample2 = df['sample_2'].dropna().values
    sample3 = df['sample_3'].dropna().values
    
    # Анализ влияния дисперсии
    variance_analysis = {
        'sample': ['sample_1', 'sample_2', 'sample_3'],
        'mean': [np.mean(sample1), np.mean(sample2), np.mean(sample3)],
        'std': [np.std(sample1, ddof=1), np.std(sample2, ddof=1), np.std(sample3, ddof=1)],
        'variance': [np.var(sample1, ddof=1), np.var(sample2, ddof=1), np.var(sample3, ddof=1)],
        'cv': [np.std(sample1, ddof=1)/np.mean(sample1) if np.mean(sample1) != 0 else 0,
               np.std(sample2, ddof=1)/np.mean(sample2) if np.mean(sample2) != 0 else 0,
               np.std(sample3, ddof=1)/np.mean(sample3) if np.mean(sample3) != 0 else 0]
    }
    
    variance_df = pd.DataFrame(variance_analysis)
    
    # Сохраняем анализ дисперсии
    output_dir = Path("output_data/result_tables")
    variance_df.to_csv(output_dir / 'variance_analysis_dataset2.csv', index=False)
    
    print("Анализ дисперсии для dataset_2:")
    print(variance_df)
    
    return variance_df

if __name__ == "__main__":
    # Применяем статистические тесты
    results = apply_statistical_tests()
    
    # Анализируем влияние дисперсии
    variance_results = analyze_variance_impact()
    
    print("\nАнализ завершен!")