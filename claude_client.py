"""
Единый хелпер для вызова LLM через OpenRouter.
OpenRouter совместим с форматом OpenAI API — просто меняем base_url.
"""
import os
from openai import OpenAI, APIStatusError

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", ""),
)

# Бесплатные модели в порядке приоритета.
# Если первая недоступна — автоматически пробуется следующая.
FREE_MODELS = [
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "deepseek/deepseek-chat:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "openchat/openchat-7b:free",
    "nousresearch/nous-capybara-7b:free",
]

FREE_MODEL = FREE_MODELS[0]  # модель по умолчанию


def call_agent(system: str, user_message: str, model: str = FREE_MODEL) -> str:
    """
    Базовый вызов агента.

    Агент — это не особый объект, а просто вызов LLM с определённым
    системным промптом (который определяет его роль) и входящим сообщением.

    Если указанная модель недоступна (404), автоматически перебирает
    резервные модели из FREE_MODELS.

    Args:
        system: системный промпт — определяет роль и поведение агента
        user_message: входящий запрос (контекст от предыдущих агентов)
        model: модель из каталога OpenRouter

    Returns:
        Текстовый ответ агента.
    """
    if not client.api_key:
        raise ValueError(
            "OPENROUTER_API_KEY не задан. "
            "Получите ключ на https://openrouter.ai и задайте переменную окружения."
        )

    # Если запрошенная модель есть в списке — пробуем её первой,
    # затем остальные по порядку. Если не в списке — только её одну.
    candidates = (
        [model] + [m for m in FREE_MODELS if m != model]
        if model in FREE_MODELS
        else [model]
    )

    last_error = None
    for candidate in candidates:
        try:
            response = client.chat.completions.create(
                model=candidate,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=2048,
            )
            if candidate != model:
                print(f"  (переключился на резервную модель: {candidate})")
            return response.choices[0].message.content
        except APIStatusError as e:
            print(f"  Модель {candidate!r} недоступна (код {e.status_code}), пробую следующую...")
            last_error = e

    raise RuntimeError(
        f"Все модели недоступны. Последняя ошибка: {last_error}"
    )
