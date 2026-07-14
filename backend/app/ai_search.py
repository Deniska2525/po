"""
ИИ-поиск по каталогу через OpenAI-совместимый Chat Completions API
(tool use / function calling).

Почему именно "OpenAI-совместимый", а не привязка к конкретному провайдеру:
и Groq, и Google Gemini, и OpenRouter выставляют один и тот же интерфейс
(тот же формат запроса/ответа, что и у OpenAI), просто с разным base_url.
Поэтому один и тот же код работает с любым из них — достаточно поменять
3 переменные окружения, ничего не переписывая.

Рекомендуемые БЕСПЛАТНЫЕ провайдеры (не нужна банковская карта):
  - Groq   (по умолчанию) — https://console.groq.com, очень быстрый,
    модели Llama, честный бесплатный тариф без ограничения по дням.
  - Gemini — https://aistudio.google.com/apikey, тоже бессрочно бесплатный
    для моделей Flash/Flash-Lite.

Как это работает:
  1. Пользователь пишет запрос на естественном языке.
  2. Модель получает этот запрос + описание инструмента search_products.
  3. Модель сама решает, с какими фильтрами вызвать поиск — может вызвать
     несколько раз, если нужно уточнить.
  4. Когда модель уверена в результате, она возвращает финальный ответ
     строго в формате JSON: краткое сообщение + id релевантных товаров.
  5. Мы по этим id достаём полные карточки товаров из своей БД — сама
     модель товары не выдумывает, только выбирает id из того, что реально
     нашёл инструмент.
"""
import os
import json
import logging
from openai import OpenAI, APIError
from sqlalchemy.orm import Session
from .product_search import filter_products, product_to_dict

logger = logging.getLogger("ai_search")

# --- Настройка провайдера через переменные окружения ---
# Groq (бесплатно, без карты): AI_BASE_URL=https://api.groq.com/openai/v1
# Gemini (бесплатно, без карты): AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
MAX_TOOL_ITERATIONS = 4  # защита от зацикливания, если модель будет звать инструмент бесконечно

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": (
            "Ищет товары (ПО) в каталоге маркетплейса. Можно вызывать несколько раз "
            "подряд с разными фильтрами, чтобы уточнить поиск. Все параметры необязательны."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "Ключевые слова для поиска по названию/описанию товара",
                },
                "category": {
                    "type": "string",
                    "description": "Категория товара (например: 'Интеграции', 'Аналитика и BI')",
                },
                "min_price": {"type": "number", "description": "Минимальная цена в рублях"},
                "max_price": {"type": "number", "description": "Максимальная цена в рублях"},
            },
        },
    },
}

SYSTEM_PROMPT = """Ты — ассистент маркетплейса программного обеспечения для бизнеса.
Твоя задача: по запросу пользователя на естественном языке найти самые подходящие
товары через инструмент search_products и вернуть их.

Правила:
- Ты ОБЯЗАН вызвать search_products минимум один раз, прежде чем дать финальный
  ответ — даже если запрос кажется расплывчатым. Не отвечай "не найдено" без
  реального вызова инструмента: возможно, каталог просто нужно поискать шире.
- Вызывай search_products столько раз, сколько нужно, чтобы подобрать хорошие варианты
  (например, если по узким ключевым словам ничего не нашлось — попробуй шире).
- Не выдумывай товары и id, которых не было в результатах инструмента.
- Когда закончишь поиск, ответь ТОЛЬКО валидным JSON без markdown и пояснений вокруг,
  строго в формате:
  {"message": "короткий дружелюбный комментарий на русском, 1-2 предложения",
   "product_ids": [список id подходящих товаров, максимум 12, по убыванию релевантности]}
- Если после реального вызова инструмента ничего подходящего не нашлось — верни
  пустой список product_ids и вежливо объясни это в message.
"""


def _run_tool_call(db: Session, tool_input: dict) -> list[dict]:
    results = filter_products(
        db,
        keywords=tool_input.get("keywords"),
        category=tool_input.get("category"),
        min_price=tool_input.get("min_price"),
        max_price=tool_input.get("max_price"),
    )
    return [product_to_dict(p) for p in results]


def _parse_final_json(raw: str) -> dict:
    text = (raw or "").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(text)
        return {
            "message": parsed.get("message", ""),
            "product_ids": parsed.get("product_ids", []),
        }
    except (json.JSONDecodeError, AttributeError):
        # Модель не вернула валидный JSON — отдаём как есть, без товаров,
        # чтобы фронт хотя бы показал текст, а не упал
        return {"message": text or "Не удалось разобрать ответ ИИ.", "product_ids": []}


def ai_search(query: str, db: Session) -> dict:
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "AI_API_KEY не задана в переменных окружения бэкенда — ИИ-поиск не может "
            "работать без ключа (бесплатный ключ можно получить на console.groq.com "
            "или aistudio.google.com/apikey)."
        )

    client = OpenAI(api_key=api_key, base_url=AI_BASE_URL)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    for _ in range(MAX_TOOL_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                tools=[SEARCH_TOOL],
                tool_choice="auto",
                max_tokens=1024,
            )
        except APIError as e:
            # Печатаем в логи Render — там будет видно точную причину (401 —
            # неверный ключ, 400 — что-то не так с форматом запроса, 429 —
            # превышен бесплатный лимит и т.д.)
            logger.error("Ошибка обращения к AI-провайдеру (%s): %s", AI_BASE_URL, e)
            return {
                "message": "ИИ-провайдер сейчас недоступен или вернул ошибку. Попробуйте ещё раз чуть позже.",
                "product_ids": [],
            }

        message = response.choices[0].message

        if not message.tool_calls:
            return _parse_final_json(message.content)

        # Модель хочет вызвать инструмент(ы).
        # ВАЖНО: content не должен быть None — некоторые OpenAI-совместимые
        # провайдеры (в т.ч. Groq) отвечают 400 Bad Request на content: null,
        # хотя формально по спецификации OpenAI это допустимо. Подставляем
        # пустую строку вместо null для совместимости.
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ],
            }
        )
        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            products = _run_tool_call(db, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(products, ensure_ascii=False),
                }
            )

    return {
        "message": "Не удалось завершить поиск за отведённое число шагов, попробуйте переформулировать запрос.",
        "product_ids": [],
    }
