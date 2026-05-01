import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
from typing import Dict

from data_generator import generate_time_series, SCENARIO_DESCRIPTIONS, SCENARIO_SHORT_NAMES
from statistical_tests import apply_all_tests


matplotlib.use("Agg")
plt.style.use("seaborn-v0_8")

# Цвета для сценариев
COLORS = ["#2196F3", "#4CAF50", "#F44336", "#FF9800", "#9C27B0"]


def _ensure_output_dir() -> Path:
    """Создаёт директорию для графиков и возвращает путь."""
    output_dir = Path("output_data/charts")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def plot_time_series(
    series: Dict[str, np.ndarray],
    descriptions: Dict[str, str],
) -> None:
    """
    Визуализирует все 5 временных рядов на отдельных подграфиках.

    Args:
        series: словарь {название_сценария: массив_значений}
        descriptions: описания сценариев
    """
    output_dir = _ensure_output_dir()
    n = len(next(iter(series.values())))
    t = np.arange(1, n + 1)

    fig, axes = plt.subplots(5, 1, figsize=(14, 16), sharex=True)
    fig.suptitle("Временные ряды для 5 сценариев", fontsize=16, fontweight="bold", y=0.98)

    for idx, (name, values) in enumerate(series.items()):
        ax = axes[idx]
        desc = descriptions.get(name, name)
        color = COLORS[idx % len(COLORS)]

        ax.plot(t, values, color=color, linewidth=0.9, alpha=0.85)
        ax.set_title(f"Сценарий {idx + 1}: {desc}", fontsize=11, fontweight="bold")
        ax.set_ylabel("x(t)")
        ax.grid(True, alpha=0.3)

        # Горизонтальная линия среднего
        mean_val = np.mean(values)
        ax.axhline(mean_val, color="red", linestyle="--", linewidth=0.8, alpha=0.6,
                    label=f"среднее = {mean_val:.2f}")
        ax.legend(loc="upper right", fontsize=9)

    axes[-1].set_xlabel("t", fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    filepath = output_dir / "time_series_all.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ График временных рядов: {filepath}")


def plot_test_results_heatmap(
    results_df: pd.DataFrame,
    short_names: Dict[str, str],
) -> None:
    """
    Тепловая карта p-значений для всех тестов и сценариев.

    Args:
        results_df: DataFrame с результатами тестов
        short_names: короткие названия сценариев
    """
    output_dir = _ensure_output_dir()

    # Формируем pivot-таблицу p-значений
    pivot = results_df.pivot_table(
        index="scenario", columns="test", values="p_value", aggfunc="first"
    )

    # Переименовываем строки
    pivot.index = [short_names.get(s, s) for s in pivot.index]

    # Сокращаем названия тестов для читаемости
    test_short = {
        "Критерий инверсий": "Инверсии",
        "Критерий Вальда-Вольфовица": "Вальд-Вольфовиц",
        "Критерий Рамачандрана-Ранганатана": "Рамачандран-\nРанганатан",
        "Критерий серий знаков первых разностей": "Серии знаков\nпервых разностей",
    }
    pivot.columns = [test_short.get(c, c) for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Рисуем тепловую карту
    im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

    # Подписи осей
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=10, ha="center")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=11)

    # Значения в ячейках
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if np.isnan(val):
                text = "N/A"
                color = "gray"
            else:
                text = f"{val:.4f}"
                color = "white" if val < 0.15 else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=10,
                    fontweight="bold", color=color)

    # Линия уровня значимости
    ax.set_title("Тепловая карта p-значений (α = 0.05)\nЗелёный — H0 принята, Красный — H0 отвергнута",
                 fontsize=13, fontweight="bold", pad=15)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("p-value", fontsize=11)
    # Отмечаем уровень значимости на colorbar
    cbar.ax.axhline(0.05, color="black", linewidth=2, linestyle="--")
    cbar.ax.text(1.5, 0.05, "α=0.05", va="center", fontsize=9, fontweight="bold")

    plt.tight_layout()
    filepath = output_dir / "p_values_heatmap.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Тепловая карта p-значений: {filepath}")


