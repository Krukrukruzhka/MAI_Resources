import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from pathlib import Path

# Настройка стиля графиков
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_visualizations():
    """Создает визуализации для всех датасетов"""
    
    # Создаем папку для графиков, если её нет
    output_dir = Path("output_data/charts")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        'dataset_1': 'input_data/dataset_1.csv',
        'dataset_2': 'input_data/dataset_2.csv', 
        'dataset_3': 'input_data/dataset_3.csv',
        'dataset_4': 'input_data/dataset_4.csv'
    }
    
    # Описания датасетов для подписей
    dataset_descriptions = {
        'dataset_1': 'Нормальные распределения: mean=10,12,14; std=2',
        'dataset_2': 'Нормальные распределения: mean=10,11,12; std=1,3,5',
        'dataset_3': 'Стандартные нормальные распределения: mean=0; std=1',
        'dataset_4': 'Нормальные распределения с выбросами: mean=10,12,14; std=2'
    }
    
    for dataset_name, file_path in datasets.items():
        print(f"Обработка {dataset_name}...")
        
        # Читаем данные
        df = pd.read_csv(file_path)
        
        # Создаем подпапку для каждого датасета
        dataset_dir = output_dir / dataset_name
        dataset_dir.mkdir(exist_ok=True)
        
        # 1. Гистограммы для каждой выборки
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f'{dataset_name}: {dataset_descriptions[dataset_name]}', fontsize=14, fontweight='bold')
        
        for i, column in enumerate(df.columns):
            ax = axes[i]
            # Убираем NaN значения
            data = df[column].dropna()
            
            ax.hist(data, bins=15, alpha=0.7, edgecolor='black')
            ax.set_title(f'{column}')
            ax.set_xlabel('Значения')
            ax.set_ylabel('Частота')
            
            # Добавляем статистику
            mean_val = data.mean()
            std_val = data.std()
            ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
            ax.axvline(mean_val + std_val, color='orange', linestyle=':', alpha=0.7, label=f'+1 std')
            ax.axvline(mean_val - std_val, color='orange', linestyle=':', alpha=0.7, label=f'-1 std')
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(dataset_dir / 'histograms.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Box plot для сравнения выборок
        plt.figure(figsize=(12, 6))
        
        # Подготовка данных для box plot
        box_data = [df[col].dropna() for col in df.columns]
        
        plt.boxplot(box_data, labels=df.columns)
        plt.title(f'{dataset_name}: Box Plot сравнения выборок\n{dataset_descriptions[dataset_name]}')
        plt.ylabel('Значения')
        plt.grid(True, alpha=0.3)
        
        plt.savefig(dataset_dir / 'boxplot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Violin plot для более детального сравнения
        plt.figure(figsize=(12, 6))
        
        # Преобразуем данные для violin plot
        violin_data = []
        for col in df.columns:
            data = df[col].dropna()
            for value in data:
                violin_data.append({'Sample': col, 'Value': value})
        
        violin_df = pd.DataFrame(violin_data)
        
        sns.violinplot(data=violin_df, x='Sample', y='Value')
        plt.title(f'{dataset_name}: Violin Plot распределений\n{dataset_descriptions[dataset_name]}')
        plt.ylabel('Значения')
        
        plt.savefig(dataset_dir / 'violinplot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Scatter plot для парных сравнений (если данные сопоставимы по длине)
        # Находим минимальную длину среди всех выборок
        min_length = min(len(df[col].dropna()) for col in df.columns)
        
        if min_length > 5:  # Создаем scatter plot только если достаточно данных
            fig, axes = plt.subplots(1, 3, figsize=(18, 5))
            fig.suptitle(f'{dataset_name}: Scatter Plot парных сравнений\n{dataset_descriptions[dataset_name]}', 
                        fontsize=14, fontweight='bold')
            
            pairs = [('sample_1', 'sample_2'), ('sample_1', 'sample_3'), ('sample_2', 'sample_3')]
            
            for i, (col1, col2) in enumerate(pairs):
                ax = axes[i]
                data1 = df[col1].dropna().iloc[:min_length]
                data2 = df[col2].dropna().iloc[:min_length]
                
                ax.scatter(data1, data2, alpha=0.6)
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                ax.set_title(f'{col1} vs {col2}')
                ax.grid(True, alpha=0.3)
                
                # Добавляем линию тренда
                if len(data1) > 1:
                    z = np.polyfit(data1, data2, 1)
                    p = np.poly1d(z)
                    ax.plot(data1, p(data1), "r--", alpha=0.8)
            
            plt.tight_layout()
            plt.savefig(dataset_dir / 'scatter_plots.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 5. QQ plot для проверки нормальности распределения
        from scipy import stats
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f'{dataset_name}: QQ Plot проверки нормальности\n{dataset_descriptions[dataset_name]}', 
                    fontsize=14, fontweight='bold')
        
        for i, column in enumerate(df.columns):
            ax = axes[i]
            data = df[column].dropna()
            
            stats.probplot(data, dist="norm", plot=ax)
            ax.set_title(f'{column} QQ Plot')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(dataset_dir / 'qq_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Созданы графики для {dataset_name}")
    
    # 6. Сводный график для сравнения всех датасетов
    print("Создание сводного графика...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for i, (dataset_name, file_path) in enumerate(datasets.items()):
        df = pd.read_csv(file_path)
        
        # Собираем все данные для сводного box plot
        all_data = []
        for col in df.columns:
            data = df[col].dropna()
            for value in data:
                all_data.append({'Dataset': dataset_name, 'Sample': col, 'Value': value})
        
        summary_df = pd.DataFrame(all_data)
        
        ax = axes[i]
        sns.boxplot(data=summary_df, x='Sample', y='Value', ax=ax)
        ax.set_title(f'{dataset_name}\n{dataset_descriptions[dataset_name]}')
        ax.set_ylabel('Значения')
        ax.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Сравнение всех датасетов: Box Plots', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'all_datasets_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Создан сводный график сравнения")
    print(f"\nВсе графики сохранены в папку: {output_dir}")

if __name__ == "__main__":
    create_visualizations()
    print("\nВизуализация завершена успешно!")