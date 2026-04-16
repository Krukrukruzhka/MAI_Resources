import warnings

import numpy as np
import pandas as pd

from scipy import stats
from scipy.stats import norm, uniform, expon, t, beta, lognorm, weibull_min

from models import DistributionType, CriterionType
from plotting import plot_distribution_comparison


warnings.filterwarnings("ignore")


SAMPLE_SIZES = [10, 50, 150, 500, 1000, 5000]
ITERATION_NUMBER = 10
ALPHA = 0.05


def generate_samples(dist_type: DistributionType, n: int):
    """Генерация выборки заданного распределения"""
    if dist_type == DistributionType.NORMAL:
        return norm.rvs(loc=0, scale=1, size=n)

    elif dist_type == DistributionType.UNIFORM:
        return uniform.rvs(loc=0, scale=1, size=n)

    elif dist_type == DistributionType.EXPONENTIAL:
        return expon.rvs(scale=1, size=n)

    elif dist_type == DistributionType.T_STUDENT:
        return t.rvs(df=20, size=n)

    elif dist_type == DistributionType.LOGNORMAL:
        return lognorm.rvs(s=0.4, scale=np.exp(0), size=n)

    elif dist_type == DistributionType.BETA:
        return beta.rvs(a=2, b=2, size=n)

    elif dist_type == DistributionType.WEIBULL:
        return weibull_min.rvs(c=1.3, scale=1, size=n)

    elif dist_type == DistributionType.NORMAL_WITH_NOISE:
        base = norm.rvs(loc=0, scale=1, size=n)
        noise = norm.rvs(loc=0, scale=0.1, size=n)  # Небольшой систематический шум
        return base + noise

    elif dist_type == DistributionType.UNIFORM_WITH_NOISE:
        base = uniform.rvs(loc=0, scale=1, size=n)
        noise = norm.rvs(loc=0, scale=0.05, size=n)  # Небольшой систематический шум
        return base + noise

    elif dist_type == DistributionType.EXPONENTIAL_WITH_NOISE:
        base = expon.rvs(scale=1, size=n)
        noise = norm.rvs(loc=0, scale=0.1, size=n)  # Небольшой систематический шум
        return base + noise

    else:
        raise Exception(f"Unknown distribution type {dist_type}")


def _merge_small_bins(observed: np.ndarray, expected: np.ndarray, min_expected: float = 5.0):
    """
    Объединение малочисленных интервалов для корректности критерия хи-квадрат.

    Асимптотическое приближение статистики χ² к распределению χ²(k-1) корректно
    лишь при достаточно больших ожидаемых частотах E_i. Классическое правило
    (Cochran, 1954): E_i ≥ 5 для каждого интервала.

    Алгоритм: последовательно объединяем соседние интервалы с правого края,
    пока E_i < min_expected, затем аналогично с левого края.

    Параметры:
        observed  — массив наблюдаемых частот O_i
        expected  — массив ожидаемых частот E_i
        min_expected — минимально допустимая ожидаемая частота (по умолчанию 5)

    Возвращает:
        (observed_merged, expected_merged) — массивы после объединения
    """
    obs = list(observed)
    exp = list(expected)

    # Объединяем с правого края
    while len(exp) > 1 and exp[-1] < min_expected:
        obs[-2] += obs[-1]
        exp[-2] += exp[-1]
        obs.pop()
        exp.pop()

    # Объединяем с левого края
    while len(exp) > 1 and exp[0] < min_expected:
        obs[1] += obs[0]
        exp[1] += exp[0]
        obs.pop(0)
        exp.pop(0)

    return np.array(obs), np.array(exp)