def plot_test_decisions(
    results_df: pd.DataFrame,
    short_names: Dict[str, str],
) -> None:
    """
    Столбчатая диаграмма решений (принята/отвергнута H0) для каждого сценария.

    Args:
        results_df: DataFrame с результатами тестов
        short_names: короткие названия сценариев
    """
    output_dir = _ensure_output_dir()

    scenarios = results_df["scenario"].unique()
    tests = results_df["test"].unique()

    test_short = {
        "Критерий инверсий": "Инверсии",
        "Критерий Вальда-Вольфовица": "Вальд-Вольфовиц",
        "Критерий Рамачандрана-Ранганатана": "Рамачандран-Ранганатан",
        "Критерий серий знаков первых разностей": "Серии знаков\nпервых разностей",
    }

    fig, axes = plt.subplots(1, len(scenarios), figsize=(18, 6), sharey=True)
    fig.suptitle("Результаты проверки гипотезы H0 (ряд случаен) для каждого сценария",
                 fontsize=14, fontweight="bold")

    for idx, scenario in enumerate(scenarios):
        ax = axes[idx]
        scenario_data = results_df[results_df["scenario"] == scenario]

        test_labels = [test_short.get(t, t) for t in scenario_data["test"]]
        decisions = scenario_data["reject_H0"].values.astype(int)
        colors = ["#F44336" if d else "#4CAF50" for d in decisions]

        bars = ax.barh(range(len(test_labels)), [1] * len(test_labels), color=colors, edgecolor="white", height=0.6)

        ax.set_yticks(range(len(test_labels)))
        ax.set_yticklabels(test_labels, fontsize=9)
        ax.set_xlim(0, 1.3)
        ax.set_xticks([])
        ax.set_title(short_names.get(scenario, scenario), fontsize=10, fontweight="bold")

        # Подписи на столбцах
        for i, (bar, decision) in enumerate(zip(bars, decisions)):
            label = "H0 отвергнута" if decision else "H0 принята"
            ax.text(0.5, i, label, ha="center", va="center", fontsize=8, fontweight="bold", color="white")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    filepath = output_dir / "test_decisions.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Диаграмма решений: {filepath}")


def plot_p_values_comparison(
    results_df: pd.DataFrame,
    short_names: Dict[str, str],
) -> None:
    """
    Сравнительная столбчатая диаграмма p-значений по тестам.

    Args:
        results_df: DataFrame с результатами тестов
        short_names: короткие названия сценариев
    """
    output_dir = _ensure_output_dir()

    tests = results_df["test"].unique()
    scenarios = results_df["scenario"].unique()

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, test_name in enumerate(tests):
        ax = axes[idx]
        test_data = results_df[results_df["test"] == test_name]

        labels = [short_names.get(s, s) for s in test_data["scenario"]]
        p_values = test_data["p_value"].values

        bars = ax.bar(range(len(labels)), p_values, color=COLORS, edgecolor="white", width=0.6)

        # Линия уровня значимости
        ax.axhline(0.05, color="red", linestyle="--", linewidth=1.5, label="α = 0.05")

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9, rotation=15, ha="right")
        ax.set_ylabel("p-value", fontsize=10)
        ax.set_title(test_name, fontsize=11, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")

        # Подписи значений
        for bar, pv in zip(bars, p_values):
            if not np.isnan(pv):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{pv:.4f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    fig.suptitle("Сравнение p-значений по критериям", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    filepath = output_dir / "p_values_comparison.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Сравнение p-значений: {filepath}")


def create_all_visualizations(
    series: Dict[str, np.ndarray],
    results_df: pd.DataFrame,
    descriptions: Dict[str, str],
    short_names: Dict[str, str],
) -> None:
    """
    Создаёт все визуализации для лабораторной работы.

    Args:
        series: словарь с временными рядами
        results_df: DataFrame с результатами тестов
        descriptions: полные описания сценариев
        short_names: короткие названия сценариев
    """
    print("\nСоздание визуализаций...")
    plot_time_series(series, descriptions)
    plot_test_results_heatmap(results_df, short_names)
    plot_test_decisions(results_df, short_names)
    plot_p_values_comparison(results_df, short_names)
    print("Все визуализации созданы!")


if __name__ == "__main__":
    series = generate_time_series()
    results = apply_all_tests(series)
    create_all_visualizations(series, results, SCENARIO_DESCRIPTIONS, SCENARIO_SHORT_NAMES)
