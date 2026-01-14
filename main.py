import arcade
from pyglet.graphics import Batch
import math
import enum
import random
from classes import Hero, Bullet, Slime

# Делаем класс для направления взгляда персонажа,
# это позволит не запутаться в чиселках и сделать код более читаемым
class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1

# Задаём размеры окна
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1100
SCREEN_TITLE = "Спрайтовый герой"


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


    def setup(self):
        # Создаём SpriteList для разных типов объектов
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        map_name = "текстуры/карта1.tmx"
        self.slime_list = arcade.SpriteList()
        
        scale_x = self.width / (self.map_width * self.tile_size)
        scale_y = self.height / (self.map_height * self.tile_size)
        scale = min(scale_x, scale_y)
        tile_map = arcade.load_tilemap(map_name, scaling=self.scale)


        self.wall_list = tile_map.sprite_lists["Слой тайлов 2"]
        self.chests_list = tile_map.sprite_lists["Слой тайлов 1"]
        self.collision_list.append(self.wall_list)
        
        # Создаём игрока
        self.player = Hero()
        self.player_list.append(self.player)
        for _ in range(20):
            self.slime_list.append(Slime(random.randint(0, self._width), random.randint(0, self._height)))

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list
        )
        self.shoot_sound = arcade.load_sound("sound/пистолет.mp3")
        self.slime_dead_sound = arcade.load_sound("sound/slime_dead.mp3")
        
        self.keys_pressed = set()
        self.lable_score = arcade.Text(f"Score: {self.score}", 125, 50, batch=self.batch, font_size=50, color=arcade.color.WHITE,
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
        # Обновляем все списки (кроме неподвижных стен)
        self.player_list.update(delta_time, self.keys_pressed)
        self.physics_engine.update()
        self.slime_list.update()
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
            hit_wall = arcade.check_for_collision_with_list(bullet, self.wall_list) # Удаление пули при врезание в стену
            if hit_wall:
                bullet.remove_from_sprite_lists()
        
        for slime in self.slime_list:
            hit_slime = arcade.check_for_collision_with_list(slime, self.bullet_list)   # Удаление слизни при врезание пули в слизня
            if hit_slime:
                slime.remove_from_sprite_lists()
                self.score += 1
                self.slime_list.append(Slime(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))
                arcade.play_sound(self.slime_dead_sound, volume=1)

        self.lable_score.text = f"Score: {self.score}"

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

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()  # Запускаем начальную настройку игры
    arcade.run()


if __name__ == "__main__":
    main()