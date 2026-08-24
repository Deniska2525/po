"""
Контекстный ИИ-поиск по каталогу через OpenAI-совместимый Chat Completions API
(tool use / function calling).

Почему именно "OpenAI-совместимый", а не привязка к конкретному провайдеру:
и Groq, и Google Gemini, и OpenRouter выставляют один и тот же интерфейс
(тот же формат запроса/ответа, что и у OpenAI), просто с разным base_url.
Поэтому один и тот же код работает с любым из них — достаточно поменять
3 переменные окружения, ничего не переписывая.

По умолчанию используется OpenRouter с моделью Gemma 4 (google/gemma-4-31b-it) —
у OpenRouter есть бесплатный тариф (":free") без банковской карты, а Gemma 4
поддерживает function calling, что и нужно для tool use в этом файле.
Ключ: https://openrouter.ai/keys

Альтернативные БЕСПЛАТНЫЕ провайдеры (если не подойдёт OpenRouter):
  - Groq   — https://console.groq.com, очень быстрый, модели Llama/GPT-OSS,
    честный бесплатный тариф без ограничения по дням (Gemma 4 там пока нет,
    только старая Gemma 2 9B).
  - Gemini — https://aistudio.google.com/apikey, тоже бессрочно бесплатный
    для моделей Flash/Flash-Lite.

Чем это отличается от обычного поиска по ключевым словам:
пользователь не подбирает слова под каталог, а описывает СВОЮ задачу или
проблему ("не хватает автоматизации техподдержки", "нужно навести порядок
в финансах небольшой команды" и т.п.). Модель:
  1. разбирает, какая потребность стоит за описанием — часто это не одна
     категория, а несколько смежных (например, "порядок в финансах" — это
     и учёт, и отчётность, и, возможно, интеграция с банком);
  2. вызывает search_products столько раз, сколько нужно, пробуя разные
     ключевые слова/категории под разные грани задачи, а не один запрос
     "в лоб";
  3. по итогам формирует не просто список карточек, а мини-консультацию:
     что вообще стоит внедрить и в каком порядке, а затем — под каждую
     рекомендованную карточку короткое обоснование, почему именно она
     закрывает часть задачи пользователя;
  4. как и раньше, товары не выдумываются — только id, которые реально
     были в результатах инструмента.
"""
import os
import json
import logging
from openai import OpenAI, APIError
from sqlalchemy.orm import Session
from .product_search import filter_products, product_to_dict

logger = logging.getLogger("ai_search")

# --- Настройка провайдера через переменные окружения ---
# OpenRouter + Gemma 4 (по умолчанию, бесплатно): AI_BASE_URL=https://openrouter.ai/api/v1
# Groq (бесплатно, без карты):    AI_BASE_URL=https://api.groq.com/openai/v1
# Gemini (бесплатно, без карты):  AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1")
AI_MODEL = os.getenv("AI_MODEL", "google/gemma-4-31b-it:free")
MAX_TOOL_ITERATIONS = 6  # консультация обычно требует нескольких поисков под разные грани задачи

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": (
            "Ищет товары (ПО) в каталоге маркетплейса. Нужно вызывать несколько раз "
            "подряд с разными фильтрами — под разные грани задачи пользователя, а не "
            "только по буквальным словам из его сообщения. Все параметры необязательны."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "Ключевые слова для поиска по названию/описанию/тегам товара",
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