def chi_square_test(sample: np.ndarray, h0_distribution: DistributionType):
    """
    Критерий Хи-квадрат Пирсона

    Гипотеза H0: выборка порождена эталонным распределением h0_distribution
    с фиксированными параметрами (N(0,1), U(0,1) или Exp(1)).
    Альтернатива H1: выборка порождена другим распределением.

    Описание: Проверяет гипотезу H0, разбивая область значений на k интервалов
    равной вероятности по эталонному распределению и сравнивая наблюдаемые
    частоты попадания в интервалы с ожидаемыми.

    Выбор числа интервалов k:
        Используется правило Стёрджесса: k = 1 + ⌊log₂(n)⌋,
        где n — объём выборки. Это правило оптимально для распределений,
        близких к нормальному, и даёт разумное число интервалов для
        умеренных объёмов выборки (Sturges, 1926).
        Минимальное число интервалов ограничено снизу значением 2.

    Объединение малочисленных интервалов:
        После построения гистограммы проверяется условие E_i ≥ 5 для
        каждого интервала (Cochran, 1954). Интервалы с E_i < 5
        объединяются с соседними, чтобы обеспечить корректность
        асимптотического приближения статистики χ².

    Формула: χ² = Σ[(O_i - E_i)² / E_i], где:
    - O_i — наблюдаемая частота в i-м интервале
    - E_i — ожидаемая частота в i-м интервале (n/k)
    - Суммирование по всем k интервалам

    Возвращает (True, p_value), если H0 отвергается (p-value < α),
    и (False, p_value), если H0 не отвергается (выборки согласованы).
    """
    n = len(sample)

    # Правило Стёрджесса: k = 1 + floor(log2(n))
    # Sturges H.A. (1926). "The Choice of a Class Interval".
    # Journal of the American Statistical Association, 21(153), 65–66.
    k = max(2, 1 + int(np.floor(np.log2(n))))

    outlier_tol = 0.02

    if h0_distribution == DistributionType.UNIFORM:
        mask = (sample >= 0) & (sample <= 1)
        outside_ratio = 1 - np.mean(mask)

        # Если выбросов слишком много — отвергаем
        if outside_ratio > outlier_tol:
            return True, 0.0

        inside = sample[mask]
        m = len(inside)

        # Если внутри слишком мало точек — тест ненадёжен
        if m < k:
            return True, 0.0

        quantiles = np.linspace(0, 1, k + 1)
        boundaries = uniform.ppf(quantiles, loc=0, scale=1)  # [0,1]

        observed, _ = np.histogram(inside, bins=boundaries)
        expected = np.full(k, m / k)

    elif h0_distribution == DistributionType.NORMAL:
        quantiles = np.linspace(0, 1, k + 1)
        boundaries = norm.ppf(quantiles, loc=0, scale=1)

        observed, _ = np.histogram(sample, bins=boundaries)
        expected = np.full(k, n / k)

    elif h0_distribution == DistributionType.EXPONENTIAL:
        mask = sample >= 0
        outside_ratio = 1 - np.mean(mask)

        if outside_ratio > outlier_tol:
            return True, 0.0

        inside = sample[mask]
        m = len(inside)

        if m < k:
            return True, 0.0

        quantiles = np.linspace(0, 1, k + 1)
        boundaries = expon.ppf(quantiles, scale=1)

        observed, _ = np.histogram(inside, bins=boundaries)
        expected = np.full(k, m / k)
    else:
        raise ValueError(f"Unexpected h0_distribution {h0_distribution}")

    # Объединяем интервалы с E_i < 5 (Cochran, 1954)
    observed, expected = _merge_small_bins(observed, expected, min_expected=5.0)

    # Число степеней свободы: (число интервалов после объединения) - 1
    # Параметры распределения не оцениваются из данных (простая гипотеза)
    df_chi = len(observed) - 1
    if df_chi < 1:
        return True, 0.0

    chi2_stat, p_value = stats.chisquare(observed, expected)
    return p_value < ALPHA, p_value


