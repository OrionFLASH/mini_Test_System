# -*- coding: utf-8 -*-
"""
main.py — Единая программа тестирования производительности системы

Весь функционал, все режимы, все настройки и конфигурации объединены в одном файле.
Выбор режима работы осуществляется через переменную RUN_MODE в начале файла.

Автор: orionflash + GPT-4
"""

import os
import sys
import time
import signal
import logging
import hashlib
import random
from datetime import datetime
from typing import Dict, Any
import threading
import numpy as np
import psutil
import argparse

# ============================================================================
# ВЫБОР РЕЖИМА РАБОТЫ
# ============================================================================
# Возможные значения:
#   'basic'        — базовый режим (минимальный CLI, только запуск теста)
#   'advanced'     — расширенный режим (поддержка аргументов командной строки, конфигов, интерактива)
#   'interactive'  — всегда запускать интерактивный режим выбора теста
#   'config'       — запуск с определённой конфигурацией (см. TEST_CONFIGS)
RUN_MODE = 'advanced'  # <--- Меняйте это значение для выбора режима

# ============================================================================
# КОНФИГУРАЦИЯ ФАЙЛОВОЙ СИСТЕМЫ
# ============================================================================
FILE_SYSTEM_CONFIG = {
    "base_path": r"/Users/orionflash/Desktop/MyProject/Test_PC_FullLoad/WORK",
    "subdirectories": {
        "logs": {
            "name": "LOGS",
            "description": "Каталог для файлов логов",
            "file_patterns": {
                "info": {
                    "prefix": "LOG1",
                    "level": "INFO",
                    "date_format": "%Y-%m-%d",
                    "extension": ".log",
                    "description": "Файлы логов уровня INFO"
                },
                "debug": {
                    "prefix": "LOG1",
                    "level": "DEBUG",
                    "date_format": "%Y-%m-%d",
                    "extension": ".log",
                    "description": "Файлы логов уровня DEBUG"
                }
            }
        },
        "output": {
            "name": "OUTPUT",
            "description": "Каталог для результатов тестирования",
            "file_patterns": {
                "results": {
                    "prefix": "LOG1",
                    "date_format": "%Y-%m-%d_%H-%M-%S",
                    "extension": ".txt",
                    "description": "Файлы с результатами тестирования"
                }
            }
        }
    },
    "file_naming": {
        "log_format": "{prefix}_{level}_{date}{extension}",
        "results_format": "{prefix}_{test_type}_{date}{extension}",
        "description": "Шаблоны именования файлов"
    }
}

# ============================================================================
# ГЛОБАЛЬНЫЕ НАСТРОЙКИ И СЛОВАРИ
# ============================================================================
LOG_LEVELS = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}

TEST_TYPES = {
    "basic": "Базовое тестирование производительности",
    "hash_calculation": "Расчет хешей SHA-256",
    "bitcoin_mining": "Симуляция майнинга биткойна",
    "matrix_operations": "Операции с матрицами",
    "prime_numbers": "Поиск простых чисел",
    "neural_simulation": "Симуляция нейронных вычислений"
}

LOAD_TYPES = {
    "CPU": "Только процессор",
    "GPU": "Только видеокарта (если доступна)",
    "BOTH": "Процессор и видеокарта",
    "NEURAL": "Нейронные вычисления (имитация)"
}

PROCESSOR_TYPES = {
    "X86": "Intel/AMD x86_64",
    "M": "Apple Silicon M-series"
}

OPERATING_SYSTEMS = {
    "macOS": "Apple macOS",
    "Windows": "Microsoft Windows",
    "Linux": "Linux"
}

TEST_SETTINGS = {
    "min_duration": 10,
    "max_duration": 60,
    "default_duration": 30,
    "interrupt_key": "q",
    "monitoring_interval": 0.5
}

COMPLEXITY_SETTINGS = {
    "hash_calculation": {
        "easy": 100000,
        "medium": 1000000,
        "hard": 10000000
    },
    "bitcoin_mining": {
        "easy": 100000,
        "medium": 500000,
        "hard": 2000000
    },
    "matrix_operations": {
        "easy": 100,
        "medium": 500,
        "hard": 1000
    },
    "prime_numbers": {
        "easy": 100000,
        "medium": 1000000,
        "hard": 5000000
    }
}

