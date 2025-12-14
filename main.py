# main.py
from fastapi import FastAPI, HTTPException, Query, status
from typing import List
import database
from models import BookCreate, BookResponse

app = FastAPI(title="AI Books API Exam", version="1.0.0")

# --- 根端點 ---
@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
def read_root():
    """
    根路徑，回傳歡迎訊息。
    """
    return {"message": "AI Books API"}

# --- GET /books：分頁取得書籍 ---
@app.get(
    "/books",
    response_model=List[BookResponse],
    tags=["Books"],
    summary="分頁取得書籍列表"
)
def read_books(
    skip: int = Query(0, ge=0, description="跳過的書籍數量 (OFFSET)"),
    limit: int = Query(10, gt=0, le=100, description="限制取得的書籍數量 (LIMIT)")
):
    """
    根據 `skip` 和 `limit` 參數分頁取得書籍列表。
    """
    books = database.get_all_books(skip=skip, limit=limit)
    return books

# --- GET /books/{book_id}：取得單一書籍 ---
@app.get(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
    summary="取得單一書籍"
)
def read_book(book_id: int):
    """
    根據書籍 ID 取得單一書籍的詳細資料。
    """
    book = database.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    return book

# --- POST /books：新增一本書 ---
@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
    summary="新增一本書籍"
)
def create_book(book: BookCreate):
    """
    新增一本新書到資料庫。
    """
    # 將 Pydantic 模型轉換為字典，並只保留有值的欄位
    book_data = book.dict(exclude_unset=True)
    
    # 確保 title, author, price 是非空值，雖然 Pydantic 已經做了部分檢查
    if not book_data.get('title') or not book_data.get('author') or book_data.get('price') is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Title, Author, and Price are required fields."
        )

    new_id = database.create_book(book_data)
    
    # 新增成功後，重新從資料庫讀取完整的書籍資料並回傳
    new_book = database.get_book_by_id(new_id)
    if new_book is None:
         # 理想上不會發生，但作為防禦性程式設計
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve newly created book.")
        
    return new_book

# --- PUT /books/{book_id}：完整更新一本書 ---
@app.put(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
    summary="完整更新一本書籍"
)
def update_book(book_id: int, book: BookCreate):
    """
    根據 ID 完整更新一本書籍的所有欄位。
    """
    # 檢查書籍是否存在
    if database.get_book_by_id(book_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")

    # 由於是完整 PUT，我們需要將所有欄位（即使是 None）傳遞給資料庫
    # 但 SQLite 的 UPDATE 語法中，我們只傳遞 Pydantic 模型中**非 None**的值會更安全
    # 這裡選擇將 Pydantic 模型轉為字典，並只保留非 None 的值
    update_data = book.dict(exclude_unset=True)

    if not update_data:
        # 如果 body 為空，回傳 400 提示使用者提供資料
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Request body cannot be empty for an update."
        )

    # 進行更新
    success = database.update_book(book_id, update_data)

    if not success:
        # 如果 update_book 函式回傳 False，表示更新失敗 (例如 ID 不存在或資料庫錯誤)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update book due to internal error.")
    
    # 更新成功後，重新讀取並回傳最新的書籍資料
    updated_book = database.get_book_by_id(book_id)
    if updated_book is None:
        # 如果更新後無法取得，可能是 ID 誤刪等極端情況
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Updated book disappeared.")

    return updated_book

# --- DELETE /books/{book_id}：刪除一本書 ---
@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Books"],
    summary="刪除一本書籍"
)
def delete_book(book_id: int):
    """
    根據 ID 刪除一本書籍。成功刪除回傳 204 No Content。
    """
    if not database.delete_book(book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    
    # 成功刪除，FastAPI 會自動回傳 204 No Content (不含內容)
    return