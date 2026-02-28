"""
Оркестратор — главный управляющий агент.

Важно: оркестратор — это обычный Python-код, а НЕ LLM.
Он управляет порядком вызова агентов и принимает логические решения
(например, запустить повторную итерацию если оценка низкая).

Это ключевая идея паттерна: LLM выполняет интеллектуальную работу,
Python управляет потоком выполнения.
"""
from agents import researcher, writer, critic


def run_pipeline(topic: str) -> dict:
    """
    Запускает полный конвейер обработки темы.

    Порядок работы:
    1. Исследователь → собирает тезисы
    2. Писатель → пишет статью на основе тезисов
    3. Критик → оценивает статью (балл 1–10)
    4. Если балл < 7: Писатель получает замечания и пишет заново (1 итерация)

    Args:
        topic: тема для статьи

    Returns:
        Словарь с результатами всех этапов.
    """
    print(f"\n{'=' * 60}")
    print(f"  ОРКЕСТРАТОР ЗАПУЩЕН")
    print(f"  Тема: \"{topic}\"")
    print(f"{'=' * 60}\n")

    # --- Шаг 1: Исследователь ---
    print("[1/3] Исследователь работает...")
    research = researcher.run(topic)
    tezis_count = len([l for l in research.strip().split("\n") if l.strip().startswith("-")])
    print(f"  ✓ Собрано {tezis_count} тезисов\n")

    # --- Шаг 2: Писатель (первая попытка) ---
    print("[2/3] Писатель работает...")
    article = writer.run(topic, research)
    word_count = len(article.split())
    print(f"  ✓ Статья написана ({word_count} слов)\n")

    # --- Шаг 3: Критик ---
    print("[3/3] Критик работает...")
    feedback, score = critic.run(topic, article)
    print(f"  ✓ Оценка: {score}/10\n")

    # --- Условная итерация ---
    # Оркестратор принимает решение на основе числового балла от Критика
    if score < 7:
        print(f"  Оценка ниже порога (7). Оркестратор запускает доработку...\n")
        print("[2б] Писатель дорабатывает статью с учётом замечаний...")
        revised = writer.run(topic, research, feedback=feedback)
        if revised and revised.strip():
            article = revised
            print(f"  ✓ Статья доработана ({len(article.split())} слов)\n")
        else:
            print(f"  ⚠ Доработка вернула пустой ответ — оставляем первую версию статьи.\n")
    else:
        print(f"  Оценка выше порога. Доработка не нужна.\n")

    return {
        "topic": topic,
        "research": research,
        "article": article,
        "feedback": feedback,
        "score": score,
    }
