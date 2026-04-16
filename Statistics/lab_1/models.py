from enum import Enum


class DistributionType(Enum):
    """Перечисление всех типов распределений, используемых в функции generate_samples"""
    
    NORMAL = "normal"
    UNIFORM = "uniform" 
    EXPONENTIAL = "exponential"
    T_STUDENT = "t_student"
    LOGNORMAL = "lognormal"
    BETA = "beta"
    WEIBULL = "weibull"
    NORMAL_WITH_NOISE = "normal_with_noise"
    UNIFORM_WITH_NOISE = "uniform_with_noise"
    EXPONENTIAL_WITH_NOISE = "exponential_with_noise"


class CriterionType(Enum):
    CHI = "chi_square"
    KS = "kolmogorov_smirnov"
    AD = "anderson_darling"


# Пример использования:
if __name__ == "__main__":
    # Получить все доступные типы распределений
    all_types = [dist_type.value for dist_type in DistributionType]
    print("Доступные типы распределений:")
    for dist_type in DistributionType:
        print(f"  {dist_type.name}: {dist_type.value}")