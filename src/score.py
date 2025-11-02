#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
得分记录模块
负责游戏得分的计算和记录
"""
import json
import os
import requests
from config.settings import BASE_DIR


class ScoreSystem:
    """得分系统类，负责得分计算和记录"""
    
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.api_url = "http://localhost:8080/api/scores"  # SpringBoot后端API地址
        self.score_multiplier = 1
    
    def add_score(self, enemy_type):
        """根据敌机类型添加得分"""
        base_score = 0
        if enemy_type == "small":
            base_score = 10
        elif enemy_type == "mid":
            base_score = 50
        elif enemy_type == "big":
            base_score = 100
            
        # 应用得分加倍效果
        self.score += base_score * self.score_multiplier
        
        # 更新最高分
        if self.score > self.high_score:
            self.high_score = self.score
    
    def reset_score(self):
        """重置得分"""
        self.score = 0
    
    def save_score(self, player_name="player"):
        """保存得分到服务器"""
        try:
            score_data = {
                "playerName": player_name,
                "score": self.score,
                "gameTime": ""
            }
            
            response = requests.post(self.api_url, json=score_data)
            if response.status_code == 201:
                print("得分保存成功")
            else:
                print(f"得分保存失败: {response.status_code}")
                # 如果服务器不可用，保存到本地
                self.save_local_score(player_name)
        except requests.exceptions.ConnectionError:
            print("无法连接到服务器，保存到本地")
            self.save_local_score(player_name)
    
    def save_local_score(self, player_name="player"):
        """保存得分到本地文件"""
        score_file = os.path.join(BASE_DIR, "scores.json")
        
        try:
            if os.path.exists(score_file):
                with open(score_file, "r") as f:
                    scores = json.load(f)
            else:
                scores = []
                
            # 添加新得分
            scores.append({
                "playerName": player_name,
                "score": self.score,
                "gameTime": ""
            })
            
            # 按得分降序排序
            scores.sort(key=lambda x: x["score"], reverse=True)
            
            with open(score_file, "w") as f:
                json.dump(scores, f, indent=4)
                
        except Exception as e:
            print(f"保存本地得分失败: {e}")
    
    def load_high_score(self):
        """加载本地最高分"""
        score_file = os.path.join(BASE_DIR, "scores.json")
        
        try:
            if os.path.exists(score_file):
                with open(score_file, "r") as f:
                    scores = json.load(f)
                    if scores:
                        return scores[0]["score"]
        except Exception as e:
            print(f"加载最高分失败: {e}")
            
        return 0
    
    def get_top_scores(self, count=10):
        """获取本地排行榜前N名"""
        score_file = os.path.join(BASE_DIR, "scores.json")
        
        try:
            if os.path.exists(score_file):
                with open(score_file, "r") as f:
                    scores = json.load(f)
                    return scores[:count]
        except Exception as e:
            print(f"加载排行榜失败: {e}")
            
        return []
    
    def close(self):
        """关闭得分系统"""
        pass
