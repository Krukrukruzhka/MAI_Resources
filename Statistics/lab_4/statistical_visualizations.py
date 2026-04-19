import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def create_statistical_visualizations():
    """Создает визуализации для результатов статистических тестов"""
    
    # Создаем папку для графиков, если её нет
    output_dir = Path("output_data/charts")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Читаем результаты тестов
    results_df = pd.read_csv("output_data/result_tables/statistical_tests_results.csv")
    variance_df = pd.read_csv("output_data/result_tables/variance_analysis_dataset2.csv")
    
    # Настройка стиля
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. График p-значений для всех критериев
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Сравнение p-значений статистических критериев', fontsize=16, fontweight='bold')
    
    datasets = results_df['dataset'].values
    p_values_fisher = results_df['p_value_fisher'].values
    p_values_kruskal = results_df['p_value_kruskal'].values
    p_values_jonckheere = results_df['p_value_jonckheere'].values
    
    # График p-значений Фишера
    ax1 = axes[0, 0]
    bars1 = ax1.bar(datasets, p_values_fisher, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
    ax1.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')
    ax1.set_title('Критерий Фишера (ANOVA)')
    ax1.set_ylabel('p-значение')
    ax1.set_yscale('log')
    ax1.legend()
    
    # Добавляем значения на столбцы
    for bar, p_val in zip(bars1, p_values_fisher):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{p_val:.2e}', 
                ha='center', va='bottom', fontsize=9)
    
    # График p-значений Краскела-Уоллиса
    ax2 = axes[0, 1]
    bars2 = ax2.bar(datasets, p_values_kruskal, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
    ax2.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')
    ax2.set_title('Критерий Краскела-Уоллиса')
    ax2.set_ylabel('p-значение')
    ax2.set_yscale('log')
    ax2.legend()
    
    for bar, p_val in zip(bars2, p_values_kruskal):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height, f'{p_val:.2e}', 
                ha='center', va='bottom', fontsize=9)
    
    # График p-значений Джонкхиера
    ax3 = axes[1, 0]
    bars3 = ax3.bar(datasets, p_values_jonckheere, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
    ax3.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')
    ax3.set_title('Критерий Джонкхиера')
    ax3.set_ylabel('p-значение')
    ax3.set_yscale('log')
    ax3.legend()
    
    for bar, p_val in zip(bars3, p_values_jonckheere):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height, f'{p_val:.3f}', 
                ha='center', va='bottom', fontsize=9)
    
    # Сводная таблица значимости
    ax4 = axes[1, 1]
    significance_data = {
        'Фишер': results_df['fisher_significant'].values,
        'Краскел-Уоллис': results_df['kruskal_significant'].values,
        'Джонкхиер': results_df['jonckheere_significant'].values
    }
    
    significance_df = pd.DataFrame(significance_data, index=datasets)
    
    # Создаем тепловую карту значимости
    im = ax4.imshow(significance_df.astype(float), cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax4.set_xticks(range(len(significance_df.columns)))
    ax4.set_yticks(range(len(significance_df.index)))
    ax4.set_xticklabels(significance_df.columns, rotation=45)
    ax4.set_yticklabels(significance_df.index)
    ax4.set_title('Статистическая значимость (α = 0.05)')
    
    # Добавляем значения в ячейки
    for i in range(len(significance_df.index)):
        for j in range(len(significance_df.columns)):
            text = ax4.text(j, i, '✓' if significance_df.iloc[i, j] else '✗',
                           ha="center", va="center", color="black", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'statistical_tests_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. График влияния дисперсии на dataset_2
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Анализ влияния дисперсии на dataset_2 (размер цветов при разных удобрениях)', 
                 fontsize=16, fontweight='bold')
    
    # Средние значения и дисперсии
    ax1 = axes[0, 0]
    samples = variance_df['sample'].values
    means = variance_df['mean'].values
    variances = variance_df['variance'].values
    
    bars1 = ax1.bar(samples, means, color=['lightblue', 'lightcoral', 'lightgreen'])
    ax1.set_title('Средние значения размеров цветов')
    ax1.set_ylabel('Средний размер')
    ax1.set_xlabel('Группа удобрений')
    
    for bar, mean in zip(bars1, means):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{mean:.2f}', 
                ha='center', va='bottom', fontsize=10)
    
    # Дисперсии
    ax2 = axes[0, 1]
    bars2 = ax2.bar(samples, variances, color=['lightblue', 'lightcoral', 'lightgreen'])
    ax2.set_title('Дисперсии размеров цветов')
    ax2.set_ylabel('Дисперсия')
    ax2.set_xlabel('Группа удобрений')
    
    for bar, var in zip(bars2, variances):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height, f'{var:.2f}', 
                ha='center', va='bottom', fontsize=10)
    
    # Коэффициент вариации
    ax3 = axes[1, 0]
    cv_values = variance_df['cv'].values
    bars3 = ax3.bar(samples, cv_values, color=['lightblue', 'lightcoral', 'lightgreen'])
    ax3.set_title('Коэффициент вариации (CV)')
    ax3.set_ylabel('CV')
    ax3.set_xlabel('Группа удобрений')
    
    for bar, cv in zip(bars3, cv_values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height, f'{cv:.3f}', 
                ha='center', va='bottom', fontsize=10)
    
    # Взаимосвязь среднего и дисперсии
    ax4 = axes[1, 1]
    ax4.scatter(means, variances, s=100, c=['blue', 'red', 'green'], alpha=0.7)
    ax4.set_title('Взаимосвязь среднего и дисперсии')
    ax4.set_xlabel('Средний размер')
    ax4.set_ylabel('Дисперсия')
    
    # Добавляем подписи точек
    for i, (mean, var, sample) in enumerate(zip(means, variances, samples)):
        ax4.annotate(sample, (mean, var), xytext=(5, 5), textcoords='offset points', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'variance_impact_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Сравнение распределений по датасетам
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Сравнение распределений по датасетам', fontsize=16, fontweight='bold')
    
    dataset_files = {
        'dataset_1': 'input_data/dataset_1.csv',
        'dataset_2': 'input_data/dataset_2.csv',
        'dataset_3': 'input_data/dataset_3.csv',
        'dataset_4': 'input_data/dataset_4.csv'
    }
    
    for idx, (dataset_name, file_path) in enumerate(dataset_files.items()):
        ax = axes[idx // 2, idx % 2]
        
        df = pd.read_csv(file_path)
        
        # Собираем все данные для боксплота
        data_to_plot = []
        labels = []
        
        for col in df.columns:
            data = df[col].dropna().values
            data_to_plot.append(data)
            labels.append(col)
        
        # Создаем боксплот
        boxplot = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
        
        # Раскрашиваем боксы
        colors = ['lightblue', 'lightcoral', 'lightgreen']
        for patch, color in zip(boxplot['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_title(f'{dataset_name}: {results_df[results_df["dataset"] == dataset_name]["description"].iloc[0]}')
        ax.set_ylabel('Значения')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'datasets_distribution_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Визуализации созданы и сохранены в output_data/charts/")

if __name__ == "__main__":
    create_statistical_visualizations()