def ks_test(sample: np.ndarray, h0_distribution: DistributionType):
    """
    Критерий Колмогорова-Смирнова

    Гипотеза H0: выборка порождена эталонным распределением h0_distribution
    с фиксированными параметрами (N(0,1), U(0,1) или Exp(1)).
    Альтернатива H1: выборка порождена другим распределением.

    Описание: Проверяет гипотезу H0, вычисляя максимальное отклонение
    эмпирической функции распределения от теоретической CDF.

    Формула: D_n = sup|F_n(x) - F(x)|, где:
    - F_n(x) — эмпирическая функция распределения
    - F(x) — теоретическая CDF эталонного распределения
    - sup — супремум (максимальное отклонение)

    Возвращает (True, p_value), если H0 отвергается (p-value < α),
    и (False, p_value), если H0 не отвергается (выборки согласованы).
    """
    if h0_distribution == DistributionType.NORMAL:
        cdf_func = lambda x: norm.cdf(x, loc=0, scale=1)
    elif h0_distribution == DistributionType.UNIFORM:
        cdf_func = lambda x: uniform.cdf(x, loc=0, scale=1)
    elif h0_distribution == DistributionType.EXPONENTIAL:
        cdf_func = lambda x: expon.cdf(x, scale=1)
    else:
        raise Exception(f"Unexpected h0_distribution {h0_distribution}")

    ks_stat, p_value = stats.kstest(sample, cdf_func)
    return p_value < ALPHA, p_value


def _ad_statistic(sample: np.ndarray, cdf_func) -> float:
    """
    Вычисление статистики Андерсона-Дарлинга для произвольной CDF
    с фиксированными (известными) параметрами.

    A² = -n - (1/n) * Σ_{i=1}^{n} [(2i-1) * (ln F(x_i) + ln(1 - F(x_{n+1-i})))]
    """
    n = len(sample)
    sorted_sample = np.sort(sample)
    u = cdf_func(sorted_sample)

    # Защита от log(0) и log(1)
    u = np.clip(u, 1e-10, 1 - 1e-10)

    i = np.arange(1, n + 1)
    S = np.sum((2 * i - 1) * (np.log(u) + np.log(1 - u[::-1])))
    A2 = -n - S / n
    return A2


def ad_test(sample: np.ndarray, h0_distribution: DistributionType):
    """
    Критерий Андерсона-Дарлинга

    Гипотеза H0: выборка порождена эталонным распределением h0_distribution
    с фиксированными параметрами (N(0,1), U(0,1) или Exp(1)).
    Альтернатива H1: выборка порождена другим распределением.

    Описание: Модификация критерия Колмогорова-Смирнова, более чувствительная
    к отклонениям в хвостах распределения. Взвешивает отклонения по всей
    области определения, придавая больший вес хвостам.

    Формула: A² = -n - (1/n) * Σ_{i=1}^{n} [(2i-1) * (ln F(x_i) + ln(1 - F(x_{n+1-i})))], где:
    - n — объем выборки
    - F(x_i) — теоретическая CDF эталонного распределения в точке x_i
    - x_i — i-я порядковая статистика (отсортированная выборка)

    Возвращает (True, A²), если H0 отвергается (A² > критического значения),
    и (False, A²), если H0 не отвергается (выборки согласованы).

    Критическое значение для простой гипотезы (параметры известны, не оцениваются):
    - При α=0.05: 2.492
    Источник: Stephens M.A. (1974), EDF Statistics for Goodness of Fit and Some Comparisons.
    """
    # Критическое значение для простой гипотезы (параметры полностью заданы)
    # при α = 0.05 по таблице Стефенса (1974)
    CRITICAL_VALUE = 2.492

    if h0_distribution == DistributionType.NORMAL:
        # FIX: CDF N(0,1) с фиксированными параметрами, без стандартизации
        cdf_func = lambda x: norm.cdf(x, loc=0, scale=1)
        A2 = _ad_statistic(sample, cdf_func)
        return A2 > CRITICAL_VALUE, A2

    elif h0_distribution == DistributionType.UNIFORM:
        # FIX: CDF U(0,1) с фиксированными параметрами, без нормализации по min/max
        cdf_func = lambda x: uniform.cdf(x, loc=0, scale=1)
        A2 = _ad_statistic(sample, cdf_func)
        return A2 > CRITICAL_VALUE, A2

    elif h0_distribution == DistributionType.EXPONENTIAL:
        # FIX: CDF Exp(1) с фиксированными параметрами, без оценки из данных
        cdf_func = lambda x: expon.cdf(x, scale=1)
        A2 = _ad_statistic(sample, cdf_func)
        return A2 > CRITICAL_VALUE, A2

    else:
        raise Exception(f"Unexpected distribution {h0_distribution}")