LOG_MESSAGES = {
    "program_start": "Программа тестирования производительности запущена",
    "system_info": "Система: {os_name} {os_version}, Процессор: {processor}, Архитектура: {architecture}",
    "test_config": "Тип теста: {test_type}, Нагрузка: {load_type}, Сложность: {complexity}",
    "test_start": "Начало тестирования в {start_time}",
    "test_progress": "Прогресс теста: {progress:.1f}% ({elapsed:.1f}s / {total:.1f}s)",
    "test_complete": "Тест завершен за {duration:.2f} секунд",
    "performance_results": "Результаты производительности: CPU: {cpu_avg:.1f}% (пик: {cpu_peak:.1f}%), RAM: {ram_avg:.1f}% (пик: {ram_peak:.1f}%)",
    "temperature_info": "Температура CPU: {cpu_temp:.1f}°C, GPU: {gpu_temp:.1f}°C",
    "test_interrupted": "Тест прерван пользователем",
    "error_occurred": "Ошибка: {error_message}",
    "program_exit": "Программа завершена",
    "interactive_mode": "Запущен интерактивный режим выбора теста",
    "config_selected": "Выбрана конфигурация: {config_name}"
}

# ============================================================================
# ПРЕДОПРЕДЕЛЕННЫЕ КОНФИГУРАЦИИ ТЕСТОВ
# ============================================================================
TEST_CONFIGS = {
    "quick": {
        "test_type": "basic",
        "load_type": "CPU",
        "complexity": "easy",
        "duration": 10
    },
    "crypto": {
        "test_type": "hash_calculation",
        "load_type": "CPU",
        "complexity": "medium",
        "duration": 20
    },
    "mining": {
        "test_type": "bitcoin_mining",
        "load_type": "CPU",
        "complexity": "medium",
        "duration": 30
    },
    "math": {
        "test_type": "matrix_operations",
        "load_type": "CPU",
        "complexity": "medium",
        "duration": 25
    },
    "prime": {
        "test_type": "prime_numbers",
        "load_type": "CPU",
        "complexity": "easy",
        "duration": 15
    },
    "neural": {
        "test_type": "neural_simulation",
        "load_type": "NEURAL",
        "complexity": "easy",
        "duration": 12
    }
}

# ============================================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ============================================================================
interrupt_flag = False
monitoring_data = {}

# ============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ФАЙЛОВОЙ СИСТЕМОЙ
# ============================================================================

def get_file_path(category: str, file_type: str, **kwargs) -> str:
    """
    Генерирует путь к файлу на основе структурированной конфигурации.
    category: 'logs' или 'output'. file_type: 'info', 'debug', 'results'.
    Дополнительные параметры (например, test_type) подставляются в шаблон имени.
    """
    try:
        base_path = FILE_SYSTEM_CONFIG["base_path"]
        subdir_config = FILE_SYSTEM_CONFIG["subdirectories"][category]
        subdir_name = subdir_config["name"]
        file_pattern = subdir_config["file_patterns"][file_type]
        # Формируем имя файла по шаблону
        if category == "logs":
            date_str = datetime.now().strftime(file_pattern["date_format"])
            filename = FILE_SYSTEM_CONFIG["file_naming"]["log_format"].format(
                prefix=file_pattern["prefix"],
                level=file_pattern["level"],
                date=date_str,
                extension=file_pattern["extension"]
            )
        elif category == "output":
            date_str = datetime.now().strftime(file_pattern["date_format"])
            test_type = kwargs.get("test_type", "unknown")
            filename = FILE_SYSTEM_CONFIG["file_naming"]["results_format"].format(
                prefix=file_pattern["prefix"],
                test_type=test_type,
                date=date_str,
                extension=file_pattern["extension"]
            )
        else:
            raise ValueError(f"Неизвестная категория: {category}")
        return os.path.join(base_path, subdir_name, filename)
    except KeyError as e:
        raise ValueError(f"Ошибка конфигурации файловой системы: {e}")


