import arcade
import enum
import math


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1100
SCREEN_TITLE = "Спрайтовый герой"


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Основные характеристики
        self.scale = 1.0
        self.speed = 250
        self.health = 100   
        
        # Загрузка текстур
        self.idle_texture = arcade.load_texture("pictures/anim/скелет/стоять на месте.png")
        self.texture = self.idle_texture
        
        self.walk_textures = []
        texture = arcade.load_texture("pictures/anim/скелет/идти в право 1.png")
        self.walk_textures.append(texture)
        texture = arcade.load_texture("pictures/anim/скелет/идти в право 2.png")
        self.walk_textures.append(texture)
            
        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1  # секунд на кадр
        
        self.is_walking = False # Никуда не идём
        self.face_direction = FaceDirection.RIGHT  # и смотрим вправо

        # Центрируем персонажа
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

    def update_animation(self, delta_time: float = 1/60):
        """ Обновление анимации """
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0
                # Поворачиваем текстуру в зависимости от направления взгляда
                if self.face_direction == FaceDirection.RIGHT:
                    self.texture = self.walk_textures[self.current_texture]
                else:
                    self.texture = self.walk_textures[self.current_texture].flip_horizontally()

        else:
            # Если не идём, то просто показываем текстуру покоя
            # и поворачиваем её в зависимости от направления взгляда
            if self.face_direction == FaceDirection.RIGHT:
                self.texture = self.idle_texture
            else:
                self.texture = self.idle_texture.flip_horizontally()

       
    def update(self, delta_time, keys_pressed):
        """ Перемещение персонажа """
        # В зависимости от нажатых клавиш определяем направление движения
        dx, dy = 0, 0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed * delta_time
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed * delta_time

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy
        # Поворачиваем персонажа в зависимости от направления движения
        # Если никуда не идём, то не меняем направление взгляда
        if dx < 0:
            self.face_direction = FaceDirection.LEFT
        elif dx > 0:
            self.face_direction = FaceDirection.RIGHT

        # Проверка на движение
        self.is_walking = dx or dy



class Bullet(arcade.Sprite):
    __texture = arcade.load_texture("pictures/photo/missile.png")

    def __init__(self, start_x, start_y, target_x, target_y, speed=800, damage=10):
        super().__init__()
        self.texture = self.__texture
        self.center_x = start_x
        self.center_y = start_y
        self.scale = 0.1
        self.speed = speed
        self.damage = damage
        
        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        self.angle = math.degrees(-angle)  # Поворот пули
        
    def update(self, delta_time):
        # Удаляем пулю, если она ушла за экран
        if (self.center_x < -100 or self.center_x > SCREEN_WIDTH + 100 or
            self.center_y < -100 or self.center_y > SCREEN_HEIGHT + 100):
            self.remove_from_sprite_lists()

        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time


class Slime(arcade.Sprite):
    def __init__(self, x, y, speed=50, damage=10):  # Уменьшил скорость для реалистичности
        super().__init__(scale=0.1)
        self.texture = arcade.load_texture("pictures/anim/слизень/slime.png")
        self.speed = speed
        self.damage = damage
        self.center_x = x
        self.center_y = y
        
    def follow_player(self, player, delta_time, wall_list):
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            old_x = self.center_x
            old_y = self.center_y
            
            self.center_x += dx * self.speed * delta_time
            self.center_y += dy * self.speed * delta_time
            hit_wall = arcade.check_for_collision_with_list(self, wall_list)
            if hit_wall:
                self.center_x = old_x
                self.center_y = old_y
                self.center_x = old_x + dx * self.speed * delta_time
                self.center_y = old_y
                hit_wall_x = arcade.check_for_collision_with_list(self, wall_list)
                if hit_wall_x:
                    self.center_x = old_x
                
                self.center_y = old_y + dy * self.speed * delta_time
                hit_wall_y = arcade.check_for_collision_with_list(self, wall_list)
                if hit_wall_y:
                    self.center_y = old_y