def calculate_norm_distribution() -> pd.DataFrame:
    """
    С помощью критериев Хи-квадрат Пирсона, Колмогорова-Смирнова, Андерсона-Дарлинга проверяем гипотезу о N(0;1)
    Для распределений:
        * N(0,1)
        * N(0,1) с добавлением небольшого систематического шума
        * Распределение Стьюдента с 20 степенями свободы
        * Логнормальное распределение с параметрами (0, 0.4)
    """

    dist_types = [
        DistributionType.NORMAL,
        DistributionType.NORMAL_WITH_NOISE,
        DistributionType.T_STUDENT,
        DistributionType.LOGNORMAL
    ]

    real_dist = DistributionType.NORMAL

    results = []

    for dist_type in dist_types:
        for sample_size in SAMPLE_SIZES:
            for _ in range(ITERATION_NUMBER):
                sample = generate_samples(dist_type, sample_size)

                chi_verdict, _ = chi_square_test(sample, real_dist)
                ks_verdict, _ = ks_test(sample, real_dist)
                ad_verdict, _ = ad_test(sample, real_dist)

                results.append({
                    "real_dist": real_dist.value,
                    "checked_dist": dist_type.value,
                    "sample_size": sample_size,
                    CriterionType.CHI.value: chi_verdict,
                    CriterionType.KS.value: ks_verdict,
                    CriterionType.AD.value: ad_verdict,
                    "sample": [sample]
                })

    return pd.DataFrame(results)


def calculate_uniform_distribution() -> pd.DataFrame:
    """
    С помощью критериев Хи-квадрат Пирсона, Колмогорова-Смирнова, Андерсона-Дарлинга проверяем гипотезу о R(0;1)
    Для распределений:
        * R(0,1)
        * R(0,1) с добавлением небольшого систематического шума
        * Beta(2, 2)
    """

    dist_types = [
        DistributionType.UNIFORM,
        DistributionType.UNIFORM_WITH_NOISE,
        DistributionType.BETA
    ]

    real_dist = DistributionType.UNIFORM

    results = []

    for dist_type in dist_types:
        for sample_size in SAMPLE_SIZES:
            for _ in range(ITERATION_NUMBER):
                sample = generate_samples(dist_type, sample_size)

                chi_verdict, _ = chi_square_test(sample, real_dist)
                ks_verdict, _ = ks_test(sample, real_dist)
                ad_verdict, _ = ad_test(sample, real_dist)

                results.append({
                    "real_dist": real_dist.value,
                    "checked_dist": dist_type.value,
                    "sample_size": sample_size,
                    CriterionType.CHI.value: chi_verdict,
                    CriterionType.KS.value: ks_verdict,
                    CriterionType.AD.value: ad_verdict,
                    "sample": [sample]
                })

    return pd.DataFrame(results)


