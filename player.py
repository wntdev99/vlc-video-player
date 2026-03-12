"""
Ubuntu Python 비디오 플레이어 (python-vlc 기반)

설치:
    sudo apt install vlc
    sudo apt install python3-vlc

사용법:
    python player.py video.mp4
    python player.py video.mp4 --fullscreen
    python player.py video.mp4 --no-fullscreen
    python player.py video.mp4 --fill stretch
    python player.py video.mp4 --fill crop
    python player.py video.mp4 --deinterlace yadif2x
"""

import sys
import time
import argparse
import vlc


class VideoPlayer:
    def __init__(self, filepath: str, fullscreen: bool = True, fill_mode: str = None, deinterlace: str = None):
        self.filepath = filepath
        self.fullscreen = fullscreen
        self.fill_mode = fill_mode      # None | "stretch" | "crop"
        self.deinterlace = deinterlace  # None | "blend" | "bob" | "discard" | "linear" | "mean" | "x" | "yadif" | "yadif2x"

        self.instance = vlc.Instance()
        self.media = self.instance.media_new(filepath)
        self.media.parse()  # 메타데이터 파싱 (duration 등)

        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)
        self.player.set_fullscreen(fullscreen)

    # ── 화면 채우기 ───────────────────────────────────────────────

    @staticmethod
    def _get_screen_size() -> tuple:
        """xrandr로 스크린 해상도 감지"""
        import subprocess, re
        result = subprocess.run(["xrandr"], capture_output=True, text=True)
        m = re.search(r"current (\d+) x (\d+)", result.stdout)
        if m:
            return int(m.group(1)), int(m.group(2))
        raise RuntimeError("화면 해상도를 감지할 수 없습니다. xrandr 출력을 확인하세요.")

    def _apply_fill(self):
        if not self.fill_mode:
            return
        w, h = self._get_screen_size()
        ratio = f"{w}:{h}"
        if self.fill_mode == "stretch":
            self.player.video_set_aspect_ratio(ratio)
        elif self.fill_mode == "crop":
            self.player.video_set_crop_geometry(ratio)

    def _apply_deinterlace(self):
        if self.deinterlace:
            self.player.video_set_deinterlace(self.deinterlace)

    # ── 영상 정보 ─────────────────────────────────────────────────

    def get_info(self) -> dict:
        duration_ms = self.media.get_duration()  # 밀리초
        duration_sec = duration_ms / 1000 if duration_ms > 0 else None

        return {
            "파일": self.filepath,
            "전체화면": self.fullscreen,
            "길이(초)": round(duration_sec, 2) if duration_sec else "알 수 없음",
            "길이(포맷)": self._fmt_duration(duration_sec) if duration_sec else "알 수 없음",
        }

    @staticmethod
    def _fmt_duration(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    # ── 재생 상태 ─────────────────────────────────────────────────

    def get_state(self) -> str:
        """
        반환값:
            'idle'     - 재생 전
            'playing'  - 재생 중
            'paused'   - 일시정지
            'ended'    - 재생 완료
            'error'    - 오류
        """
        state = self.player.get_state()
        mapping = {
            vlc.State.NothingSpecial: "idle",
            vlc.State.Opening:        "opening",
            vlc.State.Buffering:      "buffering",
            vlc.State.Playing:        "playing",
            vlc.State.Paused:         "paused",
            vlc.State.Stopped:        "ended",
            vlc.State.Ended:          "ended",
            vlc.State.Error:          "error",
        }
        return mapping.get(state, "unknown")

    def get_position(self) -> dict:
        """현재 재생 위치 반환"""
        pos_ratio = self.player.get_position()  # 0.0 ~ 1.0
        time_ms = self.player.get_time()         # 밀리초
        time_sec = time_ms / 1000 if time_ms >= 0 else 0
        return {
            "위치(초)": round(time_sec, 2),
            "위치(포맷)": self._fmt_duration(time_sec),
            "진행률(%)": round(pos_ratio * 100, 1) if pos_ratio >= 0 else 0,
        }

    def is_playing(self) -> bool:
        return self.player.is_playing() == 1

    def is_ended(self) -> bool:
        return self.get_state() in ("ended", "error")

    # ── 제어 ──────────────────────────────────────────────────────

    def play(self):
        self.player.play()
        time.sleep(0.3)  # VLC 렌더러 초기화 대기
        self._apply_fill()
        self._apply_deinterlace()

    def pause(self):
        self.player.pause()  # 토글 (재생 ↔ 일시정지)

    def stop(self):
        self.player.stop()

    def release(self):
        self.player.release()
        self.instance.release()

    # ── 블로킹 재생 ───────────────────────────────────────────────

    def play_and_wait(self, poll_interval: float = 0.5):
        """재생을 시작하고 끝날 때까지 상태를 출력하며 대기"""
        self.play()

        # VLC가 미디어를 열기까지 잠시 대기
        time.sleep(0.5)

        try:
            while not self.is_ended():
                pos = self.get_position()
                print(
                    f"\r[{self.get_state():8s}] "
                    f"{pos['위치(포맷)']} / "
                    f"{self.get_info()['길이(포맷)']}  "
                    f"({pos['진행률(%)']:5.1f}%)",
                    end="",
                    flush=True,
                )
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\n\n[사용자 중단]")
        finally:
            print()  # 줄 바꿈
            self.stop()
            self.release()


# ── CLI 진입점 ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Python VLC 비디오 플레이어")
    parser.add_argument("video", help="재생할 비디오 파일 경로")
    parser.add_argument(
        "--fullscreen",
        dest="fullscreen",
        action="store_true",
        default=True,
        help="전체화면으로 재생 (기본값)",
    )
    parser.add_argument(
        "--no-fullscreen",
        dest="fullscreen",
        action="store_false",
        help="창 모드로 재생",
    )
    parser.add_argument(
        "--fill",
        dest="fill",
        choices=["stretch", "crop"],
        default=None,
        help="화면 채우기 방식: stretch(늘림) 또는 crop(잘라서 채움)",
    )
    parser.add_argument(
        "--deinterlace",
        dest="deinterlace",
        choices=["blend", "bob", "discard", "linear", "mean", "x", "yadif", "yadif2x"],
        default=None,
        help="디인터레이싱 모드 (고품질: yadif2x, 경량: linear)",
    )
    args = parser.parse_args()

    player = VideoPlayer(args.video, fullscreen=args.fullscreen, fill_mode=args.fill, deinterlace=args.deinterlace)

    # 영상 기본 정보 출력
    info = player.get_info()
    print("=" * 40)
    print("  영상 정보")
    print("=" * 40)
    for k, v in info.items():
        print(f"  {k:12s}: {v}")
    if args.fill:
        print(f"  {'화면 채우기':12s}: {args.fill}")
    if args.deinterlace:
        print(f"  {'디인터레이스':12s}: {args.deinterlace}")
    print("=" * 40)
    print("재생 시작... (Ctrl+C 로 중단)\n")

    player.play_and_wait()

    print(f"\n최종 상태: {player.get_state()}")


if __name__ == "__main__":
    main()
