"""
Модуль визуализации для сравнения эмпирических и теоретических распределений.

Содержит три типа графиков:
1. KDE vs PDF — ядерная оценка плотности против теоретической плотности
2. ECDF vs CDF — эмпирическая функция распределения против теоретической
3. Q-Q plot — квантиль-квантильный график

Подробное описание алгоритмов приведено в docstring каждой функции.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from scipy import stats
from scipy.stats import norm, uniform, expon, gaussian_kde

from models import DistributionType


# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────────────────────────────────────

def _get_h0_rv(h0_distribution: DistributionType):
    """
    Возвращает объект scipy.stats frozen distribution для заданного
    эталонного распределения H0.
    """
    if h0_distribution == DistributionType.NORMAL:
        return norm(loc=0, scale=1)
    elif h0_distribution == DistributionType.UNIFORM:
        return uniform(loc=0, scale=1)
    elif h0_distribution == DistributionType.EXPONENTIAL:
        return expon(scale=1)
    else:
        raise ValueError(f"Нет эталонного распределения для {h0_distribution}")


def _get_dist_label(dist_type: DistributionType) -> str:
    """Человекочитаемое название распределения для подписей на графиках."""
    labels = {
        DistributionType.NORMAL: "N(0, 1)",
        DistributionType.UNIFORM: "U(0, 1)",
        DistributionType.EXPONENTIAL: "Exp(1)",
        DistributionType.T_STUDENT: "t(df=20)",
        DistributionType.LOGNORMAL: "LogN(0, 0.4)",
        DistributionType.BETA: "Beta(2, 2)",
        DistributionType.WEIBULL: "Weibull(1.3, 1)",
        DistributionType.NORMAL_WITH_NOISE: "N(0,1) + шум",
        DistributionType.UNIFORM_WITH_NOISE: "U(0,1) + шум",
        DistributionType.EXPONENTIAL_WITH_NOISE: "Exp(1) + шум",
    }
    return labels.get(dist_type, dist_type.value)


def _get_h0_label(h0_distribution: DistributionType) -> str:
    """Название эталонного распределения H0."""
    labels = {
        DistributionType.NORMAL: "N(0, 1)",
        DistributionType.UNIFORM: "U(0, 1)",
        DistributionType.EXPONENTIAL: "Exp(1)",
    }
    return labels.get(h0_distribution, h0_distribution.value)


# ─────────────────────────────────────────────────────────────────────────────
# 1. KDE vs PDF
# ─────────────────────────────────────────────────────────────────────────────

def plot_kde_vs_pdf(
    sample: np.ndarray,
    h0_distribution: DistributionType,
    sample_dist: DistributionType,
    sample_size: int,
    ax: plt.Axes,
):
    """
    Строит на одном графике кривую ядерной оценки плотности (KDE) эмпирических
    данных и кривую теоретической плотности вероятности (PDF) проверяемого
    распределения H0.

    ═══════════════════════════════════════════════════════════════════════════
    Алгоритм KDE (scipy.stats.gaussian_kde):
    ═══════════════════════════════════════════════════════════════════════════

    Ядерная оценка плотности (Kernel Density Estimation) — непараметрический
    метод оценки функции плотности вероятности по выборке.

    Формула:
        f̂(x) = (1 / n·h) · Σᵢ K((x - xᵢ) / h)

    где:
        n   — объём выборки,
        h   — ширина полосы пропускания (bandwidth),
        K   — ядерная функция (kernel),
        xᵢ  — i-й элемент выборки.

    Ядро (kernel):
        scipy.stats.gaussian_kde использует гауссово (нормальное) ядро:
            K(u) = (1 / √(2π)) · exp(-u² / 2)
        Это стандартная плотность N(0,1). Каждое наблюдение «размазывается»
        гауссовым колоколом с шириной h.

    Ширина полосы пропускания (bandwidth):
        По умолчанию используется правило Скотта (Scott's rule):
            h = n^(-1/(d+4))
        где d — размерность данных (для одномерного случая d=1):
            h = n^(-1/5)

        Это правило минимизирует AMISE (Asymptotic Mean Integrated Squared
        Error) для нормально распределённых данных. Для одномерных данных
        scipy дополнительно умножает h на стандартное отклонение выборки σ̂,
        так что фактическая ширина = σ̂ · n^(-1/5).

        Альтернативное правило — Сильвермана (Silverman's rule):
            h = (4σ̂⁵ / 3n)^(1/5) ≈ 1.06 · σ̂ · n^(-1/5)
        Оно также доступно через параметр bw_method='silverman'.

    Реализация в scipy:
        kde = gaussian_kde(data, bw_method='scott')
        kde.evaluate(x_grid)  — вычисляет f̂(x) на сетке точек

    Параметры:
        sample          — одномерная выборка (np.ndarray)
        h0_distribution — эталонное распределение H0
        sample_dist     — фактическое распределение выборки (для подписи)
        sample_size     — объём выборки (для подписи)
        ax              — объект matplotlib Axes для рисования
    """
    rv = _get_h0_rv(h0_distribution)

    # Определяем диапазон для оси X
    x_min = min(sample.min(), rv.ppf(0.001))
    x_max = max(sample.max(), rv.ppf(0.999))
    x_grid = np.linspace(x_min, x_max, 500)

    # --- KDE ---
    # gaussian_kde использует гауссово ядро K(u) = φ(u) и правило Скотта
    # для автоматического выбора bandwidth: h = σ̂ · n^(-1/5)
    kde = gaussian_kde(sample, bw_method="scott")
    kde_values = kde.evaluate(x_grid)

    # --- Теоретическая PDF ---
    pdf_values = rv.pdf(x_grid)

    # --- Рисуем ---
    ax.plot(x_grid, kde_values, label="KDE (Гауссово ядро, Scott)", color="steelblue", linewidth=1.5)
    ax.plot(x_grid, pdf_values, label=f"PDF {_get_h0_label(h0_distribution)}", color="crimson", linewidth=1.5, linestyle="--")
    ax.fill_between(x_grid, kde_values, alpha=0.15, color="steelblue")

    ax.set_xlabel("x")
    ax.set_ylabel("Плотность")
    ax.set_title(f"KDE vs PDF | {_get_dist_label(sample_dist)}, n={sample_size}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


# ─────────────────────────────────────────────────────────────────────────────
# 2. ECDF vs CDF
# ─────────────────────────────────────────────────────────────────────────────

def _compute_ecdf(sample: np.ndarray):
    """
    Вычисление эмпирической функции распределения (ECDF).

    ═══════════════════════════════════════════════════════════════════════════
    Алгоритм ECDF:
    ═══════════════════════════════════════════════════════════════════════════

    Эмпирическая функция распределения (Empirical Cumulative Distribution
    Function) — ступенчатая функция, которая для каждого значения x
    возвращает долю наблюдений в выборке, не превышающих x:

        F̂ₙ(x) = (1/n) · #{i : xᵢ ≤ x}

    где n — объём выборки, xᵢ — элементы выборки.

    Метод построения ступенчатой функции:
        1. Сортируем выборку: x₍₁₎ ≤ x₍₂₎ ≤ ... ≤ x₍ₙ₎
        2. Каждой порядковой статистике x₍ᵢ₎ присваиваем значение i/n
        3. Функция F̂ₙ(x) = 0 при x < x₍₁₎,
           F̂ₙ(x) = i/n при x₍ᵢ₎ ≤ x < x₍ᵢ₊₁₎,
           F̂ₙ(x) = 1 при x ≥ x₍ₙ₎

    Это совпадает с реализацией в statsmodels.distributions.ECDF,
    которая внутри:
        - сортирует данные (np.sort),
        - вычисляет y = np.arange(1, n+1) / n (правосторонняя ECDF),
        - возвращает ступенчатую функцию (side='right' по умолчанию).

    По теореме Гливенко–Кантелли: F̂ₙ(x) → F(x) равномерно п.н. при n → ∞.

    Возвращает:
        (x_sorted, ecdf_values) — отсортированные значения и соответствующие
        значения ECDF.
    """
    x_sorted = np.sort(sample)
    n = len(x_sorted)
    ecdf_values = np.arange(1, n + 1) / n  # F̂ₙ(x₍ᵢ₎) = i/n
    return x_sorted, ecdf_values


def plot_ecdf_vs_cdf(
    sample: np.ndarray,
    h0_distribution: DistributionType,
    sample_dist: DistributionType,
    sample_size: int,
    ax: plt.Axes,
):
    """
    Строит совмещённый график эмпирической функции распределения (ECDF)
    и теоретической функции распределения (CDF).

    ECDF строится как ступенчатая функция (step function) с помощью
    matplotlib.axes.Axes.step(where='post'), что соответствует
    правосторонней ECDF: скачок происходит в точке наблюдения.

    Параметры:
        sample          — одномерная выборка (np.ndarray)
        h0_distribution — эталонное распределение H0
        sample_dist     — фактическое распределение выборки (для подписи)
        sample_size     — объём выборки (для подписи)
        ax              — объект matplotlib Axes для рисования
    """
    rv = _get_h0_rv(h0_distribution)

    # --- ECDF ---
    x_sorted, ecdf_values = _compute_ecdf(sample)

    # --- Теоретическая CDF ---
    x_min = min(sample.min(), rv.ppf(0.001))
    x_max = max(sample.max(), rv.ppf(0.999))
    x_grid = np.linspace(x_min, x_max, 500)
    cdf_values = rv.cdf(x_grid)

    # --- Рисуем ---
    ax.step(x_sorted, ecdf_values, where="post", label="ECDF", color="steelblue", linewidth=1.2)
    ax.plot(x_grid, cdf_values, label=f"CDF {_get_h0_label(h0_distribution)}", color="crimson", linewidth=1.5, linestyle="--")

    ax.set_xlabel("x")
    ax.set_ylabel("F(x)")
    ax.set_title(f"ECDF vs CDF | {_get_dist_label(sample_dist)}, n={sample_size}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Q-Q plot
# ─────────────────────────────────────────────────────────────────────────────

def plot_qq(
    sample: np.ndarray,
    h0_distribution: DistributionType,
    sample_dist: DistributionType,
    sample_size: int,
    ax: plt.Axes,
):
    """
    Строит Q-Q plot (квантиль-квантильный график), сопоставляющий квантили
    выборки с теоретическими квантилями распределения H0.

    ═══════════════════════════════════════════════════════════════════════════
    Алгоритм Q-Q plot:
    ═══════════════════════════════════════════════════════════════════════════

    Q-Q plot (Quantile-Quantile plot) — графический метод сравнения двух
    распределений путём сопоставления их квантилей.

    Построение:
        1. Сортируем выборку: x₍₁₎ ≤ x₍₂₎ ≤ ... ≤ x₍ₙ₎
        2. Для каждой порядковой статистики x₍ᵢ₎ вычисляем
           теоретический квантиль: q_i = F⁻¹(pᵢ), где
           pᵢ = (i - 0.5) / n  — формула Хазена (Hazen plotting position).

           Альтернативные формулы plotting positions:
           - Weibull:  pᵢ = i / (n + 1)
           - Blom:     pᵢ = (i - 3/8) / (n + 1/4)
           - Tukey:    pᵢ = (i - 1/3) / (n + 1/3)

           scipy.stats.probplot использует формулу (i - alpha) / (n + 1 - 2*alpha)
           с alpha=0.5 по умолчанию (формула Филлибена), что для больших n
           близко к формуле Хазена.

        3. Строим точки (q_i, x₍ᵢ₎) на плоскости.
        4. Если выборка действительно из распределения H0, точки ложатся
           на прямую y = x (биссектрису).

    Интерпретация отклонений:
        - S-образный изгиб вверх/вниз → различие в хвостах (тяжёлые/лёгкие)
        - Систематический сдвиг → различие в среднем (location)
        - Наклон ≠ 1 → различие в масштабе (scale)

    Параметры:
        sample          — одномерная выборка (np.ndarray)
        h0_distribution — эталонное распределение H0
        sample_dist     — фактическое распределение выборки (для подписи)
        sample_size     — объём выборки (для подписи)
        ax              — объект matplotlib Axes для рисования
    """
    rv = _get_h0_rv(h0_distribution)

    # Сортируем выборку
    sorted_sample = np.sort(sample)
    n = len(sorted_sample)

    # Вычисляем plotting positions по формуле Хазена: p_i = (i - 0.5) / n
    probabilities = (np.arange(1, n + 1) - 0.5) / n

    # Теоретические квантили: q_i = F⁻¹(p_i)
    theoretical_quantiles = rv.ppf(probabilities)

    # --- Рисуем ---
    ax.scatter(
        theoretical_quantiles, sorted_sample,
        s=8, alpha=0.6, color="steelblue", edgecolors="none",
        label="Квантили выборки"
    )

    # Биссектриса y = x (идеальное совпадение)
    q_min = min(theoretical_quantiles.min(), sorted_sample.min())
    q_max = max(theoretical_quantiles.max(), sorted_sample.max())
    ax.plot([q_min, q_max], [q_min, q_max], color="crimson", linewidth=1.2, linestyle="--", label="y = x")

    ax.set_xlabel(f"Теоретические квантили ({_get_h0_label(h0_distribution)})")
    ax.set_ylabel("Квантили выборки")
    ax.set_title(f"Q-Q plot | {_get_dist_label(sample_dist)}, n={sample_size}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


# ─────────────────────────────────────────────────────────────────────────────
# Комплексная функция построения всех трёх графиков
# ─────────────────────────────────────────────────────────────────────────────

def plot_distribution_comparison(
    sample: np.ndarray,
    h0_distribution: DistributionType,
    sample_dist: DistributionType,
    sample_size: int,
    save_path: str | None = None,
):
    """
    Строит панель из трёх графиков для визуального сравнения выборки
    с теоретическим распределением H0:
        1. KDE vs PDF
        2. ECDF vs CDF
        3. Q-Q plot

    Параметры:
        sample          — одномерная выборка
        h0_distribution — эталонное распределение H0
        sample_dist     — фактическое распределение выборки
        sample_size     — объём выборки
        save_path       — путь для сохранения (если None — показывает plt.show())
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        f"Сравнение: выборка {_get_dist_label(sample_dist)} vs H₀: {_get_h0_label(h0_distribution)}, n={sample_size}",
        fontsize=13, fontweight="bold",
    )

    plot_kde_vs_pdf(sample, h0_distribution, sample_dist, sample_size, axes[0])
    plot_ecdf_vs_cdf(sample, h0_distribution, sample_dist, sample_size, axes[1])
    plot_qq(sample, h0_distribution, sample_dist, sample_size, axes[2])

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


def plot_all_comparisons(
    samples_dict: dict,
    output_dir: str = "plots",
):
    """
    Строит графики для всех комбинаций (выборка, H0) из словаря.

    Параметры:
        samples_dict — словарь вида:
            {
                (h0_dist, sample_dist, sample_size): sample_array,
                ...
            }
        output_dir — директория для сохранения графиков
    """
    os.makedirs(output_dir, exist_ok=True)

    for (h0_dist, sample_dist, sample_size), sample in samples_dict.items():
        filename = f"{h0_dist.value}_vs_{sample_dist.value}_n{sample_size}.png"
        save_path = os.path.join(output_dir, filename)

        plot_distribution_comparison(
            sample=sample,
            h0_distribution=h0_dist,
            sample_dist=sample_dist,
            sample_size=sample_size,
            save_path=save_path,
        )
