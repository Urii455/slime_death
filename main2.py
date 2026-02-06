import arcade
import time
from pyglet.graphics import Batch
import math
import enum
import random
from classes import Hero, Bullet, Slime
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount
from pyglet.graphics import Batch
from dataclasses import dataclass


A = None

class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1

# Задаём размеры окна
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Спрайтовый герой"
SPARK_TEX = [
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
    arcade.make_soft_circle_texture(8, arcade.color.PEACH),
    arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
    arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
]

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.world_camera.zoom = 2
        self.all_sprites = arcade.SpriteList()
        self.player_sprite = Hero()
        self.collision_list = list()
        self.map_width = 50
        self.map_height = 50
        self.tile_size = 32
        self.score = 0
        self.batch = Batch()
        self.health = 100
        self.num = 0
        self.game_music = arcade.load_sound("sound/game_music.mp3")
        self.is_invincible = False
        self.invincible_end_time = 2



    def setup(self):
        arcade.play_sound(self.game_music, volume=1, loop=1)   #   музыка игры
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.bullet_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList(use_spatial_hash=True)
        map_name = "текстуры/карта2.tmx"
        self.slime_list = arcade.SpriteList(use_spatial_hash=True)
        
        scale_x = self.width / (self.map_width * self.tile_size)
        scale_y = self.height / (self.map_height * self.tile_size)
        scale = min(scale_x, scale_y)
        tile_map = arcade.load_tilemap(map_name, scaling=self.scale)


        self.wall_list = tile_map.sprite_lists["Слой тайлов 2"]
        self.chests_list = tile_map.sprite_lists["Слой тайлов 1"]
        self.collision_list.append(self.wall_list)
        
        self.player = Hero()
        self.player_list.append(self.player)
        for _ in range(20):
            self.slime_list.append(Slime(random.randint(50, SCREEN_WIDTH), random.randint(110, SCREEN_HEIGHT - 100)))
            for slime in self.slime_list:
                hit_wall = arcade.check_for_collision_with_list(slime, self.wall_list) # делаю так что бы слизни не спавнились в стенах
                if hit_wall:
                    slime.remove_from_sprite_lists()
                    self.slime_list.append(Slime(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))
            

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list
        )
        self.shoot_sound = arcade.load_sound("sound/пистолет.mp3")
        self.slime_dead_sound = arcade.load_sound("sound/slime_dead.mp3")
        self.death = arcade.load_sound("sound/смерть.mp3")
        
        self.keys_pressed = set()
        self.lable_score = arcade.Text(f"Score: {self.score}", 80, 30, batch=self.batch, font_size=25, color=arcade.color.WHITE,
                                        anchor_x="center", anchor_y="center")
        self.lable_score2 = arcade.Text(f"health: {self.score}", 102, 60, batch=self.batch, font_size=25, color=arcade.color.WHITE,
                                        anchor_x="center", anchor_y="center")
                                        

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.chests_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()
        self.slime_list.draw()

        self.gui_camera.use()

        self.batch.draw()


    def on_update(self, delta_time):
        if self.num == 0: # что бы хп с 1 секунды писались
            self.lable_score2.text = f"health: {self.health}"
            self.num += 1

        self.player_list.update(delta_time, self.keys_pressed)
        self.physics_engine.update()
        
        # Слизень двигается к игроку
        for slime in self.slime_list:
            slime.follow_player(self.player, delta_time, self.wall_list)
        
        position = (
            self.player.center_x,
            self.player.center_y
        )
        CAMERA_LERP = 0.15
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            CAMERA_LERP,  # Плавность
        )
        self.player_list.update_animation()
        
        for bullet in self.bullet_list:
            bullet.update(delta_time)
        
        for bullet in self.bullet_list:
            hit_wall = arcade.check_for_collision_with_list(bullet, self.wall_list) # удаление пули при врезание в стену
            if hit_wall:
                bullet.remove_from_sprite_lists()
        
        for slime in self.slime_list:
            hit_slime = arcade.check_for_collision_with_list(slime, self.bullet_list)   # удаление слизни при врезание пули в слизня
            if hit_slime:
                print(slime)
                slime.remove_from_sprite_lists()
                self.score += 1
                self.slime_list.append(Slime(random.randint(110, SCREEN_HEIGHT - 100), random.randint(50, SCREEN_WIDTH)))
                arcade.play_sound(self.slime_dead_sound, volume=1)
                for slime in self.slime_list:
                    hit_wall = arcade.check_for_collision_with_list(slime, self.wall_list) # делаю так что бы слизни не спавнились в стенах
                    if hit_wall:
                        slime.remove_from_sprite_lists()
                        self.slime_list.append(Slime(random.randint(110, SCREEN_HEIGHT - 100), random.randint(50, SCREEN_WIDTH)))
        
        player_damage = arcade.check_for_collision_with_list(self.player, self.slime_list)
        if player_damage:
            if self.is_invincible:
                if time.time() > self.invincible_end_time:
                    self.is_invincible = False
            if not self.is_invincible:
                self.health -= 10
                arcade.play_sound(self.death, volume=0.8)
                self.start_invincibility(0.7)
                self.lable_score2.text = f"health: {self.health}"   # выводим хп
                if self.health == 0:
                    arcade.close_window()
            else:
                self.lable_score2.text = f"health: {self.health}"   # выводим хп

            

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_coords = self.world_camera.unproject((x, y))
            world_x = world_coords[0]
            world_y = world_coords[1]

            bullet = Bullet(
                self.player.center_x,
                self.player.center_y,
                world_x,
                world_y
            )
            self.bullet_list.append(bullet)
            # Проигрываем звук выстрела
            arcade.play_sound(self.shoot_sound, volume=0.3)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        
    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    
    def start_invincibility(self, seconds=1):
        self.is_invincible = True
        self.invincible_end_time = time.time() + seconds

def make_ring(x, y, count=40, radius=5.0):
    # Кольцо искр (векторы направлены по окружности)
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(count),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=random.choice(SPARK_TEX),
            change_xy=arcade.math.rand_on_circle((0.0, 0.0), radius),
            lifetime=random.uniform(0.8, 1.4),
            start_alpha=255, end_alpha=0,
            scale=random.uniform(0.4, 0.7),
            mutation_callback=gravity_drag,
        ),
    )


def gravity_drag(p):  # Для искр: чуть вниз и затухание скорости
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92


def main2():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main2()