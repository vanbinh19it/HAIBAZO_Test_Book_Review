# Haibazo Book Review

Ứng dụng quản lý sách và đánh giá sách, xây dựng theo kiến trúc full-stack:
- Backend: `FastAPI` + `SQLModel` + `PostgreSQL`
- Frontend: `React` + `TypeScript` + `Vite`

## Kết quả:
### Frontend: https://haibazo-test-book-review-frontend.vercel.app/
### Backend: https://haibazo-test-book-review.onrender.com/
- **admin**: admin@example.com
- **password**: admin@123

## Tính năng đã triển khai

### 1) CRUD Author (`/api/v1/authors`)
- **Create**: tạo tác giả mới, tự động gán `owner_id` theo user đang đăng nhập.
- **Read list**: danh sách có phân trang (`page`, `page_size`) và trả thêm `books_count` cho từng tác giả.
- **Read detail**: xem chi tiết tác giả theo `id`.
- **Update**: cập nhật thông tin tác giả.
- **Delete**: xóa tác giả.
- **Validation**:
  - Tên tác giả được `trim()`, không cho phép rỗng.
  - Chặn trùng tên tác giả trong phạm vi owner (hoặc toàn bộ khi superuser thao tác).

### 2) CRUD Books (`/api/v1/books`)
- **Create**: tạo sách theo `author_id`.
- **Read list**: danh sách có phân trang, trả thêm `author_name`.
- **Read detail**: xem chi tiết sách theo `id`.
- **Update**: cập nhật `title`, `author_id`.
- **Delete**: xóa sách.
- **Validation & ràng buộc dữ liệu**:
  - `title` được `trim()`, không cho phép rỗng.
  - Bắt buộc `author` tồn tại.
  - Không cho phép trùng sách cùng `title + author_id` trong phạm vi owner.
  - Đồng bộ owner của book theo owner của author cha.

### 3) CRUD Reviews (`/api/v1/reviews`)
- **Create**: tạo review cho một quyển sách (`book_id`).
- **Read list**: danh sách có phân trang, trả thêm `book_title`, `author_name`.
- **Read detail**: xem chi tiết review theo `id`.
- **Update**: cập nhật nội dung review hoặc chuyển sang book khác.
- **Delete**: xóa review.
- **Validation & ràng buộc dữ liệu**:
  - `content` được `trim()`, không cho phép rỗng.
  - Bắt buộc `book` tồn tại.
  - Đồng bộ owner của review theo owner của book cha.

## Authentication

- Đăng nhập bằng endpoint `POST /api/v1/login/access-token`.
- Sử dụng chuẩn OAuth2 Password Flow, trả về `Bearer JWT access token`.
- Có endpoint `POST /api/v1/login/test-token` để kiểm tra token hiện tại.
- Hỗ trợ quên mật khẩu:
  - `POST /api/v1/password-recovery/{email}`
  - `POST /api/v1/reset-password/`
- Mật khẩu được hash an toàn ở backend.

## Phân quyền (Authorization)

- Hệ thống dùng mô hình **owner-based access control** kết hợp **superuser**:
  - **User thường**:
    - Chỉ thấy dữ liệu do chính mình tạo (`owner_id == current_user.id`).
    - Chỉ được xem/sửa/xóa Author, Book, Review thuộc sở hữu của mình.
  - **Superuser**:
    - Xem và thao tác được toàn bộ dữ liệu.
- Nếu không đủ quyền, API trả về `403 Not enough permissions`.

## Ghi chú thêm

- Danh sách Authors/Books/Reviews đều có phân trang thống nhất.
- Các thao tác CRUD chính đã có test API tương ứng trong backend.
