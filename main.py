import arcade
import math
import enum

# Делаем класс для направления взгляда персонажа,
# это позволит не запутаться в чиселках и сделать код более читаемым
class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1

# Задаём размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Спрайтовый герой"

class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()
        
        # Основные характеристики
        self.scale = 1.0
        self.speed = 300
        self.health = 100
        
        # Загрузка текстур
        self.idle_texture = arcade.load_texture(":resources:/images/animated_characters/male_person/malePerson_idle.png")
        self.texture = self.idle_texture
        
        self.walk_textures = []
        for i in range(0, 8):
            texture = arcade.load_texture(f":resources:/images/animated_characters/male_person/malePerson_walk{i}.png")
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
        
        # Ограничение в пределах экрана
        self.center_x = max(self.width/2, min(SCREEN_WIDTH - self.width/2, self.center_x))
        self.center_y = max(self.height/2, min(SCREEN_HEIGHT - self.height/2, self.center_y))

        # Проверка на движение
        self.is_walking = dx or dy



class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, speed=800, damage=10):
        super().__init__()
        self.texture = arcade.load_texture(":resources:/images/space_shooter/laserBlue01.png")
        self.center_x = start_x
        self.center_y = start_y
        self.speed = speed
        self.damage = damage
        
        # Рассчитываем направление
        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)
        # И скорость
        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        # Если текстура ориентирована по умолчанию вправо, то поворачиваем пулю в сторону цели
        # Для другой ориентации нужно будет подправить угол
        self.angle = math.degrees(-angle)  # Поворачиваем пулю
        
    def update(self, delta_time):
        # Удаляем пулю, если она ушла за экран
        if (self.center_x < 0 or self.center_x > SCREEN_WIDTH or
            self.center_y < 0 or self.center_y > SCREEN_HEIGHT):
            self.remove_from_sprite_lists()

        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time



class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.ASH_GREY)

    def setup(self):
        # Создаём SpriteList для разных типов объектов
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        
        # Создаём игрока
        self.player = Hero()
        self.player_list.append(self.player)

        # Добавляем звук выстрела — и игра автоматически становится на 20% лучше!
        self.shoot_sound = arcade.load_sound(":resources:/sounds/laser1.wav")
        
        self.keys_pressed = set()

    def on_draw(self):
        self.clear()
        # Рисуем все списки в правильном порядке
        self.wall_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()

    def on_update(self, delta_time):
        # Обновляем все списки (кроме неподвижных стен)
        self.player_list.update(delta_time, self.keys_pressed)
        self.bullet_list.update()
        
        # Обновляем анимации игрока
        self.player_list.update_animation()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            bullet = Bullet(
                self.player.center_x,
                self.player.center_y,
                x,
                y
            )
            self.bullet_list.append(bullet)
            # Проигрываем звук выстрела
            arcade.play_sound(self.shoot_sound)

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