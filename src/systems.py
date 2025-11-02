#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
游戏系统模块
负责实现击杀画面系统、飞机皮肤调换界面和道具系统
"""
import pygame
import random
import os
from config.settings import BASE_DIR, button_down_sound, get_bullet_sound, get_bomb_sound, level_up_sound, bomb_sound


class KillEffectSystem:
    """击杀画面系统类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # 加载击杀特效资源
        self.effects = {
            'small': [
                pygame.image.load("material/image/enemy1_down1.png"),
                pygame.image.load("material/image/enemy1_down2.png"),
                pygame.image.load("material/image/enemy1_down3.png"),
                pygame.image.load("material/image/enemy1_down4.png")
            ],
            'mid': [
                pygame.image.load("material/image/enemy2_down1.png"),
                pygame.image.load("material/image/enemy2_down2.png"),
                pygame.image.load("material/image/enemy2_down3.png"),
                pygame.image.load("material/image/enemy2_down4.png")
            ],
            'big': [
                pygame.image.load("material/image/enemy3_down1.png"),
                pygame.image.load("material/image/enemy3_down2.png"),
                pygame.image.load("material/image/enemy3_down3.png"),
                pygame.image.load("material/image/enemy3_down4.png"),
                pygame.image.load("material/image/enemy3_down5.png"),
                pygame.image.load("material/image/enemy3_down6.png")
            ]
        }
        
        # 当前正在播放的特效
        self.active_effects = []
        
        # 击杀信息面板
        self.font = pygame.font.Font(None, 36)
        self.kill_messages = []
        
    def add_kill_effect(self, position, enemy_type):
        """添加击杀特效"""
        if enemy_type not in self.effects:
            enemy_type = 'small'
            
        effect = {
            'position': position,
            'type': enemy_type,
            'images': self.effects[enemy_type],
            'current_frame': 0,
            'frame_delay': 0,
            'active': True
        }
        
        self.active_effects.append(effect)
        
        # 添加击杀信息
        message = {
            'text': self.get_kill_message(enemy_type),
            'position': (position[0], position[1] - 30),
            'alpha': 255,
            'y_speed': -2,
            'active': True
        }
        
        self.kill_messages.append(message)
        
    def get_kill_message(self, enemy_type):
        """获取随机击杀消息"""
        messages = {
            'small': ['干得漂亮！', '完美击杀！', '太棒了！'],
            'mid': ['精彩绝伦！', '太厉害了！', '漂亮的一击！'],
            'big': ['史诗级击杀！', '太壮观了！', '难以置信！']
        }
        
        if enemy_type not in messages:
            enemy_type = 'small'
            
        return random.choice(messages[enemy_type])
        
    def update(self):
        """更新击杀特效和消息"""
        # 更新特效
        for effect in self.active_effects[:]:
            if not effect['active']:
                self.active_effects.remove(effect)
                continue
                
            effect['frame_delay'] += 1
            if effect['frame_delay'] >= 3:
                effect['current_frame'] += 1
                effect['frame_delay'] = 0
                
                if effect['current_frame'] >= len(effect['images']):
                    effect['active'] = False
        
        # 更新消息
        for message in self.kill_messages[:]:
            if not message['active']:
                self.kill_messages.remove(message)
                continue
                
            message['position'] = (message['position'][0], message['position'][1] + message['y_speed'])
            message['alpha'] -= 5
            
            if message['alpha'] <= 0:
                message['active'] = False
                
    def draw(self):
        """绘制击杀特效和消息"""
        # 绘制特效
        for effect in self.active_effects:
            if effect['active']:
                image = effect['images'][effect['current_frame']]
                rect = image.get_rect(center=effect['position'])
                self.screen.blit(image, rect)
        
        # 绘制消息
        for message in self.kill_messages:
            if message['active']:
                text_surface = self.font.render(message['text'], True, (255, 255, 255))
                text_surface.set_alpha(message['alpha'])
                rect = text_surface.get_rect(center=message['position'])
                self.screen.blit(text_surface, rect)


