# -*- coding: utf-8 -*-
import pygame
import sys
import os
import math


# 初期化
pygame.init()

# 画面設定
'''info = pygame.display.Info() 
SCREEN_WIDTH =  info.current_w #800
SCREEN_HEIGHT = info.current_h #600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("スターウォーズ風スクロール（最適化版）")
'''
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("スターウォーズ風スクロール（最適化版）")

# 色設定
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 150, 255)

# 日本語フォントの読み込み
def get_japanese_font():
    try:
        if os.name == 'nt':
            font_paths = [
                "C:/Windows/Fonts/msgothic.ttc",
                "C:/Windows/Fonts/meiryo.ttc",
                "C:/Windows/Fonts/NotoSansCJK-Regular.ttc"
            ]
        elif sys.platform == 'darwin':
            font_paths = [
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/System/Library/Fonts/AppleGothic.ttf"
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
            ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        return None
    except:
        return None

# フォント設定
japanese_font_path = get_japanese_font()

if japanese_font_path:
    print(f"日本語フォントを使用: {japanese_font_path}")
    font_title = pygame.font.Font(japanese_font_path, 36)
    font_large = pygame.font.Font(japanese_font_path, 28)
    font_small = pygame.font.Font(japanese_font_path, 22)
else:
    print("システムフォントを使用")
    font_title = pygame.font.SysFont('notosanscjk,hiragino sans gb,msgothic,meiryo', 36)
    font_large = pygame.font.SysFont('notosanscjk,hiragino sans gb,msgothic,meiryo', 28)
    font_small = pygame.font.SysFont('notosanscjk,hiragino sans gb,msgothic,meiryo', 22)

# テキスト
with open("story.txt", "r", encoding="utf-8") as f:
    story_text = f.read()

def simple_transform(surface, perspective_factor=0.3):
    """軽量な台形変形＋サイズ変更（Pygameの標準機能のみ使用）"""
    try:
        width, height = surface.get_size()
        
        # 台形変形のポイントを計算
        # 上部を狭く、下部を広く
        top_inset = int(width * perspective_factor)
        
        # サイズ変更の計算
        # 下部（y=height）で最大2倍、上部（y=0）で最小0.5倍
        max_scale = 4.0
        min_scale = 0.1
        
        # 新しいサーフェスを作成（大きめに）
        max_width = int(width * max_scale)
        transformed = pygame.Surface((max_width, height), pygame.SRCALPHA)
        transformed.fill((0, 0, 0, 0))
        
        # 行ごとに変形（軽量化のため間引き）
        step = max(1, height // 100)  # 最大100行で処理
        
        for y in range(0, height, step):
            # Y位置による変形率を計算
            ratio = y / height  # 0（上）から1（下）
            
            # 台形変形
            current_inset = int(top_inset * (1 - ratio))
            
            # サイズスケール（下で大きく、上で小さく）
            scale = min_scale + (max_scale - min_scale) * ratio
            
            try:
                # 元の行を取得
                if current_inset > 0:
                    source_rect = pygame.Rect(current_inset, y, width - 2*current_inset, step)
                else:
                    source_rect = pygame.Rect(0, y, width, step)
                
                if source_rect.width > 0 and source_rect.height > 0:
                    line_surface = surface.subsurface(source_rect)
                    
                    # 幅のスケーリング
                    scaled_width = int(width * scale)
                    scaled_height = step
                    
                    if scaled_width > 0 and scaled_height > 0:
                        scaled_line = pygame.transform.scale(line_surface, (scaled_width, scaled_height))
                        
                        # 中央に配置
                        x_offset = (max_width - scaled_width) // 2
                        transformed.blit(scaled_line, (x_offset, y))
            except Exception as e:
                # エラーの場合はそのまま描画
                try:
                    transformed.blit(surface, ((max_width - width) // 2, 0), pygame.Rect(0, y, width, step))
                except:
                    pass
        
        # 最終的に元のサイズに合わせて中央部分を取得
        final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        final_surface.fill((0, 0, 0, 0))
        
        # 中央部分をクロップ
        crop_x = (max_width - width) // 2
        if crop_x >= 0:
            final_surface.blit(transformed, (0, 0), pygame.Rect(crop_x, 0, width, height))
        else:
            # スケールダウンが必要な場合
            scaled_transformed = pygame.transform.scale(transformed, (width, height))
            final_surface.blit(scaled_transformed, (0, 0))
        
        return final_surface
    except Exception as e:
        print(f"変形エラー: {e}")
        return surface

def create_fade_mask():
    """グラデーションマスクを作成（最適化版）"""
    mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # 上部と下部のフェードゾーン
    fade_top = SCREEN_HEIGHT // 4
    fade_bottom = SCREEN_HEIGHT * 3 // 4
    
    for y in range(SCREEN_HEIGHT):
        if y < fade_top:
            # 上部フェード
            alpha = int(255 * (y / fade_top))
        elif y > fade_bottom:
            # 下部フェード
            alpha = int(255 * ((SCREEN_HEIGHT - y) / (SCREEN_HEIGHT - fade_bottom)))
        else:
            # 中央部分
            alpha = 255
        
        color = (alpha, alpha, alpha)
        pygame.draw.line(mask, color, (0, y), (SCREEN_WIDTH - 1, y))
    
    return mask

class StarWarsScroll:
    def __init__(self):
        self.scroll_position = 0
        self.scroll_speed = 2.0
        self.line_height = 35
        
        # テキストを行に分割
        self.lines = story_text.split('\n')
        
        # テキスト全体の高さを計算
        self.total_height = len(self.lines) * self.line_height
        
        # フェードマスクを事前作成
        self.fade_mask = create_fade_mask()
        
        # テキストサーフェスを作成
        self.create_text_surface()
        
    def create_text_surface(self):
        """全テキストを1つのサーフェスに描画"""
        text_width = SCREEN_WIDTH
        text_height = self.total_height + SCREEN_HEIGHT * 2
        
        self.text_surface = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
        self.text_surface.fill((0, 0, 0, 0))
        
        current_y = SCREEN_HEIGHT  # 画面の高さ分下から開始
        
        for line in self.lines:
            if line.strip():
                # フォントと色を選択
                if "EPISODE" in line:
                    font = font_title
                    color = BLUE
                elif "遥か彼方の銀河系で" in line:
                    font = font_large
                    color = BLUE
                else:
                    font = font_small
                    color = YELLOW
                
                # テキストをレンダリング
                text_render = font.render(line.strip(), True, color)
                
                # 中央に配置
                text_rect = text_render.get_rect()
                text_rect.centerx = text_width // 2
                text_rect.y = current_y
                
                self.text_surface.blit(text_render, text_rect)
            
            current_y += self.line_height
    
    def update(self):
        self.scroll_position += self.scroll_speed
        
        # テキストが全て画面外に出たらリセット
        if self.scroll_position > self.total_height + SCREEN_HEIGHT:
            self.scroll_position = 0
    
    def draw(self):
        # 現在の表示エリアを計算
        crop_y = int(self.scroll_position)
        
        # 安全な範囲でクロップ
        if crop_y >= 0 and crop_y + SCREEN_HEIGHT <= self.text_surface.get_height():
            try:
                cropped = self.text_surface.subsurface((0, crop_y, SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # 軽量な台形変形＋サイズ変更を適用
                warped_surface = simple_transform(cropped.copy(), 0.2)
                
                # フェードマスクを適用（blend_multiply使用）
                warped_surface.blit(self.fade_mask, (0, 0), special_flags=pygame.BLEND_MULT)
                
                # 最終描画
                screen.blit(warped_surface, (0, 0))
                
            except Exception as e:
                print(f"描画エラー: {e}")
                # エラー時は変形なしで描画
                try:
                    cropped = self.text_surface.subsurface((0, crop_y, SCREEN_WIDTH, SCREEN_HEIGHT))
                    screen.blit(cropped, (0, 0))
                except:
                    pass
        else:
            # 範囲外の場合は空画面
            screen.fill(BLACK)

def draw_stars():
    """背景の星を描画（最適化版）"""
    import random
    random.seed(42)
    
    # 星の数を減らして軽量化
    for i in range(50):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        brightness = random.randint(100, 255)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (x, y), 1)

def main():
    clock = pygame.time.Clock()
    scroller = StarWarsScroll()
    
    print("操作方法:")
    print("スペースキー: リセット")
    print("↑↓キー: 速度調整")
    print("ESC: 終了")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    scroller.scroll_position = 0
                elif event.key == pygame.K_UP:
                    scroller.scroll_speed = min(4.0, scroller.scroll_speed + 0.3)
                    print(f"速度: {scroller.scroll_speed:.1f}")
                elif event.key == pygame.K_DOWN:
                    scroller.scroll_speed = max(0.3, scroller.scroll_speed - 0.3)
                    print(f"速度: {scroller.scroll_speed:.1f}")
        
        # 更新
        scroller.update()
        
        # 描画
        screen.fill(BLACK)
        draw_stars()
        scroller.draw()
        
        # 操作説明
        help_text = font_small.render("SPACE: Reset, UP/DOWN: Speed, ESC: Exit", True, (100, 100, 100))
        screen.blit(help_text, (10, SCREEN_HEIGHT - 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()