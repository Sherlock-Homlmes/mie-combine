# GitHub Actions Deployment Guide

## Cấu hình Secrets cho GitHub Actions

Để GitHub Actions có thể deploy tự động lên VPS, bạn cần thêm các secrets sau vào repository:

1. Vào repository trên GitHub
2. Settings → Secrets and variables → Actions
3. Nhấn "New repository secret" và thêm các secrets sau:

### Bắt buộc:

- `VPS_HOST`: IP address của VPS
- `VPS_USERNAME`: Username để SSH vào VPS
- `VPS_SSH_KEY`: Private key SSH (nội dung file id_rsa)
- `PROJECT_PATH`: Đường dẫn đến project trên VPS (ví dụ: /home/user/mie-combine)

### Tùy chọn:

- `VPS_PORT`: Port SSH (mặc định là 22)

## Cách lấy SSH Key

1. Tạo SSH key pair trên local:

```bash
ssh-keygen -t rsa -b 4096 -C "github-actions"
```

2. Thêm public key vào VPS:

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub user@your-vps-ip
```

3. Hiển thị private key để thêm vào GitHub secrets:

```bash
cat ~/.ssh/id_rsa
```

Sao chép toàn bộ nội dung (bao gồm cả -----BEGIN/END-----) và thêm vào secret `VPS_SSH_KEY`.

## Cách hoạt động

Khi bạn push code lên branch `main`:

1. GitHub Actions sẽ tự động trigger
2. SSH vào VPS của bạn
3. Pull code mới nhất
4. Chạy script `deploy-swarm.sh`
5. Kiểm tra trạng thái service

## Kiểm tra deployment

1. Vào tab Actions trên GitHub repository
2. Xem log của workflow để kiểm tra kết quả
3. Nếu có lỗi, log sẽ hiển thị chi tiết để bạn debug

## Lưu ý

- Đảm bảo VPS của bạn đã cài Docker và đang chạy Docker Swarm
- User SSH có quyền thực thi docker commands
- Đường dẫn `PROJECT_PATH` phải chính xác