def setup_directories() -> None:
    """
    Создает необходимые директории для логов и выходных данных.
    Использует структуру FILE_SYSTEM_CONFIG.
    """
    try:
        base_path = FILE_SYSTEM_CONFIG["base_path"]
        for category, config in FILE_SYSTEM_CONFIG["subdirectories"].items():
            subdir_path = os.path.join(base_path, config["name"])
            os.makedirs(subdir_path, exist_ok=True)
    except Exception as e:
        print(f"Ошибка создания директорий: {e}")
        sys.exit(1)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Настраивает систему логирования: файл + консоль.
    Имя файла и путь берутся из FILE_SYSTEM_CONFIG.
    """
    log_path = get_file_path("logs", log_level.lower())
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger = logging.getLogger('SystemPerformanceTest')
    logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
    # Удаляем старые обработчики, чтобы не было дублирования
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def get_system_info() -> Dict[str, str]:
    """
    Получает информацию о системе: ОС, версия, процессор, архитектура, тип процессора, версия Python.
    """
    import platform
    os_name = platform.system()
    os_version = platform.version()
    processor = platform.processor() or platform.machine()
    architecture = platform.machine()
    python_version = platform.python_version()
    # Определяем тип процессора
    if 'arm' in architecture.lower() or 'apple' in processor.lower():
        processor_type = 'M'
    else:
        processor_type = 'X86'
    return {
        "os_name": os_name,
        "os_version": os_version,
        "processor": processor,
        "architecture": architecture,
        "processor_type": processor_type,
        "python_version": python_version
    }


def monitor_system_resources() -> Dict[str, float]:
    """
    Мониторит загрузку CPU, RAM и температуру (если доступно).
    Возвращает словарь со средними и пиковыми значениями.
    """
    cpu_usages = []
    mem_usages = []
    cpu_temps = []
    gpu_temps = []
    start_time = time.time()
    while not interrupt_flag:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        cpu_usages.append(cpu)
        mem_usages.append(mem)
        # Температура CPU (если доступно)
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_temps.append(np.mean([t.current for t in temps['coretemp']]))
            elif 'cpu-thermal' in temps:
                cpu_temps.append(np.mean([t.current for t in temps['cpu-thermal']]))
            # Температура GPU (если доступно)
            if 'amdgpu' in temps:
                gpu_temps.append(np.mean([t.current for t in temps['amdgpu']]))
        except Exception:
            pass
        time.sleep(TEST_SETTINGS["monitoring_interval"])
        if time.time() - start_time > TEST_SETTINGS["max_duration"]:
            break
    # Сохраняем данные мониторинга
    monitoring_data["cpu"] = cpu_usages
    monitoring_data["mem"] = mem_usages
    monitoring_data["cpu_temp"] = cpu_temps
    monitoring_data["gpu_temp"] = gpu_temps
    return monitoring_data


def start_monitoring(duration: float, logger: logging.Logger) -> None:
    """
    Запускает мониторинг ресурсов в отдельном потоке на время теста.
    """
    def monitor_loop():
        monitor_system_resources()
    t = threading.Thread(target=monitor_loop)
    t.daemon = True
    t.start()
    logger.debug("Мониторинг ресурсов запущен")
    time.sleep(duration)
    global interrupt_flag
    interrupt_flag = True
    t.join()
    logger.debug("Мониторинг ресурсов завершен")


# ============================================================================
# ФУНКЦИИ ТЕСТИРОВАНИЯ
# ============================================================================

def basic_performance_test(complexity: str, logger: logging.Logger) -> None:
    """
    Базовое тестирование производительности.
    Выполняет простые математические операции для нагрузки CPU.
    """
    iterations = COMPLEXITY_SETTINGS["hash_calculation"][complexity]
    for i in range(iterations):
        if interrupt_flag:
            break
        result = i * 2 + 1
        result = result ** 2
        result = result % 1000000
        if i % (iterations // 10) == 0:
            logger.debug(f"Базовый тест: {i}/{iterations}")


def hash_calculation_test(complexity: str, logger: logging.Logger) -> None:
    """
    Тест расчета хешей SHA-256.
    Генерирует случайные данные и рассчитывает хеш.
    """
    iterations = COMPLEXITY_SETTINGS["hash_calculation"][complexity]
    for i in range(iterations):
        if interrupt_flag:
            break
        data = f"test_data_{i}_{random.randint(1, 1000000)}".encode('utf-8')
        hash_result = hashlib.sha256(data).hexdigest()
        if i % (iterations // 10) == 0:
            logger.debug(f"Хеш: {i}/{iterations}, Результат: {hash_result[:16]}...")


def bitcoin_mining_simulation(complexity: str, logger: logging.Logger) -> None:
    """
    Симуляция майнинга биткойна.
    Имитирует поиск хеша с определенным количеством нулей.
    """
    iterations = COMPLEXITY_SETTINGS["bitcoin_mining"][complexity]
    for i in range(iterations):
        if interrupt_flag:
            break
        nonce = i
        data = f"block_data_{nonce}".encode('utf-8')
        hash_result = hashlib.sha256(data).hexdigest()
        if hash_result.startswith('00'):
            logger.debug(f"Найден блок! Nonce: {nonce}, Hash: {hash_result[:16]}...")
        if i % (iterations // 10) == 0:
            logger.debug(f"Майнинг: {i}/{iterations}")


def matrix_operations_test(complexity: str, logger: logging.Logger) -> None:
    """
    Тест операций с матрицами.
    Создает матрицы, выполняет умножение, обращение и нахождение собственных значений.
    """
    size = COMPLEXITY_SETTINGS["matrix_operations"][complexity]
    for i in range(10):  # 10 итераций для стабильной нагрузки
        if interrupt_flag:
            break
        # Создание случайных матриц
        matrix_a = np.random.rand(size, size)
        matrix_b = np.random.rand(size, size)
        
        # Матричное умножение
        result = np.dot(matrix_a, matrix_b)
        
        # Обращение матрицы
        try:
            inverse = np.linalg.inv(matrix_a)
        except np.linalg.LinAlgError:
            inverse = np.eye(size)
        
        # Собственные значения
        eigenvalues = np.linalg.eigvals(matrix_a)
        
        logger.debug(f"Матрицы: {i+1}/10, Размер: {size}x{size}")


def prime_numbers_test(complexity: str, logger: logging.Logger) -> None:
    """
    Тест поиска простых чисел.
    Ищет простые числа в заданном диапазоне.
    """
    max_number = COMPLEXITY_SETTINGS["prime_numbers"][complexity]
    
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    primes_found = 0
    for num in range(2, max_number):
        if interrupt_flag:
            break
        if is_prime(num):
            primes_found += 1
        if num % (max_number // 10) == 0:
            logger.debug(f"Простые числа: {num}/{max_number}, Найдено: {primes_found}")


def neural_simulation_test(complexity: str, logger: logging.Logger) -> None:
    """
    Симуляция нейронных вычислений.
    Имитирует прямое и обратное распространение в нейронной сети.
    """
    iterations = COMPLEXITY_SETTINGS["hash_calculation"][complexity]
    input_size = 100
    hidden_size = 50
    output_size = 10
    
    # Создание весов
    weights1 = np.random.randn(input_size, hidden_size) * 0.01
    weights2 = np.random.randn(hidden_size, output_size) * 0.01
    
    for i in range(iterations):
        if interrupt_flag:
            break
        # Входные данные
        inputs = np.random.randn(input_size)
        
        # Прямое распространение
        hidden = np.tanh(np.dot(inputs, weights1))
        outputs = np.tanh(np.dot(hidden, weights2))
        
        # Обратное распространение (упрощенное)
        output_error = outputs - np.random.randn(output_size)
        hidden_error = np.dot(output_error, weights2.T)
        
        if i % (iterations // 10) == 0:
            logger.debug(f"Нейронная сеть: {i}/{iterations}")


# ============================================================================
# ФУНКЦИИ АНАЛИЗА И СОХРАНЕНИЯ
# ============================================================================

def run_performance_test(test_type: str, load_type: str, complexity: str, 
                        duration: float, logger: logging.Logger) -> Dict[str, Any]:
    """
    Запускает тест производительности.
    Настраивает мониторинг, выбирает функцию тестирования и запускает ее.
    """
    logger.info(LOG_MESSAGES["test_start"].format(
        start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    start_time = time.time()
    
    # Запуск мониторинга в отдельном потоке
    monitor_thread = threading.Thread(target=start_monitoring, args=(duration, logger))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Выбор и запуск теста
    test_functions = {
        "basic": basic_performance_test,
        "hash_calculation": hash_calculation_test,
        "bitcoin_mining": bitcoin_mining_simulation,
        "matrix_operations": matrix_operations_test,
        "prime_numbers": prime_numbers_test,
        "neural_simulation": neural_simulation_test
    }
    
    if test_type in test_functions:
        test_functions[test_type](complexity, logger)
    else:
        logger.error(f"Неизвестный тип теста: {test_type}")
        return {"error": f"Неизвестный тип теста: {test_type}"}
    
    # Ожидание завершения мониторинга
    monitor_thread.join()
    
    actual_duration = time.time() - start_time
    logger.info(LOG_MESSAGES["test_complete"].format(duration=actual_duration))
    
    # Анализ результатов
    results = analyze_results(actual_duration, logger)
    results["duration"] = actual_duration
    
    return results


def analyze_results(duration: float, logger: logging.Logger) -> Dict[str, Any]:
    """
    Анализирует результаты тестирования.
    Использует данные мониторинга для расчета средних и пиковых значений.
    """
    if not monitoring_data.get("cpu"): # Проверяем, что данные мониторинга заполнены
        return {"error": "Нет данных мониторинга"}
    
    # Расчет статистики
    cpu_avg = np.mean(monitoring_data["cpu"])
    cpu_peak = np.max(monitoring_data["cpu"])
    ram_avg = np.mean(monitoring_data["mem"])
    ram_peak = np.max(monitoring_data["mem"])
    
    cpu_temp_avg = np.mean(monitoring_data["cpu_temp"]) if monitoring_data["cpu_temp"] else 0
    gpu_temp_avg = np.mean(monitoring_data["gpu_temp"]) if monitoring_data["gpu_temp"] else 0
    
    results = {
        "duration": duration,
        "cpu_usage_avg": cpu_avg,
        "cpu_usage_peak": cpu_peak,
        "memory_usage_avg": ram_avg,
        "memory_usage_peak": ram_peak,
        "cpu_temperature_avg": cpu_temp_avg,
        "gpu_temperature_avg": gpu_temp_avg
    }
    
    logger.info(LOG_MESSAGES["performance_results"].format(
        cpu_avg=cpu_avg, cpu_peak=cpu_peak,
        ram_avg=ram_avg, ram_peak=ram_peak
    ))
    
    if cpu_temp_avg > 0 or gpu_temp_avg > 0:
        logger.info(LOG_MESSAGES["temperature_info"].format(
            cpu_temp=cpu_temp_avg, gpu_temp=gpu_temp_avg
        ))
    
    return results


def save_results_to_file(results: Dict[str, Any], test_config: Dict[str, Any], logger: logging.Logger) -> None:
    """
    Сохраняет результаты тестирования в отдельный файл.
    Форматирует данные в читаемый формат.
    """
    try:
        # Получение пути к файлу результатов
        test_type = test_config.get("test_type", "unknown")
        file_path = get_file_path("output", "results", test_type=test_type)
        filename = os.path.basename(file_path)
        
        # Получение информации о системе
        system_info = get_system_info()
        
        # Создание содержимого файла
        content = []
        content.append("=" * 60)
        content.append("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ СИСТЕМЫ")
        content.append("=" * 60)
        content.append(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Информация о системе
        content.append("ИНФОРМАЦИЯ О СИСТЕМЕ:")
        content.append("-" * 30)
        content.append(f"Операционная система: {system_info['os_name']}")
        content.append(f"Версия ОС: {system_info['os_version']}")
        content.append(f"Процессор: {system_info['processor']}")
        content.append(f"Архитектура: {system_info['architecture']}")
        content.append(f"Тип процессора: {system_info['processor_type']}")
        content.append(f"Версия Python: {system_info['python_version']}")
        content.append("")
        
        # Конфигурация теста
        content.append("КОНФИГУРАЦИЯ ТЕСТА:")
        content.append("-" * 30)
        content.append(f"Тип теста: {test_config.get('test_type', 'N/A')}")
        content.append(f"Тип нагрузки: {test_config.get('load_type', 'N/A')}")
        content.append(f"Сложность: {test_config.get('complexity', 'N/A')}")
        content.append(f"Планируемая продолжительность: {test_config.get('duration', 'N/A')} секунд")
        content.append("")
        
        # Результаты тестирования
        content.append("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        content.append("-" * 30)
        content.append(f"Фактическое время выполнения: {results.get('duration', 0):.2f} секунд")
        content.append("")
        
        # Статистика CPU
        content.append("ЗАГРУЗКА ПРОЦЕССОРА:")
        content.append(f"  Средняя загрузка: {results.get('cpu_usage_avg', 0):.1f}%")
        content.append(f"  Пиковая загрузка: {results.get('cpu_usage_peak', 0):.1f}%")
        content.append("")
        
        # Статистика RAM
        content.append("ИСПОЛЬЗОВАНИЕ ПАМЯТИ:")
        content.append(f"  Среднее использование: {results.get('memory_usage_avg', 0):.1f}%")
        content.append(f"  Пиковое использование: {results.get('memory_usage_peak', 0):.1f}%")
        content.append("")
        
        # Температура (если доступна)
        cpu_temp = results.get('cpu_temperature_avg', 0)
        gpu_temp = results.get('gpu_temperature_avg', 0)
        
        if cpu_temp > 0 or gpu_temp > 0:
            content.append("ТЕМПЕРАТУРА:")
            if cpu_temp > 0:
                content.append(f"  Средняя температура CPU: {cpu_temp:.1f}°C")
            if gpu_temp > 0:
                content.append(f"  Средняя температура GPU: {gpu_temp:.1f}°C")
            content.append("")
        
        # Дополнительная информация
        content.append("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
        content.append("-" * 30)
        logs_dir = os.path.join(FILE_SYSTEM_CONFIG["base_path"], 
                               FILE_SYSTEM_CONFIG["subdirectories"]["logs"]["name"])
        content.append(f"Файл лога: {logs_dir}")
        content.append(f"Время создания отчета: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("=" * 60)
        
        # Запись в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        logger.info(f"Результаты сохранены в файл: {file_path}")
        print(f"\nРезультаты сохранены в файл: {filename}")
        
    except Exception as e:
        logger.error(f"Ошибка сохранения результатов: {e}")
        print(f"Ошибка сохранения результатов: {e}")


# ============================================================================
# ФУНКЦИИ CLI И ИНТЕРАКТИВА
# ============================================================================

def parse_arguments():
    """
    Парсит аргументы командной строки для расширенного режима.
    """
    parser = argparse.ArgumentParser(
        description="Система тестирования производительности компьютера",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py --config mining
  python main.py --interactive
  python main.py --test-type bitcoin_mining --duration 45
        """
    )
    parser.add_argument("--config", "-c", type=str, help="Имя готовой конфигурации (quick, crypto, mining, math, prime, neural)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Интерактивный режим выбора параметров")
    parser.add_argument("--test-type", "-t", type=str, choices=list(TEST_TYPES.keys()), help="Тип теста")
    parser.add_argument("--load-type", "-l", type=str, choices=list(LOAD_TYPES.keys()), help="Тип нагрузки")
    parser.add_argument("--complexity", "-x", type=str, choices=["easy", "medium", "hard"], help="Сложность теста")
    parser.add_argument("--duration", "-d", type=int, help="Продолжительность теста в секундах")
    parser.add_argument("--log-level", type=str, choices=["INFO", "DEBUG"], default="INFO", help="Уровень логирования")
    parser.add_argument("--list-configs", action="store_true", help="Показать список доступных конфигураций")
    return parser.parse_args()


