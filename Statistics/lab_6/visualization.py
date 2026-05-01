"""
Визуализация данных и результатов двухфакторного дисперсионного анализа.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from pathlib import Path
from typing import Dict, List

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

OUTPUT_DIR = Path("output_data/charts")


def ensure_output_dir():
    """Создаёт директорию для графиков."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. Визуализация исходных данных (heatmap + профили)
# ============================================================

def plot_scenario_heatmaps(scenarios: Dict):
    """
    Тепловые карты наблюдений для каждого сценария.

    Args:
        scenarios: словарь {key: (Y, params)}
    """
    ensure_output_dir()

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Тепловые карты наблюдений Y_ij по сценариям', fontsize=16, fontweight='bold')

    for idx, (scenario_key, (Y, params)) in enumerate(scenarios.items()):
        ax = axes[idx // 2, idx % 2]
        n, k = Y.shape

        im = ax.imshow(Y, aspect='auto', cmap='YlOrRd')
        ax.set_title(f"{params['name']}\n{params['description']}", fontsize=10)
        ax.set_xlabel('Уровень фактора A')
        ax.set_ylabel('Блок (фактор B)')
        ax.set_xticks(range(k))
        ax.set_xticklabels([f'A{i+1}' for i in range(k)])
        ax.set_yticks(range(n))
        ax.set_yticklabels([f'B{j+1}' for j in range(n)])

        # Подписи значений в ячейках
        for j in range(n):
            for i in range(k):
                ax.text(i, j, f'{Y[j, i]:.1f}', ha='center', va='center',
                        fontsize=7, color='black' if Y[j, i] < Y.mean() + Y.std() else 'white')

        plt.colorbar(im, ax=ax, shrink=0.8)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'scenario_heatmaps.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Тепловые карты сценариев сохранены")


def plot_scenario_profiles(scenarios: Dict):
    """
    Профильные графики: средние по уровням A для каждого блока.

    Args:
        scenarios: словарь {key: (Y, params)}
    """
    ensure_output_dir()

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Профильные графики: значения по уровням фактора A', fontsize=16, fontweight='bold')

    for idx, (scenario_key, (Y, params)) in enumerate(scenarios.items()):
        ax = axes[idx // 2, idx % 2]
        n, k = Y.shape

        x = np.arange(1, k + 1)

        # Линии для каждого блока
        for j in range(n):
            ax.plot(x, Y[j, :], 'o-', alpha=0.4, linewidth=1, markersize=4,
                    label=f'Блок {j+1}' if j < 4 else None)

        # Средние по уровням A
        means = Y.mean(axis=0)
        ax.plot(x, means, 's-', color='black', linewidth=2.5, markersize=8,
                label='Среднее по A', zorder=10)

        ax.set_title(f"{params['name']}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Уровень фактора A')
        ax.set_ylabel('Значение Y')
        ax.set_xticks(x)
        ax.set_xticklabels([f'A{i}' for i in x])
        ax.legend(fontsize=7, loc='upper left', ncol=2)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'scenario_profiles.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Профильные графики сохранены")


def plot_boxplots(scenarios: Dict):
    """
    Box-plot для каждого сценария: распределение по уровням A.

    Args:
        scenarios: словарь {key: (Y, params)}
    """
    ensure_output_dir()

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Box-plot: распределение значений по уровням фактора A', fontsize=16, fontweight='bold')

    for idx, (scenario_key, (Y, params)) in enumerate(scenarios.items()):
        ax = axes[idx // 2, idx % 2]
        n, k = Y.shape

        data_for_box = [Y[:, i] for i in range(k)]
        bp = ax.boxplot(data_for_box, labels=[f'A{i+1}' for i in range(k)],
                        patch_artist=True, notch=True)

        colors = sns.color_palette("husl", k)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        ax.set_title(f"{params['name']}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Уровень фактора A')
        ax.set_ylabel('Значение Y')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'scenario_boxplots.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Box-plot сохранены")


# ============================================================
# 2. Визуализация результатов тестов
# ============================================================

def plot_p_values_comparison(results_df: pd.DataFrame):
    """
    Сравнение p-value различных критериев по сценариям.

    Args:
        results_df: DataFrame с результатами тестов
    """
    ensure_output_dir()

    # Фильтруем только тесты для фактора A
    tests_A = results_df[~results_df['test'].str.contains('\\(B\\)')].copy()

    fig, ax = plt.subplots(figsize=(14, 8))

    scenarios = tests_A['scenario'].unique()
    tests = tests_A['test'].unique()
    x = np.arange(len(scenarios))
    width = 0.8 / len(tests)

    colors = sns.color_palette("husl", len(tests))

    for i, test in enumerate(tests):
        test_data = tests_A[tests_A['test'] == test]
        p_values = []
        for scenario in scenarios:
            row = test_data[test_data['scenario'] == scenario]
            if len(row) > 0:
                p_values.append(row['p_value'].values[0])
            else:
                p_values.append(np.nan)

        offset = (i - len(tests) / 2 + 0.5) * width
        bars = ax.bar(x + offset, p_values, width, label=test, color=colors[i], alpha=0.8)

        # Подписи значений
        for bar, pv in zip(bars, p_values):
            if not np.isnan(pv):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                        f'{pv:.4f}', ha='center', va='bottom', fontsize=7, rotation=45)

    # Линия значимости
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')
    ax.axhline(y=0.01, color='darkred', linestyle=':', linewidth=1.5, label='α = 0.01')

    ax.set_xlabel('Сценарий', fontsize=12)
    ax.set_ylabel('p-value', fontsize=12)
    ax.set_title('Сравнение p-value критериев по сценариям\n(для фактора A)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=10)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'p_values_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Сравнение p-value сохранено")


def plot_p_values_heatmap(results_df: pd.DataFrame):
    """
    Тепловая карта p-value: сценарии × критерии.

    Args:
        results_df: DataFrame с результатами тестов
    """
    ensure_output_dir()

    # Создаём pivot-таблицу
    pivot = results_df.pivot_table(
        values='p_value',
        index='scenario',
        columns='test',
        aggfunc='first'
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    # Маска для NaN
    mask = pivot.isna()

    sns.heatmap(pivot, annot=True, fmt='.4f', cmap='RdYlGn_r',
                mask=mask, ax=ax, linewidths=1, linecolor='white',
                vmin=0, vmax=0.1,
                cbar_kws={'label': 'p-value'})

    ax.set_title('Тепловая карта p-value: сценарии × критерии', fontsize=14, fontweight='bold')
    ax.set_xlabel('Критерий', fontsize=12)
    ax.set_ylabel('Сценарий', fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'p_values_heatmap.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Тепловая карта p-value сохранена")


def plot_test_decisions(results_df: pd.DataFrame):
    """
    Матрица решений: значим / не значим для каждого теста и сценария.

    Args:
        results_df: DataFrame с результатами тестов
    """
    ensure_output_dir()

    pivot = results_df.pivot_table(
        values='significant_005',
        index='scenario',
        columns='test',
        aggfunc='first'
    ).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    mask = pivot.isna()

    cmap = plt.cm.colors.ListedColormap(['#ff6b6b', '#51cf66'])
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap=cmap,
                mask=mask, ax=ax, linewidths=2, linecolor='white',
                vmin=0, vmax=1,
                cbar_kws={'label': '0 = Не значим, 1 = Значим (α=0.05)'})

    # Заменяем числа на текст
    for text in ax.texts:
        val = text.get_text()
        if val == '1':
            text.set_text('✓')
            text.set_fontsize(16)
            text.set_fontweight('bold')
        elif val == '0':
            text.set_text('✗')
            text.set_fontsize(16)
            text.set_fontweight('bold')

    ax.set_title('Матрица решений: значимость критериев (α = 0.05)',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Критерий', fontsize=12)
    ax.set_ylabel('Сценарий', fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'test_decisions.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Матрица решений сохранена")


# ============================================================
# 3. Сравнение одно- и двухфакторного анализа
# ============================================================

def plot_one_vs_two_way_comparison(Y: np.ndarray, scenario_name: str):
    """
    Визуальное сравнение одно- и двухфакторного анализа.

    Показывает, как блочная структура «поглощает» вариацию.

    Args:
        Y: матрица наблюдений (n x k)
        scenario_name: название сценария
    """
    ensure_output_dir()

    from statistical_tests import one_way_anova, two_way_anova

    anova1 = one_way_anova(Y)
    anova2 = two_way_anova(Y)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(f'{scenario_name}: Сравнение одно- и двухфакторного анализа',
                 fontsize=14, fontweight='bold')

    # 1. Разложение SS (однофакторный)
    ax = axes[0]
    labels_1 = ['SS_between\n(фактор A)', 'SS_within\n(остаток)']
    sizes_1 = [anova1['SS_between'], anova1['SS_within']]
    colors_1 = ['#4ecdc4', '#ff6b6b']
    wedges, texts, autotexts = ax.pie(sizes_1, labels=labels_1, colors=colors_1,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontsize': 10})
    ax.set_title(f'Однофакторный ANOVA\nF={anova1["F_statistic"]:.2f}, p={anova1["p_value"]:.4f}',
                 fontsize=11)

    # 2. Разложение SS (двухфакторный)
    ax = axes[1]
    labels_2 = ['SS_A\n(фактор A)', 'SS_B\n(блоки)', 'SS_error\n(остаток)']
    sizes_2 = [anova2['SS_A'], anova2['SS_B'], anova2['SS_error']]
    colors_2 = ['#4ecdc4', '#45b7d1', '#ff6b6b']
    wedges, texts, autotexts = ax.pie(sizes_2, labels=labels_2, colors=colors_2,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontsize': 10})
    ax.set_title(f'Двухфакторный ANOVA\nF_A={anova2["F_A"]:.2f}, p_A={anova2["p_value_A"]:.4f}',
                 fontsize=11)

    # 3. Сравнение F-статистик
    ax = axes[2]
    tests = ['Однофакт.\nФишер', 'Двухфакт.\nФишер (A)']
    f_values = [anova1['F_statistic'], anova2['F_A']]
    p_values = [anova1['p_value'], anova2['p_value_A']]
    colors_bar = ['#4ecdc4', '#45b7d1']

    bars = ax.bar(tests, f_values, color=colors_bar, alpha=0.8, edgecolor='black')

    for bar, f_val, p_val in zip(bars, f_values, p_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'F={f_val:.2f}\np={p_val:.4f}', ha='center', va='bottom', fontsize=10)

    # Критическое значение F
    from scipy import stats as sp_stats
    n, k = Y.shape
    f_crit_1 = sp_stats.f.ppf(0.95, k - 1, n * k - k)
    f_crit_2 = sp_stats.f.ppf(0.95, k - 1, (k - 1) * (n - 1))
    ax.axhline(y=f_crit_2, color='red', linestyle='--', linewidth=1.5,
               label=f'F_крит (2-факт.) = {f_crit_2:.2f}')

    ax.set_ylabel('F-статистика', fontsize=12)
    ax.set_title('Сравнение F-статистик', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'one_vs_two_way_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Сравнение одно- и двухфакторного анализа сохранено")


# ============================================================
# 4. Визуализация рангов (для Фридмана и Пейджа)
# ============================================================

def plot_rank_analysis(scenarios: Dict):
    """
    Визуализация рангов для критериев Фридмана и Пейджа.

    Args:
        scenarios: словарь {key: (Y, params)}
    """
    ensure_output_dir()
    from scipy import stats as sp_stats

    # Берём только сценарии 1 и 2 (для Пейджа)
    selected = {k: v for k, v in scenarios.items() if k in ['scenario_1', 'scenario_2']}

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Анализ рангов для критериев Фридмана и Пейджа', fontsize=16, fontweight='bold')

    for idx, (scenario_key, (Y, params)) in enumerate(selected.items()):
        n, k = Y.shape

        # Ранжируем внутри каждого блока
        ranks = np.zeros_like(Y, dtype=float)
        for j in range(n):
            ranks[j, :] = sp_stats.rankdata(Y[j, :])

        # Тепловая карта рангов
        ax = axes[idx, 0]
        im = ax.imshow(ranks, aspect='auto', cmap='YlGnBu')
        ax.set_title(f"{params['name']}: Ранги внутри блоков", fontsize=11)
        ax.set_xlabel('Уровень фактора A')
        ax.set_ylabel('Блок')
        ax.set_xticks(range(k))
        ax.set_xticklabels([f'A{i+1}' for i in range(k)])
        ax.set_yticks(range(n))
        ax.set_yticklabels([f'B{j+1}' for j in range(n)])

        for j in range(n):
            for i in range(k):
                ax.text(i, j, f'{ranks[j, i]:.0f}', ha='center', va='center',
                        fontsize=10, fontweight='bold')

        plt.colorbar(im, ax=ax, shrink=0.8)

        # Суммы рангов
        ax = axes[idx, 1]
        R = ranks.sum(axis=0)
        x = np.arange(1, k + 1)
        bars = ax.bar(x, R, color=sns.color_palette("husl", k), alpha=0.8, edgecolor='black')

        # Ожидаемые суммы рангов при H0
        expected_R = n * (k + 1) / 2
        ax.axhline(y=expected_R, color='red', linestyle='--', linewidth=2,
                    label=f'Ожидаемое при H0 = {expected_R:.1f}')

        for bar, r in zip(bars, R):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f'{r:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_xlabel('Уровень фактора A', fontsize=11)
        ax.set_ylabel('Сумма рангов', fontsize=11)
        ax.set_title(f"{params['name']}: Суммы рангов по уровням A", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([f'A{i}' for i in x])
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'rank_analysis.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Анализ рангов сохранён")


# ============================================================
# 5. Сводная визуализация: влияние выбросов и тяжёлых хвостов
# ============================================================

def plot_robustness_comparison(scenarios: Dict):
    """
    Сравнение робастности критериев: сценарий 1 (норма) vs сценарий 3 (Лаплас + выброс).

    Args:
        scenarios: словарь {key: (Y, params)}
    """
    ensure_output_dir()
    from statistical_tests import friedman_test, two_way_anova

    Y1, params1 = scenarios['scenario_1']
    Y3, params3 = scenarios['scenario_3']

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Робастность критериев: нормальный шум vs Лаплас + выброс',
                 fontsize=14, fontweight='bold')

    # 1. Распределение остатков
    ax = axes[0]
    n1, k1 = Y1.shape
    n3, k3 = Y3.shape

    residuals_1 = Y1 - Y1.mean(axis=0)[np.newaxis, :] - Y1.mean(axis=1)[:, np.newaxis] + Y1.mean()
    residuals_3 = Y3 - Y3.mean(axis=0)[np.newaxis, :] - Y3.mean(axis=1)[:, np.newaxis] + Y3.mean()

    ax.hist(residuals_1.flatten(), bins=15, alpha=0.6, label='Сценарий 1 (норм.)',
            color='#4ecdc4', edgecolor='black', density=True)
    ax.hist(residuals_3.flatten(), bins=15, alpha=0.6, label='Сценарий 3 (Лаплас)',
            color='#ff6b6b', edgecolor='black', density=True)
    ax.set_title('Распределение остатков', fontsize=11)
    ax.set_xlabel('Остаток')
    ax.set_ylabel('Плотность')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # 2. Сравнение p-value
    ax = axes[1]
    friedman_1 = friedman_test(Y1)
    friedman_3 = friedman_test(Y3)
    anova_1 = two_way_anova(Y1)
    anova_3 = two_way_anova(Y3)

    tests = ['Фридман', 'Фишер (A)']
    p_sc1 = [friedman_1['p_value'], anova_1['p_value_A']]
    p_sc3 = [friedman_3['p_value'], anova_3['p_value_A']]

    x = np.arange(len(tests))
    width = 0.35

    bars1 = ax.bar(x - width / 2, p_sc1, width, label='Сценарий 1 (норм.)',
                   color='#4ecdc4', alpha=0.8, edgecolor='black')
    bars3 = ax.bar(x + width / 2, p_sc3, width, label='Сценарий 3 (Лаплас+выброс)',
                   color='#ff6b6b', alpha=0.8, edgecolor='black')

    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')

    for bar, pv in zip(bars1, p_sc1):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                f'{pv:.4f}', ha='center', va='bottom', fontsize=9)
    for bar, pv in zip(bars3, p_sc3):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                f'{pv:.4f}', ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('p-value', fontsize=11)
    ax.set_title('Сравнение p-value', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(tests)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # 3. Сравнение F-статистик
    ax = axes[2]
    f_values = [anova_1['F_A'], anova_3['F_A']]
    labels = ['Сценарий 1\n(норм.)', 'Сценарий 3\n(Лаплас+выброс)']
    colors = ['#4ecdc4', '#ff6b6b']

    bars = ax.bar(labels, f_values, color=colors, alpha=0.8, edgecolor='black')
    for bar, fv in zip(bars, f_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'F={fv:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('F-статистика (фактор A)', fontsize=11)
    ax.set_title('Влияние выбросов на F-статистику', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'robustness_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Сравнение робастности сохранено")


# ============================================================
# Главная функция визуализации
# ============================================================

def create_all_visualizations(scenarios: Dict, results_df: pd.DataFrame):
    """
    Создаёт все визуализации.

    Args:
        scenarios: словарь {key: (Y, params)}
        results_df: DataFrame с результатами тестов
    """
    print("\nСоздание визуализаций:")
    print("-" * 40)

    # Данные
    plot_scenario_heatmaps(scenarios)
    plot_scenario_profiles(scenarios)
    plot_boxplots(scenarios)

    # Результаты тестов
    plot_p_values_comparison(results_df)
    plot_p_values_heatmap(results_df)
    plot_test_decisions(results_df)

    # Ранговый анализ
    plot_rank_analysis(scenarios)

    # Робастность
    plot_robustness_comparison(scenarios)

    # Сравнение одно- и двухфакторного (для сценария 2)
    Y2, params2 = scenarios['scenario_2']
    plot_one_vs_two_way_comparison(Y2, params2['name'])

    print(f"\nВсе визуализации сохранены в {OUTPUT_DIR}/")


if __name__ == "__main__":
    from data_generator import generate_all_scenarios
    from statistical_tests import apply_all_tests

    scenarios = generate_all_scenarios()
    results_df = apply_all_tests(scenarios)
    create_all_visualizations(scenarios, results_df)
