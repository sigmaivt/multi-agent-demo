"""
Единый хелпер для вызова LLM через OpenRouter.
OpenRouter совместим с форматом OpenAI API — просто меняем base_url.
"""
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", ""),
)

# OpenRouter сам выбирает лучшую доступную бесплатную модель
FREE_MODEL = "z-ai/glm-4.5-air:free"


def call_agent(system: str, user_message: str, model: str = FREE_MODEL) -> str:
    """
    Базовый вызов агента.

    Агент — это не особый объект, а просто вызов LLM с определённым
    системным промптом (который определяет его роль) и входящим сообщением.

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

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        max_tokens=2048,
    )
    actual_model = response.model or model
    print(f"  [модель: {actual_model}]")
    content = response.choices[0].message.content
    return content or ""