def print_all_configs() -> None:
    """
    Выводит список всех доступных конфигураций.
    """
    print("\n" + "="*60)
    print("ДОСТУПНЫЕ КОНФИГУРАЦИИ ТЕСТОВ")
    print("="*60)
    
    for config_name, config in TEST_CONFIGS.items():
        print(f"\n📋 {config_name.upper()}")
        print(f"   Тип теста: {config['test_type']}")
        print(f"   Тип нагрузки: {config['load_type']}")
        print(f"   Сложность: {config['complexity']}")
        print(f"   Продолжительность: {config['duration']} секунд")
        print(f"   Описание: {TEST_TYPES.get(config['test_type'], 'N/A')}")


def interactive_config_selection() -> Dict[str, Any]:
    """
    Интерактивный выбор конфигурации теста.
    """
    print("\n" + "="*50)
    print("ИНТЕРАКТИВНЫЙ ВЫБОР КОНФИГУРАЦИИ ТЕСТА")
    print("="*50)
    
    # Выбор типа теста
    print("\n📊 Доступные типы тестов:")
    for i, (test_type, description) in enumerate(TEST_TYPES.items(), 1):
        print(f"   {i}. {test_type} — {description}")
    
    while True:
        try:
            choice = int(input(f"\nВыберите тип теста (1-{len(TEST_TYPES)}): ")) - 1
            if 0 <= choice < len(TEST_TYPES):
                test_type = list(TEST_TYPES.keys())[choice]
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
        except ValueError:
            print("❌ Введите число.")
    
    # Выбор типа нагрузки
    print("\n⚡ Доступные типы нагрузки:")
    for i, (load_type, description) in enumerate(LOAD_TYPES.items(), 1):
        print(f"   {i}. {load_type} — {description}")
    
    while True:
        try:
            choice = int(input(f"\nВыберите тип нагрузки (1-{len(LOAD_TYPES)}): ")) - 1
            if 0 <= choice < len(LOAD_TYPES):
                load_type = list(LOAD_TYPES.keys())[choice]
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
        except ValueError:
            print("❌ Введите число.")
    
    # Выбор сложности
    print("\n🎯 Доступные уровни сложности:")
    complexities = ["easy", "medium", "hard"]
    for i, complexity in enumerate(complexities, 1):
        print(f"   {i}. {complexity}")
    
    while True:
        try:
            choice = int(input(f"\nВыберите сложность (1-{len(complexities)}): ")) - 1
            if 0 <= choice < len(complexities):
                complexity = complexities[choice]
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
        except ValueError:
            print("❌ Введите число.")
    
    # Выбор продолжительности
    while True:
        try:
            duration = int(input(f"\nВведите продолжительность теста в секундах ({TEST_SETTINGS['min_duration']}-{TEST_SETTINGS['max_duration']}): "))
            if TEST_SETTINGS['min_duration'] <= duration <= TEST_SETTINGS['max_duration']:
                break
            else:
                print(f"❌ Продолжительность должна быть от {TEST_SETTINGS['min_duration']} до {TEST_SETTINGS['max_duration']} секунд.")
        except ValueError:
            print("❌ Введите число.")
    
    config = {
        "test_type": test_type,
        "load_type": load_type,
        "complexity": complexity,
        "duration": duration
    }
    
    print(f"\n✅ Выбранная конфигурация:")
    print(f"   Тип теста: {test_type}")
    print(f"   Тип нагрузки: {load_type}")
    print(f"   Сложность: {complexity}")
    print(f"   Продолжительность: {duration} секунд")
    
    return config


