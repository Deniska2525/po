import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..ai_search import ai_search

logger = logging.getLogger("ai_search")
router = APIRouter(prefix="/ai-search", tags=["ai-search"])


@router.post("/", response_model=schemas.AISearchResponse)
def ai_search_endpoint(payload: schemas.AISearchRequest, db: Session = Depends(get_db)):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Пустой запрос")

    try:
        result = ai_search(query, db)
    except RuntimeError as e:
        # AI_API_KEY не задана — понятная ошибка вместо 500
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        # Любая другая непредвиденная ошибка при обращении к AI-провайдеру —
        # полный traceback пишем в логи Render (exc_info=True), пользователю
        # отдаём понятное сообщение вместо голого 500
        logger.exception("Непредвиденная ошибка в ai_search для запроса: %s", query)
        raise HTTPException(
            status_code=502,
            detail="Не удалось выполнить ИИ-поиск. Попробуйте ещё раз чуть позже.",
        )

    advice = result.get("advice", [])
    recs = result.get("recommendations", [])
    product_ids = [r["product_id"] for r in recs]
    products = (
        db.query(models.Product)
        .filter(models.Product.id.in_(product_ids), models.Product.is_active == True)
        .all()
    )
    # Сохраняем порядок релевантности и обоснование, которые выбрал ИИ
    by_id = {p.id: p for p in products}
    reasons_by_id = {r["product_id"]: r.get("reason", "") for r in recs}
    recommendations = [
        {"product": by_id[r["product_id"]], "reason": reasons_by_id.get(r["product_id"], "")}
        for r in recs
        if r["product_id"] in by_id
    ]

    return {
        "message": result.get("message", ""),
        "advice": advice,
        "recommendations": recommendations,
    }
