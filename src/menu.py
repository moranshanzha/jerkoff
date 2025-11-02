#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
游戏菜单模块
负责处理游戏的开始界面和得分历史界面
"""
import pygame
from config.settings import *
from src.score import ScoreSystem


class StartMenu:
    """开始菜单类"""
    
    def __init__(self, screen, score_system):
        self.screen = screen
        self.score_system = score_system
        self.width, self.height = screen.get_size()
        
        # 加载背景图片
        self.background = pygame.image.load(os.path.join(BASE_DIR, "material/image/background.png"))
        
        # 加载标题图片
        self.title_font = pygame.font.Font(None, 72)
        self.title_text = self.title_font.render("飞机大战", True, (255, 0, 0))
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 150))
        
        # 加载按钮图片
        self.start_button_normal = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_resume_nor.png"))
        self.start_button_pressed = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_resume_pressed.png"))
        self.quit_button_normal = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_pause_nor.png"))
        self.quit_button_pressed = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_pause_pressed.png"))
        self.score_button_normal = pygame.image.load(os.path.join(BASE_DIR, "material/image/btn_finish.png"))
        self.score_button_pressed = pygame.image.load(os.path.join(BASE_DIR, "material/image/btn_finish.png"))  # 暂时用同一个图片
        
        # 设置按钮位置
        self.start_button_rect = self.start_button_normal.get_rect(center=(self.width // 2, 350))
        self.quit_button_rect = self.quit_button_normal.get_rect(center=(self.width // 2, 450))
        self.score_button_rect = self.score_button_normal.get_rect(center=(self.width // 2, 550))
        
        # 加载最高分
        self.high_score = self.score_system.high_score
        self.high_score_font = pygame.font.Font(None, 36)
        self.high_score_text = self.high_score_font.render(f"历史最高分: {self.high_score}", True, (255, 255, 255))
        self.high_score_rect = self.high_score_text.get_rect(center=(self.width // 2, 250))
        
        # 当前选中的按钮
        self.selected_button = None
    
    def draw(self):
        """绘制开始菜单"""
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        # 绘制标题
        self.screen.blit(self.title_text, self.title_rect)
        
        # 绘制最高分
        self.screen.blit(self.high_score_text, self.high_score_rect)
        
        # 绘制按钮
        if self.selected_button == "start":
            self.screen.blit(self.start_button_pressed, self.start_button_rect)
        else:
            self.screen.blit(self.start_button_normal, self.start_button_rect)
            
        if self.selected_button == "quit":
            self.screen.blit(self.quit_button_pressed, self.quit_button_rect)
        else:
            self.screen.blit(self.quit_button_normal, self.quit_button_rect)
            
        if self.selected_button == "score":
            self.screen.blit(self.score_button_pressed, self.score_button_rect)
        else:
            self.screen.blit(self.score_button_normal, self.score_button_rect)
    
    def handle_event(self, event):
        """处理菜单事件"""
        if event.type == pygame.MOUSEMOTION:
            # 鼠标移动事件
            if self.start_button_rect.collidepoint(event.pos):
                self.selected_button = "start"
            elif self.quit_button_rect.collidepoint(event.pos):
                self.selected_button = "quit"
            elif self.score_button_rect.collidepoint(event.pos):
                self.selected_button = "score"
            else:
                self.selected_button = None
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 鼠标点击事件
            if event.button == 1:  # 左键点击
                if self.start_button_rect.collidepoint(event.pos):
                    button_down_sound.play()
                    return "start"
                elif self.quit_button_rect.collidepoint(event.pos):
                    button_down_sound.play()
                    return "quit"
                elif self.score_button_rect.collidepoint(event.pos):
                    button_down_sound.play()
                    return "score_history"
        
        elif event.type == pygame.KEYDOWN:
            # 键盘事件
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if self.selected_button == "start":
                    self.selected_button = "score"
                elif self.selected_button == "quit":
                    self.selected_button = "start"
                elif self.selected_button == "score":
                    self.selected_button = "quit"
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if self.selected_button == "start":
                    self.selected_button = "quit"
                elif self.selected_button == "quit":
                    self.selected_button = "score"
                elif self.selected_button == "score":
                    self.selected_button = "start"
            elif event.key == pygame.K_RETURN:
                if self.selected_button == "start":
                    button_down_sound.play()
                    return "start"
                elif self.selected_button == "quit":
                    button_down_sound.play()
                    return "quit"
                elif self.selected_button == "score":
                    button_down_sound.play()
                    return "score_history"
        
        return None


class ScoreHistoryScreen:
    """得分历史记录屏幕类"""
    
    def __init__(self, screen, score_system):
        self.screen = screen
        self.score_system = score_system
        self.width, self.height = screen.get_size()
        
        # 加载背景图片
        self.background = pygame.image.load(os.path.join(BASE_DIR, "material/image/background.png"))
        
        # 标题
        self.title_font = pygame.font.Font(None, 60)
        self.title_text = self.title_font.render("得分历史", True, (255, 0, 0))
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 100))
        
        # 返回按钮
        self.back_button_normal = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_pause_nor.png"))
        self.back_button_pressed = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_pause_pressed.png"))
        self.back_button_rect = self.back_button_normal.get_rect(topleft=(20, 20))
        
        # 得分列表
        self.scores = self.score_system.get_top_scores(10)
        self.score_font = pygame.font.Font(None, 36)
        
        # 当前选中的按钮
        self.selected_button = None
    
    def update_scores(self):
        """更新得分列表"""
        self.scores = self.score_system.get_top_scores(10)
    
    def draw(self):
        """绘制得分历史记录屏幕"""
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        # 绘制标题
        self.screen.blit(self.title_text, self.title_rect)
        
        # 绘制返回按钮
        if self.selected_button == "back":
            self.screen.blit(self.back_button_pressed, self.back_button_rect)
        else:
            self.screen.blit(self.back_button_normal, self.back_button_rect)
        
        # 绘制得分列表
        y_offset = 200
        for i, score in enumerate(self.scores):
            if i >= 10:  # 最多显示10条记录
                break
                
            score_text = self.score_font.render(f"{i+1}. {score['playerName']}: {score['score']}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(score_text, score_rect)
            y_offset += 50
            
        # 如果没有得分记录
        if not self.scores:
            no_scores_text = self.score_font.render("暂无得分记录", True, (255, 255, 255))
            no_scores_rect = no_scores_text.get_rect(center=(self.width // 2, 300))
            self.screen.blit(no_scores_text, no_scores_rect)
    
    def handle_event(self, event):
        """处理得分历史屏幕事件"""
        if event.type == pygame.MOUSEMOTION:
            # 鼠标移动事件
            if self.back_button_rect.collidepoint(event.pos):
                self.selected_button = "back"
            else:
                self.selected_button = None
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 鼠标点击事件
            if event.button == 1:  # 左键点击
                if self.back_button_rect.collidepoint(event.pos):
                    button_down_sound.play()
                    return "back"
        
        elif event.type == pygame.KEYDOWN:
            # 键盘事件
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                button_down_sound.play()
                return "back"
            elif event.key == pygame.K_RETURN and self.selected_button == "back":
                button_down_sound.play()
                return "back"
        
        return None