def calculate_expon_distribution() -> pd.DataFrame:
    """
    С помощью критериев Хи-квадрат Пирсона, Колмогорова-Смирнова, Андерсона-Дарлинга проверяем гипотезу о Exp(1)
    Для распределений:
        * Exp(1)
        * Exp(1) с добавлением небольшого систематического шума
        * Распределение Вейбулла с k=1.3, λ=1
    """

    dist_types = [
        DistributionType.EXPONENTIAL,
        DistributionType.EXPONENTIAL_WITH_NOISE,
        DistributionType.WEIBULL
    ]

    real_dist = DistributionType.EXPONENTIAL

    results = []

    for dist_type in dist_types:
        for sample_size in SAMPLE_SIZES:
            for _ in range(ITERATION_NUMBER):
                sample = generate_samples(dist_type, sample_size)

                chi_verdict, _ = chi_square_test(sample, real_dist)
                ks_verdict, _ = ks_test(sample, real_dist)
                ad_verdict, _ = ad_test(sample, real_dist)

                results.append({
                    "real_dist": real_dist.value,
                    "checked_dist": dist_type.value,
                    "sample_size": sample_size,
                    CriterionType.CHI.value: chi_verdict,
                    CriterionType.KS.value: ks_verdict,
                    CriterionType.AD.value: ad_verdict,
                    "sample": [sample]
                })

    return pd.DataFrame(results)


