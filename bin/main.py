#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import os

from pygame.locals import *

# 添加项目根目录到sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config.settings import *
from src.plane import OurPlane  # 导入我们的飞机
from src.enemy import SmallEnemy
from src.bullet import Bullet
from src.score import ScoreSystem
from src.menu import StartMenu, ScoreHistoryScreen
from src.systems import KillEffectSystem, SkinSystem, WeaponSystem, ItemSystem, EffectSystem


bg_size = 480, 852  # 初始化游戏背景大小(宽, 高)
screen = pygame.display.set_mode(bg_size)  # 设置背景对话框
pygame.display.set_caption("飞机大战")  # 设置标题

background = pygame.image.load(os.path.join(BASE_DIR, "material/image/background.png"))  # 加载背景图片,并设置为不透明


# 血槽颜色绘制
color_black = (0, 0, 0)
color_green = (0, 255, 0)
color_red = (255, 0, 0)
color_white = (255, 255, 255)

# 初始化得分系统
score_system = ScoreSystem()

# 获取我方飞机
our_plane = OurPlane(bg_size)

# 初始化新系统
kill_effect_system = KillEffectSystem(screen)
skin_system = SkinSystem(screen, our_plane)
weapon_system = WeaponSystem(our_plane)
item_system = ItemSystem(screen, our_plane, weapon_system, score_system)
effect_system = EffectSystem(screen)

# 加载保存的皮肤选择
skin_system.load_skin_selection()


def add_small_enemies(group1, group2, num):
    """
    添加小型敌机
    指定个敌机对象添加到精灵组（sprite.group）
    参数group1、group2是两个精灵组类型的形参，用以存储多个精灵对象（敌机）。
    需要注意的一点是group既然是特定的精灵组结构体，在向其内部添加精灵对象时需要调用其对应的成员函数add()
    :return:
    """
    for i in range(num):
        small_enemy = SmallEnemy(bg_size)
        group1.add(small_enemy)
        group2.add(small_enemy)