SYSTEM_PROMPT = """Ты — консультант маркетплейса программного обеспечения для бизнеса.

Пользователь описывает СВОЮ задачу, проблему или то, чего ему не хватает —
своими словами, а не в виде поискового запроса. Твоя работа — как у хорошего
консультанта в магазине: сначала понять, что человеку на самом деле нужно,
и только потом предлагать конкретные решения.

Как действовать:
1. Разбери описание на составляющие. Часто за одной фразой пользователя стоит
   несколько разных потребностей (например, "хочу навести порядок в бизнесе" —
   это может быть и учёт, и аналитика, и автоматизация процессов). Не сужай
   задачу до первого попавшегося ключевого слова.
2. Вызови search_products НЕСКОЛЬКО раз с разными формулировками и фильтрами —
   под каждую выявленную грань задачи отдельно, пробуй и узкие, и более широкие
   варианты (категории, синонимы), если узкие ничего не дали. Ты ОБЯЗАН вызвать
   инструмент минимум один раз, даже если запрос кажется расплывчатым или не
   похож на "поисковый".
3. Не выдумывай товары и id, которых не было в результатах инструмента.
4. Когда закончишь поиск, ответь ТОЛЬКО валидным JSON без markdown и пояснений
   вокруг, строго в формате:
   {
     "message": "1-2 предложения: как ты понял задачу пользователя своими словами",
     "advice": ["конкретный шаг или совет №1 — что внедрить и как",
                "шаг/совет №2", "... максимум 5 пунктов"],
     "recommendations": [
       {"product_id": <id из результатов инструмента>,
        "reason": "1 короткое предложение — какую именно часть задачи закрывает этот товар"},
       ...до 12 штук, по убыванию релевантности
     ]
   }
   - "advice" — это практические рекомендации по внедрению (что сделать сначала,
     что потом, на что обратить внимание), а не пересказ списка товаров.
   - Если у пользователя не одна, а несколько потребностей, старайся закрыть
     рекомендациями каждую из них, а не только самую очевидную.
   - Если по задаче в целом или по какой-то её части в каталоге ничего
     подходящего не нашлось — так и напиши в "advice" (например, что стоит
     поискать вне каталога или сформулировать задачу конкретнее), а не
     оставляй пользователя в неведении.
   - Если вообще ничего не нашлось — верни пустой "recommendations" и не
     выдумывай значение через силу.
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


def _empty_result(message: str) -> dict:
    return {"message": message, "advice": [], "recommendations": []}


def _parse_final_json(raw: str) -> dict:
    text = (raw or "").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, AttributeError):
        # Модель не вернула валидный JSON — отдаём как есть, без товаров,
        # чтобы фронт хотя бы показал текст, а не упал
        return _empty_result(text or "Не удалось разобрать ответ ИИ.")

    message = parsed.get("message", "") if isinstance(parsed, dict) else ""
    advice = parsed.get("advice", []) if isinstance(parsed, dict) else []
    if not isinstance(advice, list):
        advice = [str(advice)] if advice else []
    advice = [str(a) for a in advice if str(a).strip()]

    raw_recs = parsed.get("recommendations", []) if isinstance(parsed, dict) else []
    recommendations = []
    if isinstance(raw_recs, list):
        for item in raw_recs:
            if isinstance(item, dict) and "product_id" in item:
                try:
                    recommendations.append({
                        "product_id": int(item["product_id"]),
                        "reason": str(item.get("reason", "")),
                    })
                except (TypeError, ValueError):
                    continue

    return {"message": message, "advice": advice, "recommendations": recommendations}


def ai_search(query: str, db: Session) -> dict:
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "AI_API_KEY не задана в переменных окружения бэкенда — ИИ-поиск не может "
            "работать без ключа (бесплатный ключ можно получить на openrouter.ai/keys, "
            "console.groq.com или aistudio.google.com/apikey)."
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
                max_tokens=1536,
            )
        except APIError as e:
            # Печатаем в логи Render — там будет видно точную причину (401 —
            # неверный ключ, 400 — что-то не так с форматом запроса, 429 —
            # превышен бесплатный лимит и т.д.)
            logger.error("Ошибка обращения к AI-провайдеру (%s): %s", AI_BASE_URL, e)
            return _empty_result("ИИ-провайдер сейчас недоступен или вернул ошибку. Попробуйте ещё раз чуть позже.")

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

    return _empty_result("Не удалось завершить подбор за отведённое число шагов, попробуйте описать задачу иначе.")
