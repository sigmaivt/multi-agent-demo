"""
Точка входа в многоагентный конвейер.

Запуск:
    python main.py                          # интерактивный ввод темы
    python main.py "Квантовые вычисления"   # тема из аргумента командной строки
"""
import sys
from orchestrator import run_pipeline


def main():
    # Тема берётся из аргумента командной строки или вводится пользователем
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Введите тему для статьи: ").strip()
        if not topic:
            topic = "Влияние искусственного интеллекта на рынок труда"
            print(f"  (Используется тема по умолчанию: \"{topic}\")")

    # Запускаем конвейер
    result = run_pipeline(topic)

    # Выводим итоговый результат
    print("=" * 60)
    print("  ИТОГОВАЯ СТАТЬЯ")
    print("=" * 60)
    print(result["article"])

    print("\n" + "=" * 60)
    print("  ОЦЕНКА КРИТИКА")
    print("=" * 60)
    print(result["feedback"])
    print()


if __name__ == "__main__":
    main()