def analyze_power_and_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Анализ мощности и чувствительности непараметрических критериев согласия.

    Для каждой комбинации (эталонное распределение, тестируемое распределение, объём выборки)
    по ITERATION_NUMBER повторениям вычисляет долю отвержений H0 каждым критерием.

    Интерпретация доли отвержений:
    - Когда real_dist == checked_dist (H0 верна):
        доля отвержений = оценка вероятности ошибки I рода.
        Ожидаемое значение ≈ α (0.05).
    - Когда real_dist != checked_dist (H0 ложна):
        доля отвержений = оценка мощности критерия.
        Чем ближе к 1.0, тем лучше критерий обнаруживает отличие.

    Чувствительность оценивается по тому, при каком минимальном объёме выборки
    мощность критерия превышает 0.8 (порог надёжного обнаружения).
    """
    criterion_cols = [
        CriterionType.CHI.value,
        CriterionType.KS.value,
        CriterionType.AD.value,
    ]

    # Приводим bool-столбцы к числовому типу (могут быть object после concat с пустым DataFrame)
    for col in criterion_cols:
        df[col] = df[col].astype(float)

    # Агрегируем: для каждой группы считаем долю отвержений (среднее по bool-столбцам)
    agg_df = (
        df.groupby(["real_dist", "checked_dist", "sample_size"])[criterion_cols]
        .mean()
        .reset_index()
    )

    # Определяем тип метрики
    agg_df["metric"] = np.where(
        agg_df["real_dist"] == agg_df["checked_dist"],
        "type_1_error",
        "power",
    )

    # Округляем доли до 4 знаков
    for col in criterion_cols:
        agg_df[col] = agg_df[col].round(4)

    # Определяем чувствительность: минимальный n, при котором мощность >= 0.8
    sensitivity_rows = []
    power_df = agg_df[agg_df["metric"] == "power"]
    for (h0, test), grp in power_df.groupby(["real_dist", "checked_dist"]):
        for col in criterion_cols:
            above = grp[grp[col] >= 0.8]
            min_n = int(above["sample_size"].min()) if len(above) > 0 else None
            sensitivity_rows.append({
                "real_dist": h0,
                "checked_dist": test,
                "criterion": col,
                "min_n_for_power_0.8": min_n,
            })

    sensitivity_df = pd.DataFrame(sensitivity_rows)

    # Объединяем: к основной таблице добавляем сводку по чувствительности
    # через pivot, чтобы получить одну строку на пару распределений
    sens_pivot = sensitivity_df.pivot_table(
        index=["real_dist", "checked_dist"],
        columns="criterion",
        values="min_n_for_power_0.8",
        aggfunc="first",
    ).reset_index()
    sens_pivot.columns.name = None

    # Переименуем столбцы чувствительности
    rename_map = {col: f"sensitivity_{col}" for col in criterion_cols}
    sens_pivot = sens_pivot.rename(columns=rename_map)

    # Мержим чувствительность к основной таблице
    result = agg_df.merge(sens_pivot, on=["real_dist", "checked_dist"], how="left")

    # Для строк type_1_error чувствительность не имеет смысла — ставим NaN
    for col in rename_map.values():
        result.loc[result["metric"] == "type_1_error", col] = np.nan

    result = result.sort_values(
        ["real_dist", "checked_dist", "sample_size"]
    ).reset_index(drop=True)

    return result


# Размеры выборок, для которых строятся графики визуального сравнения.
# Выбраны три характерных размера: малый (50), средний (500), большой (5000),
# чтобы наглядно показать сходимость KDE → PDF и ECDF → CDF при росте n.
PLOT_SAMPLE_SIZES = [50, 500, 5000]


def build_visual_comparisons(df: pd.DataFrame, output_dir: str = "plots"):
    """
    Для каждой комбинации (H0-распределение, фактическое распределение)
    и для выбранных размеров выборки строит панель из трёх графиков:
        1. KDE vs PDF
        2. ECDF vs CDF
        3. Q-Q plot

    Из DataFrame берётся первая итерация (первая выборка) для каждой
    комбинации параметров, чтобы не дублировать графики.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Маппинг: какое H0-распределение проверяется для каждой группы
    h0_map = {
        DistributionType.NORMAL.value: DistributionType.NORMAL,
        DistributionType.NORMAL_WITH_NOISE.value: DistributionType.NORMAL,
        DistributionType.T_STUDENT.value: DistributionType.NORMAL,
        DistributionType.LOGNORMAL.value: DistributionType.NORMAL,
        DistributionType.UNIFORM.value: DistributionType.UNIFORM,
        DistributionType.UNIFORM_WITH_NOISE.value: DistributionType.UNIFORM,
        DistributionType.BETA.value: DistributionType.UNIFORM,
        DistributionType.EXPONENTIAL.value: DistributionType.EXPONENTIAL,
        DistributionType.EXPONENTIAL_WITH_NOISE.value: DistributionType.EXPONENTIAL,
        DistributionType.WEIBULL.value: DistributionType.EXPONENTIAL,
    }

    for sample_size in PLOT_SAMPLE_SIZES:
        subset = df[df["sample_size"] == sample_size]

        # Берём первую итерацию для каждой комбинации (real_dist, checked_dist)
        first_iter = subset.groupby(["real_dist", "checked_dist"]).first().reset_index()

        for _, row in first_iter.iterrows():
            checked_dist_value = row["checked_dist"]
            sample = row["sample"]

            # sample хранится как список из одного массива
            if isinstance(sample, list):
                sample = sample[0]

            h0_dist = h0_map.get(checked_dist_value)
            if h0_dist is None:
                continue

            # Восстанавливаем DistributionType из строкового значения
            sample_dist = DistributionType(checked_dist_value)

            filename = f"{h0_dist.value}_vs_{checked_dist_value}_n{sample_size}.png"
            save_path = os.path.join(output_dir, filename)

            plot_distribution_comparison(
                sample=sample,
                h0_distribution=h0_dist,
                sample_dist=sample_dist,
                sample_size=sample_size,
                save_path=save_path,
            )

    print(f"Графики сохранены в директорию: {output_dir}/")


def main():
    df = pd.DataFrame(columns=["real_dist", "checked_dist", "sample_size", CriterionType.CHI.value, CriterionType.KS.value, CriterionType.AD.value, "sample"])
    df.index.name = "id"

    df = pd.concat([df, calculate_norm_distribution()], ignore_index=True)
    df = pd.concat([df, calculate_uniform_distribution()], ignore_index=True)
    df = pd.concat([df, calculate_expon_distribution()], ignore_index=True)

    df.to_csv("result_tables/results.csv")

    # Анализ мощности и чувствительности
    analysis_df = analyze_power_and_sensitivity(df)
    analysis_df.to_csv("result_tables/analysis.csv", index=False)

    # Построение графиков визуального сравнения распределений
    build_visual_comparisons(df, output_dir="plots")


if __name__ == "__main__":
    main()
