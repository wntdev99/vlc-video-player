# vlc-video-player

Python + python-vlc 기반의 CLI 비디오 플레이어.
전체화면, 화면 채우기(stretch/crop), 디인터레이싱을 지원한다.

## 요구사항

```bash
sudo apt install vlc
pip install python-vlc
```

## 사용법

```bash
python player.py <video>  [옵션...]
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--fullscreen` | 전체화면 재생 | 활성 |
| `--no-fullscreen` | 창 모드 재생 | — |
| `--fill stretch` | 화면 비율에 맞게 영상을 늘려 채움 (비율 왜곡) | — |
| `--fill crop` | 가장자리를 잘라 화면을 채움 (왜곡 없음) | — |
| `--deinterlace <mode>` | 디인터레이싱 모드 지정 | — |

### `--deinterlace` 모드

| 모드 | 특징 |
|------|------|
| `yadif2x` | 최고 품질, CPU 부하 높음 |
| `yadif` | 품질/성능 균형 |
| `linear` | 경량, 낮은 부하 |
| `blend` | 부드러운 블렌딩 |
| `bob` | 필드 분리 |
| `discard` | 한 필드 제거 |
| `mean` | 필드 평균 |
| `x` | 적응형 |

## 예시

```bash
# 기본 전체화면 재생
python player.py video.mp4

# 화면 꽉 채우기 (비율 유지, 가장자리 잘림)
python player.py video.mp4 --fill crop

# 화면 꽉 채우기 (비율 왜곡, 잘림 없음)
python player.py video.mp4 --fill stretch

# 고품질 디인터레이싱
python player.py video.mp4 --deinterlace yadif2x

# 조합 사용
python player.py video.mp4 --fill crop --deinterlace yadif2x

# 창 모드
python player.py video.mp4 --no-fullscreen
```

## 재생 중 출력

```
========================================
  영상 정보
========================================
  파일        : video.mp4
  전체화면    : True
  길이(초)    : 120.5
  길이(포맷)  : 02:00
  화면 채우기 : crop
  디인터레이스: yadif2x
========================================
재생 시작... (Ctrl+C 로 중단)

[ playing] 00:12 / 02:00  ( 10.0%)
```

`Ctrl+C` 로 중단할 수 있다.