def signal_handler(signum, frame):
    """
    Обработчик сигналов для корректного завершения.
    Устанавливает флаг прерывания и выводит сообщение.
    """
    global interrupt_flag
    interrupt_flag = True
    print("\n⚠️  Прерывание выполнения (Ctrl+C)")
    print("Завершение программы...")


# ============================================================================
# ОСНОВНЫЕ ФУНКЦИИ ЗАПУСКА
# ============================================================================

def run_basic_mode():
    """
    Запуск базового режима (минимальный CLI).
    """
    # Настройка обработчика сигналов
    signal.signal(signal.SIGINT, signal_handler)
    
    # Создание директорий
    setup_directories()
    
    # Настройка логирования
    logger = setup_logging("INFO")
    
    # Получение информации о системе
    system_info = get_system_info()
    
    # Логирование запуска программы
    logger.info(LOG_MESSAGES["program_start"])
    logger.info(LOG_MESSAGES["system_info"].format(**system_info))
    
    # Настройки теста (можно изменить)
    test_config = {
        "test_type": "bitcoin_mining",
        "load_type": "CPU",
        "complexity": "medium",
        "duration": TEST_SETTINGS["default_duration"]
    }
    
    # Логирование конфигурации теста
    logger.info(LOG_MESSAGES["test_config"].format(**test_config))
    
    try:
        # Запуск теста
        results = run_performance_test(
            test_config["test_type"],
            test_config["load_type"],
            test_config["complexity"],
            test_config["duration"],
            logger
        )
        
        # Сохранение результатов в файл
        save_results_to_file(results, test_config, logger)
        
        # Вывод результатов
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*50)
        print(f"Время выполнения: {results.get('duration', 0):.2f} секунд")
        print(f"Средняя загрузка CPU: {results.get('cpu_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка CPU: {results.get('cpu_usage_peak', 0):.1f}%")
        print(f"Средняя загрузка RAM: {results.get('memory_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка RAM: {results.get('memory_usage_peak', 0):.1f}%")
        
        if results.get('cpu_temperature_avg', 0) > 0:
            print(f"Средняя температура CPU: {results.get('cpu_temperature_avg', 0):.1f}°C")
        if results.get('gpu_temperature_avg', 0) > 0:
            print(f"Средняя температура GPU: {results.get('gpu_temperature_avg', 0):.1f}°C")
        
    except Exception as e:
        logger.error(LOG_MESSAGES["error_occurred"].format(error_message=str(e)))
        print(f"Ошибка: {e}")
    
    finally:
        logger.info(LOG_MESSAGES["program_exit"])
        print("\nПрограмма завершена.")


