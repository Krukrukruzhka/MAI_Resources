import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import os


def marks_histogram():
    """
    Изобразить гистограммы выборок на одном графике
    """

    # Фильтруем только числовые оценки (игнорируем 'Зч')
    df_1_numeric = df_1[df_1['Оценка'].apply(lambda x: str(x).isdigit())].copy()
    df_2_numeric = df_2[df_2['Оценка'].apply(lambda x: str(x).isdigit())].copy()

    df_1_numeric['Оценка'] = df_1_numeric['Оценка'].astype(int)
    df_2_numeric['Оценка'] = df_2_numeric['Оценка'].astype(int)

    plt.figure(figsize=(12, 8))

    x = np.arange(2, 6)
    width = 0.35

    counts_1 = [len(df_1_numeric[df_1_numeric['Оценка'] == i]) for i in range(2, 6)]
    counts_2 = [len(df_2_numeric[df_2_numeric['Оценка'] == i]) for i in range(2, 6)]

    plt.bar(x - width / 2, counts_1, width, label='Person 1', color='#FF69B4', alpha=0.7, edgecolor='black')
    plt.bar(x + width / 2, counts_2, width, label='Person 2', color='#4169E1', alpha=0.7, edgecolor='black')

    plt.title('Сравнение распределения оценок двух студентов', fontsize=16, fontweight='bold')
    plt.xlabel('Оценка', fontsize=12)
    plt.ylabel('Количество оценок', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(x)
    plt.xlim(1.5, 5.5)

    os.makedirs('output_data/charts', exist_ok=True)

    plt.savefig('output_data/charts/comparison_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()


def apply_statistical_tests(sample_1, sample_2, test_names=None):
    """
    Применить статистические критерии к двум выборкам
    """
    
    if test_names is None:
        test_names = ['Колмогоров-Смирнов', 'Омега-квадрат', 'Манна-Уитни']
    
    results = {}
    
    # Критерий Колмогорова-Смирнова
    if 'Колмогоров-Смирнов' in test_names:
        ks_stat, ks_pvalue = stats.ks_2samp(sample_1, sample_2)
        results['Колмогоров-Смирнов'] = ks_pvalue
    
    # Критерий омега-квадрат Смирнова
    if 'Омега-квадрат' in test_names:
        cvm_result = stats.cramervonmises_2samp(sample_1, sample_2)
        results['Омега-квадрат'] = cvm_result.pvalue
    
    # Критерий Манна-Уитни
    if 'Манна-Уитни' in test_names:
        mw_stat, mw_pvalue = stats.mannwhitneyu(sample_1, sample_2, alternative='two-sided')
        results['Манна-Уитни'] = mw_pvalue
    
    return results


def use_criterion():
    """
    Применить критерии Смирнова (Колмогорова-Смирнова), омега-квадрат Смирнова,
    хи-квадрат (попробовать разные варианты выбора числа интервалов, сделать выводы), Манна-Уитни,
    сравнить результаты
    """
    # Подготовка данных - фильтруем только числовые оценки
    df_1_numeric = df_1[df_1['Оценка'].apply(lambda x: str(x).isdigit())].copy()
    df_2_numeric = df_2[df_2['Оценка'].apply(lambda x: str(x).isdigit())].copy()
    
    df_1_numeric['Оценка'] = df_1_numeric['Оценка'].astype(int)
    df_2_numeric['Оценка'] = df_2_numeric['Оценка'].astype(int)
    
    sample_1 = df_1_numeric['Оценка'].values
    sample_2 = df_2_numeric['Оценка'].values

    print("\n")

    print("=== СТАТИСТИЧЕСКИЙ АНАЛИЗ РАСПРЕДЕЛЕНИЙ ОЦЕНОК ===")
    print(f"\tРазмер выборки 1: {len(sample_1)}")
    print(f"\tРазмер выборки 2: {len(sample_2)}")
    print(f"\tСреднее выборки 1: {sample_1.mean():.3f}")
    print(f"\tСреднее выборки 2: {sample_2.mean():.3f}")
    print(f"\tСтандартное отклонение выборки 1: {sample_1.std():.3f}")
    print(f"\tСтандартное отклонение выборки 2: {sample_2.std():.3f}")

    print()
    
    # Применяем основные критерии
    results = apply_statistical_tests(sample_1, sample_2)
    
    # Выводим результаты основных критериев
    for i, (test_name, p_value) in enumerate(results.items(), 1):
        print(f"{i}. КРИТЕРИЙ {test_name.upper()}")
        print(f"\tP-значение: {p_value:.4f}")
        if p_value < 0.05:
            print("\tВывод: Распределения статистически значимо различаются (p < 0.05)")
        else:
            print("\tВывод: Нет статистически значимых различий в распределениях (p >= 0.05)")
        print()

    # 3. Критерий хи-квадрат с разными вариантами интервалов
    print("3. КРИТЕРИЙ ХИ-КВАДРАТ")
    intervals_options = [1, 2, 3, 4, 5]
    
    for n_intervals in intervals_options:
        print(f"\tЧисло интервалов: {n_intervals}")

        # Создаем интервалы от минимальной до максимальной оценки
        min_val = min(sample_1.min(), sample_2.min())
        max_val = max(sample_1.max(), sample_2.max())
        bins = np.linspace(min_val - 0.5, max_val + 0.5, n_intervals + 1)

        hist_1, _ = np.histogram(sample_1, bins=bins)
        hist_2, _ = np.histogram(sample_2, bins=bins)

        contingency_table = np.array([hist_1, hist_2])
        
        # Если есть интервалы с нулевыми частотами, объединяем их с соседними
        if np.any(contingency_table.sum(axis=0) == 0):
            print("\tПредупреждение: Обнаружены интервалы с нулевыми частотами, тест не может быть выполнен\n")
            continue
            
        # Критерий хи-квадрат для независимых выборок
        try:
            chi2_stat, chi2_pvalue, _, _ = stats.chi2_contingency(contingency_table)
            
            print(f"\tСтатистика χ²: {chi2_stat:.4f}")
            print(f"\tP-значение: {chi2_pvalue:.4f}")
            
            if chi2_pvalue < 0.05:
                print("\tВывод: Распределения статистически значимо различаются (p < 0.05)\n")
            else:
                print("\tВывод: Нет статистически значимых различий в распределениях (p >= 0.05)\n")
        except ValueError as e:
            print(f"\tОшибка: {e}")
            print("\tТест не может быть выполнен из-за нулевых ожидаемых частот\n")
    

    print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    for test_name, p_value in results.items():
        significance = "значимо" if p_value < 0.05 else "не значимо"
        print(f"\t{test_name}: p = {p_value:.4f} ({significance})")

    print()

    print("ВЫВОДЫ")
    significant_tests = [name for name, p in results.items() if p < 0.05]
    if significant_tests:
        print(f"\tСтатистически значимые различия обнаружены в тестах: {', '.join(significant_tests)}")
        print("\tЭто означает, что распределения оценок двух студентов статистически различаются.")
    else:
        print("\tСтатистически значимых различий не обнаружено.")
        print("\tЭто означает, что распределения оценок двух студентов статистически не различаются.")


def check_sample_volumes():
    """
    Представим, что одна из двух выборок -- это "до", другая "после". Применить критерий знаков, проверить, что объёмы выборок совпадают
    """
    print("\n")

    print("=== ПРОВЕРКА ОБЪЕМОВ ВЫБОРОК И КРИТЕРИЙ ЗНАКОВ ===")
    df_1_numeric = df_1[df_1['Оценка'].apply(lambda x: str(x).isdigit())].copy()
    df_2_numeric = df_2[df_2['Оценка'].apply(lambda x: str(x).isdigit())].copy()
    
    df_1_numeric['Оценка'] = df_1_numeric['Оценка'].astype(int)
    df_2_numeric['Оценка'] = df_2_numeric['Оценка'].astype(int)
    
    # 1. Проверка совпадения объемов выборок
    print("1. ПРОВЕРКА СОВПАДЕНИЯ ОБЪЕМОВ ВЫБОРОК")
    print(f"Размер выборки 1 (студент 1): {len(df_1_numeric)}")
    print(f"Размер выборки 2 (студент 2): {len(df_2_numeric)}")
    
    if len(df_1_numeric) == len(df_2_numeric):
        print("✓ Объемы выборок совпадают")
    else:
        print("✗ Объемы выборок не совпадают")
        print("Предупреждение: Для парного сравнения объемы выборок должны совпадать")
    
    # 2. Сопоставление оценок по дисциплинам для парного сравнения
    print("\n2. СОПОСТАВЛЕНИЕ ОЦЕНОК ПО ДИСЦИПЛИНАМ")
    marks_1 = {}
    marks_2 = {}
    
    for _, row in df_1_numeric.iterrows():
        discipline = row['Дисциплина']
        marks_1[discipline] = row['Оценка']
    
    for _, row in df_2_numeric.iterrows():
        discipline = row['Дисциплина']
        marks_2[discipline] = row['Оценка']
    
    # Находим общие дисциплины
    common_disciplines = set(marks_1.keys()) & set(marks_2.keys())
    print(f"Количество общих дисциплин: {len(common_disciplines)}")
    
    if len(common_disciplines) == 0:
        print("Нет общих дисциплин для парного сравнения")
        return
    
    # Создаем парные данные
    paired_data = []
    for discipline in common_disciplines:
        paired_data.append((marks_1[discipline], marks_2[discipline]))
    
    print(f"Количество парных наблюдений: {len(paired_data)}")
    
    # 3. Критерий знаков
    print("\n3. КРИТЕРИЙ ЗНАКОВ (SIGN TEST)")
    
    # Вычисляем разности
    differences = []
    positive_count = 0
    negative_count = 0
    zero_count = 0
    
    for mark1, mark2 in paired_data:
        diff = mark1 - mark2
        differences.append(diff)
        if diff > 0:
            positive_count += 1
        elif diff < 0:
            negative_count += 1
        else:
            zero_count += 1
    
    print(f"Количество положительных разностей (студент 1 > студент 2): {positive_count}")
    print(f"Количество отрицательных разностей (студент 1 < студент 2): {negative_count}")
    print(f"Количество нулевых разностей (равные оценки): {zero_count}")
    
    # Исключаем нулевые разности для критерия знаков
    n = positive_count + negative_count
    
    if n > 0:
        # Критерий знаков (биномиальный тест)
        # Нулевая гипотеза: вероятность положительной разности = 0.5
        p_value = stats.binomtest(min(positive_count, negative_count), n, 0.5, alternative='two-sided').pvalue
        
        print(f"\nСтатистика критерия знаков:")
        print(f"Количество ненулевых разностей: {n}")
        print(f"P-значение: {p_value:.4f}")
        
        if p_value < 0.05:
            print("Вывод: Статистически значимые различия между 'до' и 'после' (p < 0.05)")
            if positive_count > negative_count:
                print("Студент 1 имеет статистически значимо более высокие оценки")
            else:
                print("Студент 2 имеет статистически значимо более высокие оценки")
        else:
            print("Вывод: Нет статистически значимых различий между 'до' и 'после' (p >= 0.05)")
    else:
        print("Недостаточно данных для критерия знаков (все разности равны нулю)")


def simulate_normal_distributions():
    """
    Сгенерировать две выборки объемом 50 из стандартного нормального закона N(0;1),
    но вторая выборка будет измененной (три случая):
    1. N(0.2;1) - сдвиг среднего
    2. N(0;4) - увеличение дисперсии
    3. N(0;1) + выбросы (испортить 3-6 значений)
    Применить критерии сравнения распределений, повторить 10 раз
    """
    np.random.seed(42)  # Для воспроизводимости
    
    print("\n=== СИМУЛЯЦИЯ НОРМАЛЬНЫХ РАСПРЕДЕЛЕНИЙ ===")
    print("Генерация выборок объемом 50 из N(0;1) и модифицированных распределений")
    print("Повторение эксперимента 10 раз для уменьшения ошибок генерации\n")
    
    # Критерии для сравнения
    test_names = ['Колмогоров-Смирнов', 'Омега-квадрат', 'Манна-Уитни']
    
    # Случаи для тестирования
    cases = [
        ("N(0.2;1) - сдвиг среднего", lambda: np.random.normal(0.2, 1, 50)),
        ("N(0;4) - увеличение дисперсии", lambda: np.random.normal(0, 2, 50)),
        ("N(0;1) + выбросы", lambda: add_outliers(np.random.normal(0, 1, 50)))
    ]
    
    # Функция для добавления выбросов
    def add_outliers(sample):
        n_outliers = np.random.randint(3, 7)  # 3-6 выбросов
        outlier_indices = np.random.choice(len(sample), n_outliers, replace=False)
        sample_with_outliers = sample.copy()
        # Заменяем выбранные значения на большие (5-10 стандартных отклонений)
        for idx in outlier_indices:
            sample_with_outliers[idx] = np.random.normal(0, 1) + np.random.choice([1, -1]) * np.random.uniform(5, 10)
        return sample_with_outliers
    
    # Результаты по всем повторениям
    all_results = {case_name: {test: [] for test in test_names} for case_name, _ in cases}
    
    # Проводим 10 повторений
    for repetition in range(10):
        print(f"\n--- Повторение {repetition + 1} ---")
        
        # Базовая выборка
        base_sample = np.random.normal(0, 1, 50)
        
        for case_name, modified_sample_generator in cases:
            print(f"\nСлучай: {case_name}")
            
            # Генерируем модифицированную выборку
            modified_sample = modified_sample_generator()
            
            # Применяем критерии с использованием универсальной функции
            results = apply_statistical_tests(base_sample, modified_sample)
            
            for test_name, p_value in results.items():
                all_results[case_name][test_name].append(p_value)
            
            for test_name, p_value in results.items():
                print(f"  {test_name}: p = {p_value:.4f}")
    
    # Анализ результатов
    print("\n=== АНАЛИЗ РЕЗУЛЬТАТОВ (10 ПОВТОРЕНИЙ) ===")
    
    for case_name in all_results:
        print(f"\n{case_name}:")
        
        for test_name in test_names:
            p_values = all_results[case_name][test_name]
            significant_count = sum(1 for p in p_values if p < 0.05)
            avg_pvalue = np.mean(p_values)
            
            print(f"  {test_name}:")
            print(f"    Среднее p-значение: {avg_pvalue:.4f}")
            print(f"    Статистически значимо в {significant_count}/10 повторениях")
            print(f"    Мощность теста: {significant_count/10:.1%}")
    
    # Выводы
    print("\n=== ВЫВОДЫ ===")
    print("1. Критерий Колмогоров-Смирнов: чувствителен к различиям в форме распределения")
    print("2. Критерий омега-квадрат: более мощный для интегральных различий")
    print("3. Критерий Манна-Уитни: чувствителен к различиям в медианах")
    print("4. Мощность тестов зависит от типа различий между распределениями")


if __name__ == "__main__":
    # Загрузка данных из двух разных файлов
    df_1 = pd.read_excel('input_data/marks_person_1.xlsx')[['Семестр', 'Дисциплина', 'Оценка', 'Преподаватель']]
    df_2 = pd.read_excel('input_data/marks_person_2.xlsx')[['Семестр', 'Дисциплина', 'Оценка', 'Преподаватель']]

    marks_histogram()
    use_criterion()
    check_sample_volumes()
    simulate_normal_distributions()