"""
Оркестратор — главный управляющий агент.

Важно: оркестратор — это обычный Python-код, а НЕ LLM.
Он управляет порядком вызова агентов и принимает логические решения
(например, запустить повторную итерацию если оценка низкая).

Это ключевая идея паттерна: LLM выполняет интеллектуальную работу,
Python управляет потоком выполнения.

Версия 2: три исследователя работают ПАРАЛЛЕЛЬНО через ThreadPoolExecutor,
затем Синтезатор объединяет их результаты.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents import researcher, synthesizer, writer, critic


def run_pipeline(topic: str) -> dict:
    """
    Запускает конвейер с параллельными исследователями.

    Порядок работы:
    1. Три Исследователя работают ОДНОВРЕМЕННО по разным аспектам темы
    2. Синтезатор объединяет три блока в единый список тезисов
    3. Писатель пишет статью
    4. Критик оценивает (балл 1–10)
    5. Если балл < 7: Писатель дорабатывает с учётом замечаний

    Args:
        topic: тема для статьи

    Returns:
        Словарь с результатами всех этапов.
    """
    print(f"\n{'=' * 60}")
    print(f"  ОРКЕСТРАТОР ЗАПУЩЕН  [параллельные агенты]")
    print(f"  Тема: \"{topic}\"")
    print(f"{'=' * 60}\n")

    # --- Шаг 1: Три исследователя параллельно ---
    print("[1/4] Три исследователя работают параллельно...")

    aspects = {
        "факты": "ключевые факты, определения и научные данные",
        "примеры": "реальные примеры, кейсы и практические применения",
        "тренды": "актуальные тренды, прогнозы и будущее развитие",
    }

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(researcher.run, topic, desc): name
            for name, desc in aspects.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()
            print(f"  ✓ Исследователь «{name}» завершил работу")

    facts = results["факты"]
    examples = results["примеры"]
    trends = results["тренды"]
    print()

    # --- Шаг 2: Синтезатор объединяет результаты ---
    print("[2/4] Синтезатор объединяет три блока исследований...")
    research = synthesizer.run(topic, facts, examples, trends)
    tezis_count = len([l for l in research.strip().split("\n") if l.strip().startswith("-")])
    print(f"  ✓ Итоговый список: {tezis_count} тезисов\n")

    # --- Шаг 3: Писатель ---
    print("[3/4] Писатель работает...")
    article = writer.run(topic, research)
    word_count = len(article.split())
    print(f"  ✓ Статья написана ({word_count} слов)\n")

    # --- Шаг 4: Критик ---
    print("[4/4] Критик работает...")
    feedback, score = critic.run(topic, article)
    print(f"  ✓ Оценка: {score}/10\n")

    # --- Условная итерация ---
    if score < 7:
        print(f"  Оценка ниже порога (7). Оркестратор запускает доработку...\n")
        print("[3б] Писатель дорабатывает статью с учётом замечаний...")
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