def run_advanced_mode():
    """
    Запуск расширенного режима (аргументы командной строки, конфиги, интерактив).
    """
    # Парсинг аргументов
    args = parse_arguments()
    
    # Показать список конфигураций и выйти
    if args.list_configs:
        print_all_configs()
        return
    
    # Настройка обработчика сигналов
    signal.signal(signal.SIGINT, signal_handler)
    
    # Создание директорий
    setup_directories()
    
    # Настройка логирования
    logger = setup_logging(args.log_level)
    
    # Получение информации о системе
    system_info = get_system_info()
    
    # Логирование запуска программы
    logger.info(LOG_MESSAGES["program_start"])
    logger.info(LOG_MESSAGES["system_info"].format(**system_info))
    
    # Определение конфигурации теста
    if args.interactive:
        logger.info(LOG_MESSAGES["interactive_mode"])
        test_config = interactive_config_selection()
    elif args.config:
        test_config = TEST_CONFIGS.get(args.config, TEST_CONFIGS["quick"])
        logger.info(LOG_MESSAGES["config_selected"].format(config_name=args.config))
    else:
        # Использование аргументов командной строки или значений по умолчанию
        test_config = {
            "test_type": args.test_type or "bitcoin_mining",
            "load_type": args.load_type or "CPU",
            "complexity": args.complexity or "medium",
            "duration": args.duration or TEST_SETTINGS["default_duration"]
        }
    
    # Логирование конфигурации теста
    logger.info(LOG_MESSAGES["test_config"].format(**test_config))
    
    try:
        # Запуск теста
        results = run_performance_test(
            test_config["test_type"],
            test_config["load_type"],
            test_config["complexity"],
            test_config["duration"],
            logger
        )
        
        # Сохранение результатов в файл
        save_results_to_file(results, test_config, logger)
        
        # Вывод результатов
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*50)
        print(f"Время выполнения: {results.get('duration', 0):.2f} секунд")
        print(f"Средняя загрузка CPU: {results.get('cpu_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка CPU: {results.get('cpu_usage_peak', 0):.1f}%")
        print(f"Средняя загрузка RAM: {results.get('memory_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка RAM: {results.get('memory_usage_peak', 0):.1f}%")
        
        if results.get('cpu_temperature_avg', 0) > 0:
            print(f"Средняя температура CPU: {results.get('cpu_temperature_avg', 0):.1f}°C")
        if results.get('gpu_temperature_avg', 0) > 0:
            print(f"Средняя температура GPU: {results.get('gpu_temperature_avg', 0):.1f}°C")
        
    except Exception as e:
        logger.error(LOG_MESSAGES["error_occurred"].format(error_message=str(e)))
        print(f"Ошибка: {e}")
    
    finally:
        logger.info(LOG_MESSAGES["program_exit"])
        print("\nПрограмма завершена.")


