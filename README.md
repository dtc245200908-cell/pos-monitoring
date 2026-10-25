# Hệ thống Quản lý Chung cư / Căn hộ

**Python | Ubuntu | Prometheus | Grafana | Node Exporter**

## Giới thiệu dự án

Hệ thống quản lý Chung cư / Căn hộ bằng Python, kết hợp giám sát
ứng dụng và tài nguyên Ubuntu bằng Prometheus, Grafana và Node Exporter.

## Truy cập nhanh

| Dịch vụ | Đường dẫn |
|---|---|
| Ứng dụng POS | http://localhost:5001 |
| Prometheus | http://localhost:9090 |
| Prometheus Targets | http://localhost:9090/targets |
| Grafana | http://localhost:3001 |
| POS Metrics | http://localhost:5001/metrics |
| Node Exporter | http://localhost:9100/metrics |

**Lưu ý:** localhost chỉ truy cập được trong môi trường
đang chạy dịch vụ, không phải website công khai.

## Kiến trúc giám sát

POS Python (5001) → Prometheus (9090) → Grafana (3001)

Node Exporter (9100) → Prometheus (9090)

## Kết quả thực hiện

| Thành phần | Kết quả kiểm tra gần nhất |
|---|---|
| Ứng dụng POS | Hoạt động |
| Prometheus | Hoạt động |
| Job pos_app | UP |
| Grafana | Hoạt động |
| Node Exporter | Hoạt động |
| Dashboard Grafana | Đã thiết lập 7 biểu đồ |
| Cảnh báo Grafana | Đã thử nghiệm |

## Khởi động ứng dụng

Mở Ubuntu và thực hiện:

1. `cd ~/pos-monitoring`
2. `source venv/bin/activate`
3. `python app.py`
4. 'docker compose ps "

Nếu cổng 5001 đã được sử dụng và POS vẫn trả HTTP 200,
không cần khởi động thêm một tiến trình khác.

## Kiểm tra dịch vụ

- `systemctl is-active prometheus`
- `systemctl is-active grafana-server`
- `systemctl is-active prometheus-node-exporter`

## Cấu hình Prometheus

- Job: `pos_app`
- Target: `localhost:5001`
- Endpoint: `/metrics`
- Scrape interval: `5s`

## Dashboard Grafana

Dự án đã thiết lập 7 biểu đồ giám sát.
Truy cập http://localhost:3001 để xem dashboard.

## Minh chứng dự án

- Giao diện ứng dụng POS
- Prometheus Targets hiển thị UP
- Dashboard Grafana với 7 biểu đồ
- Cảnh báo Grafana
- Kết quả giám sát Node Exporter

Ảnh minh chứng sẽ được bổ sung khi có file ảnh thực tế.

## Mã nguồn GitHub

https://github.com/dtc245200908-cell/pos-monitoring
