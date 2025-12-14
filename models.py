# models.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class BookCreate(BaseModel):
    """
    用於 POST 和 PUT 請求的書籍資料模型。
    所有欄位皆為可選 (Optional)，但 price 驗證器確保其 > 0。
    """
    title: Optional[str] = Field(None, min_length=1, description="書名")
    author: Optional[str] = Field(None, min_length=1, description="作者")
    publisher: Optional[str] = Field(None, description="出版社")
    price: Optional[int] = Field(None, gt=0, description="價格 (台幣, 必須大於 0)")
    publish_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="出版日期 (格式 YYYY-MM-DD)")
    isbn: Optional[str] = Field(None, description="ISBN")
    cover_url: Optional[str] = Field(None, description="封面圖片 URL")

    @validator('price', always=True)
    def validate_price_on_create(cls, v, values, **kwargs):
        """檢查 price 在存在時是否大於 0。"""
        if v is not None and v <= 0:
            raise ValueError('price must be greater than 0')
        return v

    class Config:
        # 將 schema_extra 替換為 json_schema_extra
        json_schema_extra = {
            "example": {
                "title": "測試書",
                "author": "我",
                "price": 999,
                "publisher": "某出版社",
                "publish_date": "2025-12-31"
            }
        }

class BookResponse(BaseModel):
    """
    用於 API 回傳的書籍資料模型。
    包含 id 和 created_at 欄位。
    """
    id: int = Field(..., description="書籍 ID")
    title: str = Field(..., description="書名")
    author: str = Field(..., description="作者")
    publisher: Optional[str] = Field(None, description="出版社")
    price: int = Field(..., gt=0, description="價格 (台幣)")
    publish_date: Optional[str] = Field(None, description="出版日期 (格式 YYYY-MM-DD)")
    isbn: Optional[str] = Field(None, description="ISBN")
    cover_url: Optional[str] = Field(None, description="封面圖片 URL")
    created_at: datetime = Field(..., description="建立時間戳")

    class Config:
        # 將 orm_mode = True 替換為 from_attributes = True
        from_attributes = True