def run_interactive_mode():
    """
    Запуск интерактивного режима.
    """
    # Настройка обработчика сигналов
    signal.signal(signal.SIGINT, signal_handler)
    
    # Создание директорий
    setup_directories()
    
    # Настройка логирования
    logger = setup_logging("INFO")
    
    # Получение информации о системе
    system_info = get_system_info()
    
    # Логирование запуска программы
    logger.info(LOG_MESSAGES["program_start"])
    logger.info(LOG_MESSAGES["system_info"].format(**system_info))
    
    # Интерактивный выбор конфигурации
    logger.info(LOG_MESSAGES["interactive_mode"])
    test_config = interactive_config_selection()
    
    # Логирование конфигурации теста
    logger.info(LOG_MESSAGES["test_config"].format(**test_config))
    
    try:
        # Запуск теста
        results = run_performance_test(
            test_config["test_type"],
            test_config["load_type"],
            test_config["complexity"],
            test_config["duration"],
            logger
        )
        
        # Сохранение результатов в файл
        save_results_to_file(results, test_config, logger)
        
        # Вывод результатов
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*50)
        print(f"Время выполнения: {results.get('duration', 0):.2f} секунд")
        print(f"Средняя загрузка CPU: {results.get('cpu_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка CPU: {results.get('cpu_usage_peak', 0):.1f}%")
        print(f"Средняя загрузка RAM: {results.get('memory_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка RAM: {results.get('memory_usage_peak', 0):.1f}%")
        
        if results.get('cpu_temperature_avg', 0) > 0:
            print(f"Средняя температура CPU: {results.get('cpu_temperature_avg', 0):.1f}°C")
        if results.get('gpu_temperature_avg', 0) > 0:
            print(f"Средняя температура GPU: {results.get('gpu_temperature_avg', 0):.1f}°C")
        
    except Exception as e:
        logger.error(LOG_MESSAGES["error_occurred"].format(error_message=str(e)))
        print(f"Ошибка: {e}")
    
    finally:
        logger.info(LOG_MESSAGES["program_exit"])
        print("\nПрограмма завершена.")