class SkinSystem:
    """飞机皮肤系统类"""
    
    def __init__(self, screen, our_plane):
        self.screen = screen
        self.our_plane = our_plane
        self.width, self.height = screen.get_size()
        
        # 加载皮肤资源
        # 使用现有图片作为所有皮肤的默认图片
        hero1 = pygame.image.load(os.path.join(BASE_DIR, "material/image/hero1.png"))
        hero2 = pygame.image.load(os.path.join(BASE_DIR, "material/image/hero2.png"))
        destroy_images = [
            pygame.image.load(os.path.join(BASE_DIR, "material/image/hero_blowup_n1.png")),
            pygame.image.load(os.path.join(BASE_DIR, "material/image/hero_blowup_n2.png")),
            pygame.image.load(os.path.join(BASE_DIR, "material/image/hero_blowup_n3.png")),
            pygame.image.load(os.path.join(BASE_DIR, "material/image/hero_blowup_n4.png")),
        ]
        
        self.skins = [
            {
                'name': '默认皮肤',
                'image_one': hero1,
                'image_two': hero2,
                'destroy_images': destroy_images,
                'unlocked': True,
                'price': 0
            },
            {
                'name': '红色皮肤',
                'image_one': hero1,
                'image_two': hero2,
                'destroy_images': destroy_images,
                'unlocked': False,
                'price': 1000
            },
            {
                'name': '蓝色皮肤',
                'image_one': hero1,
                'image_two': hero2,
                'destroy_images': destroy_images,
                'unlocked': False,
                'price': 2000
            }
        ]
        
        # 当前选中的皮肤索引
        self.current_skin_index = 0
        
        # 皮肤选择界面状态
        self.skin_menu_active = False
        
        # 界面元素
        self.title_font = pygame.font.Font(None, 60)
        self.text_font = pygame.font.Font(None, 36)
        
        # 按钮
        self.back_button_normal = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_pause_nor.png"))
        self.back_button_pressed = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_pause_pressed.png"))
        self.select_button_normal = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_resume_nor.png"))
        self.select_button_pressed = pygame.image.load(os.path.join(BASE_DIR, "material/image/game_resume_pressed.png"))
        
        self.back_button_rect = self.back_button_normal.get_rect(topleft=(20, 20))
        self.select_button_rect = self.select_button_normal.get_rect(bottomright=(self.width - 20, self.height - 20))
        
        # 皮肤预览区域
        self.preview_rect = pygame.Rect(self.width // 2 - 150, 150, 300, 300)
        
        # 皮肤列表区域
        self.list_rect = pygame.Rect(50, 150, 200, 500)
        
        # 当前选中的列表项
        self.selected_list_item = 0
        
    def update_skin(self):
        """更新飞机皮肤"""
        skin = self.skins[self.current_skin_index]
        self.our_plane.image_one = skin['image_one']
        self.our_plane.image_two = skin['image_two']
        self.our_plane.destroy_images = skin['destroy_images']
        self.our_plane.mask = pygame.mask.from_surface(self.our_plane.image_one)
        
    def toggle_skin_menu(self):
        """切换皮肤菜单的显示状态"""
        self.skin_menu_active = not self.skin_menu_active
        if not self.skin_menu_active:
            # 保存当前皮肤选择
            self.save_skin_selection()
            
    def save_skin_selection(self):
        """保存皮肤选择到本地"""
        import json
        import os
        
        skin_file = os.path.join(BASE_DIR, "skin_selection.json")
        
        try:
            with open(skin_file, "w") as f:
                json.dump({'current_skin': self.current_skin_index}, f)
        except Exception as e:
            print(f"保存皮肤选择失败: {e}")
            
    def load_skin_selection(self):
        """从本地加载皮肤选择"""
        import json
        import os
        
        skin_file = os.path.join(BASE_DIR, "skin_selection.json")
        
        try:
            if os.path.exists(skin_file):
                with open(skin_file, "r") as f:
                    data = json.load(f)
                    if 'current_skin' in data:
                        self.current_skin_index = data['current_skin']
                        self.update_skin()
        except Exception as e:
            print(f"加载皮肤选择失败: {e}")
            
    def handle_event(self, event):
        """处理皮肤菜单事件"""
        if event.type == pygame.MOUSEMOTION:
            # 鼠标移动事件
            if self.back_button_rect.collidepoint(event.pos):
                self.selected_button = "back"
            elif self.select_button_rect.collidepoint(event.pos):
                self.selected_button = "select"
            else:
                # 检查皮肤列表
                list_y = self.list_rect.y + 50
                for i, skin in enumerate(self.skins):
                    item_rect = pygame.Rect(self.list_rect.x + 10, list_y + i * 60, self.list_rect.width - 20, 50)
                    if item_rect.collidepoint(event.pos):
                        self.selected_list_item = i
                        break
                else:
                    self.selected_button = None
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 鼠标点击事件
            if event.button == 1:
                if self.back_button_rect.collidepoint(event.pos):
                    button_down_sound.play()
                    self.toggle_skin_menu()
                elif self.select_button_rect.collidepoint(event.pos):
                    button_down_sound.play()
                    self.current_skin_index = self.selected_list_item
                    self.update_skin()
                else:
                    # 检查皮肤列表
                    list_y = self.list_rect.y + 50
                    for i, skin in enumerate(self.skins):
                        item_rect = pygame.Rect(self.list_rect.x + 10, list_y + i * 60, self.list_rect.width - 20, 50)
                        if item_rect.collidepoint(event.pos):
                            self.selected_list_item = i
                            break
        
        elif event.type == pygame.KEYDOWN:
            # 键盘事件
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                self.toggle_skin_menu()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_list_item = (self.selected_list_item - 1) % len(self.skins)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_list_item = (self.selected_list_item + 1) % len(self.skins)
            elif event.key == pygame.K_RETURN:
                self.current_skin_index = self.selected_list_item
                self.update_skin()
        
    def draw(self):
        """绘制皮肤选择界面"""
        if not self.skin_menu_active:
            return
            
        # 绘制半透明背景
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = self.title_font.render("飞机皮肤", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # 绘制皮肤预览区域
        pygame.draw.rect(self.screen, (255, 255, 255), self.preview_rect, 2)
        skin = self.skins[self.selected_list_item]
        preview_image = skin['image_one']
        preview_image = pygame.transform.scale(preview_image, (200, 200))
        preview_rect = preview_image.get_rect(center=self.preview_rect.center)
        self.screen.blit(preview_image, preview_rect)
        
        # 绘制皮肤信息
        name_text = self.text_font.render(f"名称: {skin['name']}", True, (255, 255, 255))
        self.screen.blit(name_text, (self.preview_rect.x, self.preview_rect.y + self.preview_rect.height + 20))
        
        if skin['unlocked']:
            status_text = self.text_font.render("状态: 已解锁", True, (0, 255, 0))
        else:
            status_text = self.text_font.render(f"状态: 未解锁 (价格: {skin['price']})", True, (255, 255, 0))
        self.screen.blit(status_text, (self.preview_rect.x, self.preview_rect.y + self.preview_rect.height + 60))
        
        # 绘制皮肤列表
        pygame.draw.rect(self.screen, (255, 255, 255), self.list_rect, 2)
        list_title = self.text_font.render("可用皮肤", True, (255, 255, 255))
        self.screen.blit(list_title, (self.list_rect.x + 10, self.list_rect.y + 10))
        
        list_y = self.list_rect.y + 50
        for i, skin in enumerate(self.skins):
            item_rect = pygame.Rect(self.list_rect.x + 10, list_y + i * 60, self.list_rect.width - 20, 50)
            
            if i == self.selected_list_item:
                pygame.draw.rect(self.screen, (255, 0, 0), item_rect)
                
            if skin['unlocked']:
                color = (255, 255, 255)
            else:
                color = (100, 100, 100)
                
            skin_name = self.text_font.render(skin['name'], True, color)
            self.screen.blit(skin_name, (item_rect.x + 10, item_rect.y + 10))
            
        # 绘制按钮
        if self.selected_button == "back":
            self.screen.blit(self.back_button_pressed, self.back_button_rect)
        else:
            self.screen.blit(self.back_button_normal, self.back_button_rect)
            
        if self.selected_button == "select":
            self.screen.blit(self.select_button_pressed, self.select_button_rect)
        else:
            self.screen.blit(self.select_button_normal, self.select_button_rect)
            
        # 绘制按钮文字
        back_text = self.text_font.render("返回", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        select_text = self.text_font.render("选择", True, (255, 255, 255))
        select_text_rect = select_text.get_rect(center=self.select_button_rect.center)
        self.screen.blit(select_text, select_text_rect)


class WeaponSystem:
    """武器系统类"""
    
    def __init__(self, our_plane):
        self.our_plane = our_plane
        
        # 武器类型
        self.weapon_types = {
            'normal': {
                'name': '普通子弹',
                'damage': 1,
                'fire_rate': 10,
                'spread': 0,
                'image': pygame.image.load("material/image/bullet1.png")
            },
            'double': {
                'name': '双发子弹',
                'damage': 1,
                'fire_rate': 10,
                'spread': 20,
                'image': pygame.image.load("material/image/bullet2.png")
            },
            'laser': {
                'name': '激光',
                'damage': 3,
                'fire_rate': 5,
                'spread': 0,
                'image': pygame.image.load("material/image/bullet1.png")
            }
        }
        
        # 当前武器
        self.current_weapon = 'normal'
        
        # 武器切换冷却时间
        self.weapon_switch_cooldown = 0
        
        # 武器效果持续时间
        self.weapon_effects = {}
        
    def update(self):
        """更新武器系统"""
        # 处理武器切换冷却
        if self.weapon_switch_cooldown > 0:
            self.weapon_switch_cooldown -= 1
            
        # 处理武器效果持续时间
        for weapon_type in list(self.weapon_effects.keys()):
            self.weapon_effects[weapon_type] -= 1
            if self.weapon_effects[weapon_type] <= 0:
                del self.weapon_effects[weapon_type]
                
                # 如果当前武器效果结束，切换回普通武器
                if self.current_weapon == weapon_type:
                    self.current_weapon = 'normal'
                    
    def switch_weapon(self, weapon_type):
        """切换武器"""
        if weapon_type not in self.weapon_types:
            return
            
        if self.weapon_switch_cooldown == 0:
            self.current_weapon = weapon_type
            self.weapon_switch_cooldown = 60  # 1秒冷却时间
            
    def add_weapon_effect(self, weapon_type, duration):
        """添加武器效果"""
        if weapon_type not in self.weapon_types:
            return
            
        if weapon_type in self.weapon_effects:
            # 如果武器效果已存在，延长持续时间
            self.weapon_effects[weapon_type] += duration
        else:
            # 否则添加新的武器效果
            self.weapon_effects[weapon_type] = duration
            self.current_weapon = weapon_type
            
    def get_current_weapon(self):
        """获取当前武器"""
        return self.weapon_types[self.current_weapon]
        
    def get_weapon_duration(self, weapon_type):
        """获取武器效果剩余持续时间"""
        return self.weapon_effects.get(weapon_type, 0)


class ItemSystem:
    """道具系统类"""
    
    def __init__(self, screen, our_plane, weapon_system, score_system):
        self.screen = screen
        self.our_plane = our_plane
        self.weapon_system = weapon_system
        self.score_system = score_system
        self.width, self.height = screen.get_size()
        
        # 道具类型
        self.item_types = {
            'double_bullet': {
                'name': '双发子弹',
                'image': pygame.image.load("material/image/powerup_double.png"),
                'effect': 'weapon',
                'effect_param': 'double',
                'duration': 600  # 10秒
            },
            'laser': {
                'name': '激光',
                'image': pygame.image.load("material/image/powerup_laser.png"),
                'effect': 'weapon',
                'effect_param': 'laser',
                'duration': 300  # 5秒
            },
            'bomb': {
                'name': '炸弹',
                'image': pygame.image.load("material/image/bomb.png"),
                'effect': 'bomb',
                'effect_param': 1,
                'duration': 0  # 立即生效
            },
            'health': {
                'name': '生命',
                'image': pygame.image.load("material/image/powerup_health.png"),
                'effect': 'health',
                'effect_param': 1,
                'duration': 0  # 立即生效
            },
            'score_multiplier': {
                'name': '得分加倍',
                'image': pygame.image.load("material/image/powerup_score.png"),
                'effect': 'score_multiplier',
                'effect_param': 2,
                'duration': 600  # 10秒
            }
        }
        
        # 当前活动的道具
        self.active_items = []
        
        # 道具生成定时器
        self.item_spawn_timer = 0
        self.item_spawn_interval = 300  # 5秒生成一个道具
        
        # 道具效果
        self.active_effects = {
            'score_multiplier': 0,
            'health_boost': 0
        }
        
        # 炸弹数量
        self.bomb_count = 3
        
    def update(self, enemies):
        """更新道具系统"""
        # 生成道具
        self.item_spawn_timer += 1
        if self.item_spawn_timer >= self.item_spawn_interval:
            self.spawn_item()
            self.item_spawn_timer = 0
            self.item_spawn_interval = random.randint(200, 400)  # 随机生成间隔
            
        # 更新道具位置
        for item in self.active_items[:]:
            item['rect'].y += item['speed']
            
            # 检查是否超出屏幕
            if item['rect'].y > self.height:
                self.active_items.remove(item)
                continue
                
            # 检查是否与玩家飞机碰撞
            if pygame.sprite.collide_mask(self.our_plane, item['sprite']):
                self.collect_item(item)
                self.active_items.remove(item)
                continue
        
        # 更新道具效果
        for effect_type in list(self.active_effects.keys()):
            if self.active_effects[effect_type] > 0:
                self.active_effects[effect_type] -= 1
            else:
                # 效果结束
                if effect_type == 'score_multiplier':
                    self.score_system.score_multiplier = 1
                    
    def draw(self):
        """绘制道具"""
        for item in self.active_items:
            self.screen.blit(item['image'], item['rect'])
            
        # 绘制炸弹数量
        bomb_font = pygame.font.Font(None, 36)
        bomb_text = bomb_font.render(f"炸弹: {self.bomb_count}", True, (255, 255, 255))
        self.screen.blit(bomb_text, (self.width - 120, 10))
        
        # 绘制道具效果指示器
        self.draw_effect_indicators()
        
    def spawn_item(self):
        """生成道具"""
        # 随机选择道具类型
        item_type = random.choice(list(self.item_types.keys()))
        item_data = self.item_types[item_type]
        
        # 创建道具精灵
        item_sprite = pygame.sprite.Sprite()
        item_sprite.image = item_data['image']
        item_sprite.rect = item_data['image'].get_rect()
        item_sprite.mask = pygame.mask.from_surface(item_data['image'])
        
        # 随机生成位置
        x = random.randint(0, self.width - item_sprite.rect.width)
        y = random.randint(-200, -50)
        
        item_sprite.rect.x = x
        item_sprite.rect.y = y
        
        # 添加到活动道具列表
        self.active_items.append({
            'type': item_type,
            'data': item_data,
            'sprite': item_sprite,
            'image': item_data['image'],
            'rect': item_sprite.rect,
            'speed': random.randint(2, 5)
        })
        
    def collect_item(self, item):
        """收集道具"""
        item_type = item['type']
        item_data = item['data']
        
        if item_data['effect'] == 'weapon':
            self.weapon_system.add_weapon_effect(item_data['effect_param'], item_data['duration'])
            get_bullet_sound.play()
        elif item_data['effect'] == 'bomb':
            self.bomb_count += item_data['effect_param']
            get_bomb_sound.play()
        elif item_data['effect'] == 'health':
            # 这里假设飞机有生命值属性
            if hasattr(self.our_plane, 'health'):
                self.our_plane.health += item_data['effect_param']
                if self.our_plane.health > self.our_plane.max_health:
                    self.our_plane.health = self.our_plane.max_health
        elif item_data['effect'] == 'score_multiplier':
            self.active_effects['score_multiplier'] = item_data['duration']
            self.score_system.score_multiplier = item_data['effect_param']
            level_up_sound.play()
            
    def use_bomb(self, enemies):
        """使用炸弹"""
        if self.bomb_count > 0:
            bomb_sound.play()
            self.bomb_count -= 1
            
            # 清除所有敌机
            for enemy in enemies:
                enemy.active = False
                
            # 播放炸弹特效
            # 这里可以添加炸弹爆炸的特效动画
            
    def draw_effect_indicators(self):
        """绘制道具效果指示器"""
        x = 10
        y = 100
        
        # 绘制得分加倍效果
        if self.active_effects['score_multiplier'] > 0:
            multiplier_text = self.text_font.render(f"得分加倍: {self.active_effects['score_multiplier'] // 60}s", True, (255, 255, 0))
            self.screen.blit(multiplier_text, (x, y))
            y += 40
            
        # 绘制当前武器效果
        for weapon_type in self.weapon_system.weapon_effects:
            duration = self.weapon_system.weapon_effects[weapon_type]
            if duration > 0:
                weapon_text = self.text_font.render(f"{self.weapon_system.weapon_types[weapon_type]['name']}: {duration // 60}s", True, (0, 255, 0))
                self.screen.blit(weapon_text, (x, y))
                y += 40
                
    def get_score_multiplier(self):
        """获取得分倍数"""
        return self.active_effects.get('score_multiplier', 0) > 0 and self.score_system.score_multiplier or 1


class EffectSystem:
    """效果系统类，负责管理所有视觉效果"""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # 爆炸效果
        self.explosion_effects = []
        
        # 激光效果
        self.laser_effects = []
        
        # 粒子效果
        self.particle_effects = []
        
    def add_explosion_effect(self, position, size='small'):
        """添加爆炸效果"""
        explosion = {
            'position': position,
            'size': size,
            'frames': [],
            'current_frame': 0,
            'frame_delay': 0,
            'active': True
        }
        
        # 根据爆炸大小加载不同的图像
        if size == 'small':
            for i in range(1, 5):
                image = pygame.image.load(f"material/image/explosion_small_{i}.png")
                explosion['frames'].append(image)
        elif size == 'medium':
            for i in range(1, 7):
                image = pygame.image.load(f"material/image/explosion_medium_{i}.png")
                explosion['frames'].append(image)
        elif size == 'large':
            for i in range(1, 9):
                image = pygame.image.load(f"material/image/explosion_large_{i}.png")
                explosion['frames'].append(image)
                
        self.explosion_effects.append(explosion)
        
    def add_laser_effect(self, start_pos, end_pos, color=(255, 0, 0), duration=5):
        """添加激光效果"""
        laser = {
            'start_pos': start_pos,
            'end_pos': end_pos,
            'color': color,
            'width': 3,
            'duration': duration,
            'active': True
        }
        
        self.laser_effects.append(laser)
        
    def add_particle_effect(self, position, count=10, color=(255, 255, 255), size=2, speed=5):
        """添加粒子效果"""
        particles = []
        
        for _ in range(count):
            angle = random.uniform(0, 360)
            x_speed = speed * random.cos(angle)
            y_speed = speed * random.sin(angle)
            
            particle = {
                'position': list(position),
                'velocity': (x_speed, y_speed),
                'color': color,
                'size': size,
                'life': random.randint(10, 30),
                'active': True
            }
            
            particles.append(particle)
            
        self.particle_effects.append({
            'particles': particles,
            'active': True
        })
        
    def update(self):
        """更新所有效果"""
        # 更新爆炸效果
        for explosion in self.explosion_effects[:]:
            if not explosion['active']:
                self.explosion_effects.remove(explosion)
                continue
                
            explosion['frame_delay'] += 1
            if explosion['frame_delay'] >= 3:
                explosion['current_frame'] += 1
                explosion['frame_delay'] = 0
                
                if explosion['current_frame'] >= len(explosion['frames']):
                    explosion['active'] = False
        
        # 更新激光效果
        for laser in self.laser_effects[:]:
            if not laser['active']:
                self.laser_effects.remove(laser)
                continue
                
            laser['duration'] -= 1
            if laser['duration'] <= 0:
                laser['active'] = False
        
        # 更新粒子效果
        for effect in self.particle_effects[:]:
            if not effect['active']:
                self.particle_effects.remove(effect)
                continue
                
            active_particles = []
            for particle in effect['particles']:
                if not particle['active']:
                    continue
                    
                particle['position'][0] += particle['velocity'][0]
                particle['position'][1] += particle['velocity'][1]
                particle['life'] -= 1
                
                if particle['life'] > 0:
                    active_particles.append(particle)
                    
            if not active_particles:
                effect['active'] = False
            else:
                effect['particles'] = active_particles
        
    def draw(self):
        """绘制所有效果"""
        # 绘制爆炸效果
        for explosion in self.explosion_effects:
            if explosion['active']:
                image = explosion['frames'][explosion['current_frame']]
                rect = image.get_rect(center=explosion['position'])
                self.screen.blit(image, rect)
        
        # 绘制激光效果
        for laser in self.laser_effects:
            if laser['active']:
                pygame.draw.line(self.screen, laser['color'], laser['start_pos'], laser['end_pos'], laser['width'])
        
        # 绘制粒子效果
        for effect in self.particle_effects:
            for particle in effect['particles']:
                if particle['active']:
                    pygame.draw.circle(self.screen, particle['color'], 
                                      (int(particle['position'][0]), int(particle['position'][1])), 
                                      particle['size'])
