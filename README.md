# vlc-video-player

Python + python-vlc 기반 CLI 비디오 플레이어.

## 요구사항

```bash
# VLC 및 python 바인딩
sudo apt install vlc
sudo apt install python3-vlc
```

## 설치

```bash
git clone https://github.com/wntdev99/vlc-video-player.git
cd vlc-video-player
```

## 사용법

```bash
python3 player.py <video> [옵션...]
```

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--fullscreen` | 전체화면 재생 | 기본 활성 |
| `--no-fullscreen` | 창 모드 재생 | — |
| `--fill stretch` | 영상을 늘려 화면 꽉 채움 (비율 왜곡) | — |
| `--fill crop` | 가장자리를 잘라 화면 꽉 채움 (왜곡 없음) | — |
| `--deinterlace <mode>` | 디인터레이싱 모드 지정 | — |

### `--fill` 비교

| 방식 | 비율 왜곡 | 화면 잘림 | 검은 여백 |
|------|:---------:|:---------:|:---------:|
| 미사용 | 없음 | 없음 | 있음 |
| `stretch` | 있음 | 없음 | 없음 |
| `crop` | 없음 | 있음 | 없음 |

### `--deinterlace` 모드

| 모드 | 설명 |
|------|------|
| `yadif2x` | 최고 품질, CPU 부하 높음 |
| `yadif` | 품질/성능 균형 |
| `linear` | 경량, 낮은 부하 |
| `blend` | 부드러운 블렌딩 |
| `bob` | 필드 분리 |
| `discard` | 한 필드 제거 |
| `mean` | 필드 평균 |
| `x` | 적응형 |

> 인터레이스 영상(방송 녹화 등)의 빗살 현상을 제거한다. 일반 MP4에는 불필요.

## 예시

```bash
# 기본 전체화면 재생
python3 player.py video.mp4

# 창 모드
python3 player.py video.mp4 --no-fullscreen

# 화면 꽉 채우기 — 잘림 허용, 왜곡 없음
python3 player.py video.mp4 --fill crop

# 화면 꽉 채우기 — 잘림 없음, 비율 왜곡
python3 player.py video.mp4 --fill stretch

# 고품질 디인터레이싱
python3 player.py video.mp4 --deinterlace yadif2x

# 조합
python3 player.py video.mp4 --fill crop --deinterlace yadif2x
```

## Docker 환경에서 실행

컨테이너 내부에서 실행 시 X11 디스플레이 접근 권한이 필요하다.

### 방법 1: xhost (간단)

**1. 호스트에서 root 접근 허용 (한 번만)**

```bash
xhost +local:root
```

**2. 컨테이너 내부에서 DISPLAY 설정 후 실행**

```bash
export DISPLAY=:0
python3 player.py video.mp4
```

### 방법 2: .Xauthority 복사

**1. 호스트에서 인증 파일 복사**

```bash
docker cp /home/james/.Xauthority ros1-main:/root/.Xauthority
```

**2. 컨테이너 내부에서 설정 후 실행**

```bash
export DISPLAY=:0
export XAUTHORITY=/root/.Xauthority
python3 player.py video.mp4
```

> 컨테이너 실행 시 `/tmp/.X11-unix:/tmp/.X11-unix` 가 마운트되어 있어야 한다.

## 실행 화면

```
========================================
  영상 정보
========================================
  파일          : video.mp4
  전체화면      : True
  길이(초)      : 120.5
  길이(포맷)    : 02:00
  화면 채우기   : crop
  디인터레이스  : yadif2x
========================================
재생 시작... (Ctrl+C 로 중단)

[ playing] 00:12 / 02:00  ( 10.0%)
```

`Ctrl+C` 로 언제든 중단할 수 있다.
