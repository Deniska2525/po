from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from datetime import datetime

router = APIRouter(prefix="/downloads", tags=["downloads"])

@router.post("/track")
def track_download(
    download_data: schemas.DownloadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    product = db.query(models.Product).filter(models.Product.id == download_data.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.downloads_count += 1
    
    download = models.Download(
        user_id=current_user.id,
        product_id=download_data.product_id,
        ip_address=download_data.ip_address or request.client.host,
        user_agent=download_data.user_agent or request.headers.get("user-agent")
    )
    
    db.add(download)
    db.commit()
    
    return {
        "download_url": product.download_url,
        "message": "Download tracked successfully"
    }

@router.get("/stats/product/{product_id}")
def get_product_download_stats(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.developer_id != current_user.id and current_user.role not in ["admin", "superuser"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_stats = db.query(
        func.date(models.Download.downloaded_at).label('date'),
        func.count(models.Download.id).label('count')
    ).filter(
        models.Download.product_id == product_id,
        models.Download.downloaded_at >= thirty_days_ago
    ).group_by(func.date(models.Download.downloaded_at)).all()
    
    return {
        "total_downloads": product.downloads_count,
        "daily_stats": [{"date": str(stat.date), "count": stat.count} for stat in daily_stats]
    }