def run_config_mode():
    """
    Запуск с определённой конфигурацией из TEST_CONFIGS.
    """
    # Выбираем конфигурацию (можно изменить)
    config_name = "mining"  # Измените на нужную конфигурацию
    
    # Настройка обработчика сигналов
    signal.signal(signal.SIGINT, signal_handler)
    
    # Создание директорий
    setup_directories()
    
    # Настройка логирования
    logger = setup_logging("INFO")
    
    # Получение информации о системе
    system_info = get_system_info()
    
    # Логирование запуска программы
    logger.info(LOG_MESSAGES["program_start"])
    logger.info(LOG_MESSAGES["system_info"].format(**system_info))
    
    # Получение конфигурации
    test_config = TEST_CONFIGS.get(config_name, TEST_CONFIGS["quick"])
    logger.info(LOG_MESSAGES["config_selected"].format(config_name=config_name))
    
    # Логирование конфигурации теста
    logger.info(LOG_MESSAGES["test_config"].format(**test_config))
    
    try:
        # Запуск теста
        results = run_performance_test(
            test_config["test_type"],
            test_config["load_type"],
            test_config["complexity"],
            test_config["duration"],
            logger
        )
        
        # Сохранение результатов в файл
        save_results_to_file(results, test_config, logger)
        
        # Вывод результатов
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*50)
        print(f"Время выполнения: {results.get('duration', 0):.2f} секунд")
        print(f"Средняя загрузка CPU: {results.get('cpu_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка CPU: {results.get('cpu_usage_peak', 0):.1f}%")
        print(f"Средняя загрузка RAM: {results.get('memory_usage_avg', 0):.1f}%")
        print(f"Пиковая загрузка RAM: {results.get('memory_usage_peak', 0):.1f}%")
        
        if results.get('cpu_temperature_avg', 0) > 0:
            print(f"Средняя температура CPU: {results.get('cpu_temperature_avg', 0):.1f}°C")
        if results.get('gpu_temperature_avg', 0) > 0:
            print(f"Средняя температура GPU: {results.get('gpu_temperature_avg', 0):.1f}°C")
        
    except Exception as e:
        logger.error(LOG_MESSAGES["error_occurred"].format(error_message=str(e)))
        print(f"Ошибка: {e}")
    
    finally:
        logger.info(LOG_MESSAGES["program_exit"])
        print("\nПрограмма завершена.")

# ============================================================================
# ЗАПУСК ПРОГРАММЫ В ЗАВИСИМОСТИ ОТ RUN_MODE
# ============================================================================
if __name__ == "__main__":
    # В зависимости от RUN_MODE вызываем нужный main-функционал
    if RUN_MODE == 'basic':
        run_basic_mode()
    elif RUN_MODE == 'advanced':
        run_advanced_mode()
    elif RUN_MODE == 'interactive':
        run_interactive_mode()
    elif RUN_MODE == 'config':
        run_config_mode()
    else:
        print(f"Неизвестный режим RUN_MODE: {RUN_MODE}")
        sys.exit(1) 