def game_loop():
    """游戏主循环"""
    # 响应音乐
    pygame.mixer.music.play(-1)  # loops 接收该参数, -1 表示无限循环(默认循环播放一次)
    running = True
    switch_image = False  # 切换飞机的标识位(使飞机具有喷气式效果)
    delay = 60  # 对一些效果进行延迟, 效果更好一些
    start_time = time.time()  # 记录游戏开始时间

    enemies = pygame.sprite.Group()  # 生成敌方飞机组(一种精灵组用以存储所有敌机精灵)
    small_enemies = pygame.sprite.Group()  # 敌方小型飞机组(不同型号敌机创建不同的精灵组来存储)

    add_small_enemies(small_enemies, enemies, 6)  # 生成若干敌方小型飞机

    # 定义子弹, 各种敌机和我方敌机的毁坏图像索引
    bullet_index = 0
    e1_destroy_index = 0
    me_destroy_index = 0
    score_font = pygame.font.Font(None, 36)  # 得分显示字体
    high_score_font = pygame.font.Font(None, 24)  # 最高分显示字体

    # 定义子弹实例化个数
    bullet1 = []
    bullet_num = 6
    for i in range(bullet_num):
        bullet1.append(Bullet(our_plane.rect.midtop))
    
    # 重置得分系统
    score_system.reset_score()
    score_system.score_multiplier = 1
    
    # 重置飞机状态
    our_plane.reset()
    
    # 重置道具系统
    item_system.bomb_count = 3
    
    # 重置武器系统
    weapon_system.current_weapon = 'normal'
    weapon_system.weapon_effects = {}

    while running:

        # 绘制背景图
        screen.blit(background, (0, 0))

        # 微信的飞机貌似是喷气式的, 那么这个就涉及到一个帧数的问题
        clock = pygame.time.Clock()
        clock.tick(60)
        
        # 更新各种系统
        our_plane.update()
        kill_effect_system.update()
        weapon_system.update()
        item_system.update(enemies)
        effect_system.update()

        # 绘制我方飞机的两种不同的形式
        if not delay % 3:
            switch_image = not switch_image

        for each in small_enemies:
            if each.active:
                # 随机循环输出小飞机敌机
                each.move()
                screen.blit(each.image, each.rect)

                pygame.draw.line(screen, color_black,
                                 (each.rect.left, each.rect.top - 5),
                                 (each.rect.right, each.rect.top - 5),
                                 2)
                energy_remain = each.energy / SmallEnemy.energy
                if energy_remain > 0.2:  # 如果血量大约百分之二十则为绿色，否则为红色
                    energy_color = color_green
                else:
                    energy_color = color_red
                pygame.draw.line(screen, energy_color,
                                 (each.rect.left, each.rect.top - 5),
                                 (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),
                                 2)
            else:
                if e1_destroy_index == 0:
                    enemy1_down_sound.play()
                screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                e1_destroy_index = (e1_destroy_index + 1) % 4
                if e1_destroy_index == 0:
                    each.reset()

        # 当我方飞机存活状态, 正常展示
        if our_plane.active:
            # 绘制飞机（考虑无敌状态的闪烁效果）
            if not our_plane.invincible or delay % 5 < 3:
                if switch_image:
                    screen.blit(our_plane.image_one, our_plane.rect)
                else:
                    screen.blit(our_plane.image_two, our_plane.rect)

            # 飞机存活的状态下才可以发射子弹
            current_weapon = weapon_system.get_current_weapon()
            if not (delay % current_weapon['fire_rate']):  # 根据当前武器的射速发射子弹
                bullet_sound.play()
                bullets = bullet1
                
                # 根据武器类型发射不同数量的子弹
                if current_weapon['name'] == '普通子弹':
                    bullets[bullet_index].reset(our_plane.rect.midtop)
                    bullet_index = (bullet_index + 1) % bullet_num
                elif current_weapon['name'] == '双发子弹':
                    # 发射两颗子弹，左右分开
                    bullets[bullet_index].reset((our_plane.rect.midtop[0] - 20, our_plane.rect.midtop[1]))
                    bullet_index = (bullet_index + 1) % bullet_num
                    bullets[bullet_index].reset((our_plane.rect.midtop[0] + 20, our_plane.rect.midtop[1]))
                    bullet_index = (bullet_index + 1) % bullet_num
                elif current_weapon['name'] == '激光':
                    # 发射激光
                    effect_system.add_laser_effect(
                        our_plane.rect.midtop,
                        (our_plane.rect.midtop[0], 0),
                        color=(0, 255, 255),
                        duration=5
                    )
                    
                    # 检测激光是否击中敌机
                    for enemy in enemies:
                        if enemy.active and enemy.rect.collidepoint((our_plane.rect.midtop[0], enemy.rect.top)):
                            enemy.active = False
                            score_system.add_score("small")
                            kill_effect_system.add_kill_effect(enemy.rect.center, "small")

            for b in bullets:
                if b.active:  # 只有激活的子弹才可能击中敌机
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemies_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemies_hit:  # 如果子弹击中飞机
                        b.active = False  # 子弹损毁
                        for e in enemies_hit:
                            e.active = False  # 小型敌机损毁
                            score_system.add_score("small")  # 添加得分
                            kill_effect_system.add_kill_effect(e.rect.center, "small")

        # 毁坏状态绘制爆炸的场面
        else:
            if not (delay % 3):
                screen.blit(our_plane.destroy_images[me_destroy_index], our_plane.rect)
                me_destroy_index = (me_destroy_index + 1) % 4
                if me_destroy_index == 0:
                    me_down_sound.play()
                    score_system.save_score()  # 保存得分
                    return  # 游戏结束，返回主菜单

        # 调用 pygame 实现的碰撞方法 spritecollide (我方飞机如果和敌机碰撞, 更改飞机的存活属性)
        enemies_down = pygame.sprite.spritecollide(our_plane, enemies, False, pygame.sprite.collide_mask)
        if enemies_down:
            for enemy in enemies_down:
                if enemy.active:
                    enemy.active = False
                    # 飞机受到伤害
                    if not our_plane.take_damage():
                        # 飞机被摧毁
                        for row in enemies:
                            row.active = False

        # 响应用户的操作
        for event in pygame.event.get():
            if event.type == 12:  # 如果用户按下屏幕上的关闭按钮，触发QUIT事件，程序退出
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    # 切换皮肤菜单
                    skin_system.toggle_skin_menu()
                elif event.key == pygame.K_SPACE:
                    # 使用炸弹
                    item_system.use_bomb(enemies)
            
            # 处理皮肤菜单事件
            if skin_system.skin_menu_active:
                skin_system.handle_event(event)

        if delay == 0:
            delay = 60
        delay -= 1

        # 获得用户所有的键盘输入序列(如果用户通过键盘发出“向上”的指令,其他类似)
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[K_UP]:
            our_plane.move_up()
        if key_pressed[K_s] or key_pressed[K_DOWN]:
            our_plane.move_down()
        if key_pressed[K_a] or key_pressed[K_LEFT]:
            our_plane.move_left()
        if key_pressed[K_d] or key_pressed[K_RIGHT]:
            our_plane.move_right()

        # 显示得分
        score_text = score_font.render(f"Score: {score_system.score}", True, color_white)
        screen.blit(score_text, (10, 10))
        
        # 显示最高分
        high_score_text = high_score_font.render(f"High Score: {score_system.high_score}", True, color_white)
        screen.blit(high_score_text, (10, 50))
        
        # 显示当前武器
        current_weapon = weapon_system.get_current_weapon()
        weapon_text = high_score_font.render(f"Weapon: {current_weapon['name']}", True, color_white)
        screen.blit(weapon_text, (10, 90))
        
        # 显示生命值
        health_bar_width = 100
        health_bar_height = 10
        health_ratio = our_plane.health / our_plane.max_health
        pygame.draw.rect(screen, color_black, (10, 130, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, color_red if health_ratio < 0.3 else color_green, 
                         (10, 130, health_bar_width * health_ratio, health_bar_height))
        health_text = high_score_font.render(f"Health: {our_plane.health}/{our_plane.max_health}", True, color_white)
        screen.blit(health_text, (10, 150))

        # 绘制各种效果
        kill_effect_system.draw()
        effect_system.draw()
        
        # 绘制道具
        item_system.draw()
        
        # 绘制皮肤菜单
        skin_system.draw()
        
        # 绘制图像并输出到屏幕上面
        pygame.display.flip()
    return "quit"

def main():
    """游戏主入口"""
    running = True
    current_screen = "start_menu"
    
    # 创建开始菜单和得分历史屏幕
    start_menu = StartMenu(screen, score_system)
    score_history = ScoreHistoryScreen(screen, score_system)
    
    while running:
        if current_screen == "start_menu":
            result = start_menu.run()
            if result == "start_game":
                # 重置飞机状态
                our_plane.reset()
                # 开始游戏循环
                game_result = game_loop()
                if game_result == "quit":
                    running = False
                else:
                    current_screen = "start_menu"
            elif result == "show_history":
                current_screen = "score_history"
            elif result == "quit":
                running = False
        elif current_screen == "score_history":
            result = score_history.run()
            if result == "back":
                current_screen = "start_menu"
            elif result == "quit":
                running = False
    
    # 清理资源
    score_system.save_score()
    score_system.close()
    pygame.quit()
    sys.exit()




