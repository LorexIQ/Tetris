from copy import deepcopy
from random import choice

import pygame
import re

rows = 10  # Число столбцов
columns = 20  # Число строчек
size_block = 30  # Размер 1 блока фигуры
GameWSize = rows * size_block, columns * size_block  # Размер игрового поля
InfoWSize = 575, 660  # Размер информационного поля
NextPocketWSize = 150, 150  # Размер поля следующей фигуры
RecordWSize = 240, 515  # Размер полей рекордов и настроек
RecordValue = 15  # Кол-во рекордов в списке
FPS = 60  # Частота обновления экрана
SpeedMain = 40  # Скорость падения фигуры
ZeroPosY = 0  # Нулевая скорость
MaxSpeed = 1000   # Скорость дропа фигуры
menu_run = True  # Переменная запуска меню
drop = False  # Переменная моментального дропа фигуры
state = []  # Массив выгрузки настроек из меню (Сетка, тень, звук, дроп, ник)
music_run = True  # Переменная одноразоового запуска музыки
Speed = SpeedMain  # Дублёж переменной скорости, для сохранения её при повторном прохождении игры
# Правый край игрового поля
DistanceRightArea = (InfoWSize[0] - ((InfoWSize[0] - (30 + rows * size_block)) // 2)) - NextPocketWSize[0] / 2
high_score = 0  # Лучший счёт
named = 'Guest'  # Ник
move = [0, 0]  # Массив хранения параметров отслеживания нажатий клавиш <- и ->
score = 0  # Текущий счёт
lines = 0  # Срезания линий
lines_score = 0  # Срезанные линии
scores = {0: 0, 1: 50, 2: 150, 3: 500, 4: 1000}  # Массив магазина начисляемых очков за кол-во срезанных линий

# Переменные цветов (Удобнее, чем pygame.Color('цвет'))
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (139, 0, 255)
SKYBLUE = (66, 170, 255)
GRAY = (26, 26, 26)
DARKORANGE = (255, 104, 0)
DARKOBLACKORANGE = (200, 100, 0)
DARKGRAY = (20, 20, 20)
BLACKORANGE = (102, 66, 0)
BUTTONACTIVE = (204, 82, 0)
DARKRED = (100, 0, 0)

# Создание главного окна и поверхностей
pygame.init()
main_win = pygame.display.set_mode(InfoWSize)
menu = pygame.Surface(InfoWSize)
next_area = pygame.Surface(NextPocketWSize)
pocket_area = pygame.Surface(NextPocketWSize)
game_area = pygame.Surface(GameWSize)
record_area = pygame.Surface(RecordWSize)
setting_area = pygame.Surface(RecordWSize)
lose_menu_area = pygame.Surface(InfoWSize)
pause_area = pygame.Surface(InfoWSize, pygame.SRCALPHA)
clock = pygame.time.Clock()
pygame.display.set_caption("Тетрис v1.03")

# Создание сетки игрового поля
grid = [pygame.Rect(x * size_block, y * size_block, size_block, size_block) for y in range(columns, -1, -1)
        for x in range(rows)]
# Создание рамок информационных поверхностей
vbm = 30  # value borders menu (Отступ бортов интерфейса от краёв экрана)
boorders_rect = ((0, 0), (rows * size_block - 1, 0), (rows * size_block - 1, columns * size_block - 1),
                 (0, size_block * columns - 1))
boorders_next_rect = ((0, 0), (NextPocketWSize[0] - 1, 0), (NextPocketWSize[0] - 1, NextPocketWSize[0] - 1),
                      (0, NextPocketWSize[0] - 1))
boorders_menu = ((273, InfoWSize[1] - vbm), (273, vbm), (InfoWSize[0] - vbm, vbm), (InfoWSize[0] - vbm, InfoWSize[1] - vbm),
                 (vbm, InfoWSize[1] - vbm), (vbm, 95), (273, 95))
boorders_lose_menu = ((vbm, vbm), (InfoWSize[0] - vbm, vbm), (InfoWSize[0] - vbm, InfoWSize[1] - vbm),
                      (vbm, InfoWSize[1] - vbm))

# Шрифты разных размеров
font_tetris = pygame.font.Font('Font/Font.ttf', 45)
font_label = pygame.font.Font('Font/Font.ttf', 20)
font_score = pygame.font.Font('Font/Font.ttf', 15)
font_end = pygame.font.Font('Font/Font.ttf', 30)

# Загрузка музыки
pygame.mixer.music.load('Sound/Music.mp3')

# Массивы фигур
I = [(-1, 0), (-2, 0), (0, 0), (1, 0)]
L = [(0, 0), (0, -1), (0, 1), (-1, -1)]
J = [(0, 0), (0, -1), (0, 1), (1, -1)]
Z = [(-1, 0), (-1, 1), (0, 0), (0, -1)]
S = [(0, 0), (-1, 0), (0, 1), (-1, -1)]
T = [(0, 0), (0, -1), (0, 1), (-1, 0)]
O = [(-1, 0), (-1, -1), (0, -1), (0, 0)]

figures_position = [O, I, Z, S, J, T, L]  # Объединение фигур в матрицу
figures_color = (YELLOW, SKYBLUE, RED, GREEN, ORANGE, PURPLE, BLUE)  # Массив с цветами фигур
# Создание квадратов фигур
figures = [[pygame.Rect(x + rows // 2, y + 1, 1, 1) for x, y in pos] for pos in figures_position]
one_rect_figure = pygame.Rect(0, 0, size_block - 2, size_block - 2)  # Позиционирование квадратов
zeroMas = [[0 for x in range(rows)] for y in range(columns)]  # Массив сохранения состояний падающих фигур
colorType = choice(figures)  # Случайный выбор фигуры
colorTypeNext = choice(figures)  # Случайный выбор следующей фигуры
figure = deepcopy(colorType)  # Глубока копия фигуры
next_figure = deepcopy(colorTypeNext)  # Глубокая копия следующей фигуры
figure_index = figures.index(colorTypeNext)  # Получание индекса фигуры в списке
buffer = deepcopy(figure)  # Буфер фигуры
pocket = []  # Массив кармана
score_pocket = 1  # Проверка наличия фигуры в кармане
color_pocket = []  # Цвет фигуры в кармане
pocket_index = 0  # Индекс фигуры в кармане
shadow_figure = deepcopy(colorType)  # Глубокая копия фигуры для создания тени

# Создание прямоугольников для настроек и рекордов
HieghtRecord = RecordWSize[1] / RecordValue
recordMasNameRect = [pygame.Rect(0, i * HieghtRecord,
                                 (RecordWSize[0] / 2) - 2, HieghtRecord - 5) for i in range(RecordValue)]
recordMasScoreRect = [pygame.Rect(123, i * HieghtRecord,
                                  (RecordWSize[0] / 2) - 2, HieghtRecord - 5) for i in range(RecordValue)]
settingMasRect = [pygame.Rect(0, i * 55, RecordWSize[0], 55 - 5) for i in range(4)]
settingMasBigRect = [pygame.Rect(0, 220 + i * 105, RecordWSize[0], 105 - 5) for i in range(2)]

# Класс (библиотека) создания полей для ввода символов
class ImputBox:
    # Основные параметры класса
    def __init__(self, maincolor, SecondColor, x, y, width, height, name = '', mass = None):
        self.maincolor = maincolor
        self.secondcolor = SecondColor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = name
        self.textcolor = maincolor
        self.mass = mass

    def draw(self, win, sizeText = 20, board = 3):  # Функция отрисовки
        if self.text == 'Guest':  # Проверка на стандартный ник
            self.textcolor = (70, 70, 70)  # Меняется цвет на серый
        else:
            self.textcolor = self.maincolor  # Меняется цвет на основной
        if self.mass == 1:  # Проверяется активность ввода
            color = self.secondcolor
        else:
            color = self.maincolor
        pygame.draw.rect(win, color, (self.x, self.y, self.width, self.height), board)  # Рисуем поле ввода
        font = pygame.font.Font('Font/Font.ttf', sizeText)  # Подключаем шрифт
        label = font.render(self.text, True, self.textcolor)  # Создание надписи
        # Размещение надписи посреди ImputBox'а
        win.blit(label, ((self.width / 2) + self.x - label.get_width() / 2,
                         (self.height / 2) + self.y - label.get_height() / 2))

    def imput(self, event_slider):  # Функция ввода текста
        if self.mass == 1:  # Если активен ввод
            if event_slider.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]  # Удалить последний символ
            elif len(self.text) < 11 and not event_slider.key == pygame.K_SPACE:
                self.text += event_slider.unicode  # Добавление символов, не более 1 и без пробелов

    def CheckMouseInButton(self, positionMouse):  # Функция проверки положения мыши
        if self.x <= positionMouse[0] - 289 <= self.x + self.width:
            if self.y <= positionMouse[1] - 100 <= self.y + self.height:
                return True
        return False

# Класс (библиотека) для создания слайдеров
class Slider:
    # Основные параметры класса
    def __init__(self, maincolor, SecondColor, x, y, width, height, radius, position_slider):
        self.maincolor = maincolor
        self.secondcolor = SecondColor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.xslide = position_slider

    def draw(self, win, mass, nameButton, board=None):  # Функция отрисовки
        posMouse = pygame.mouse.get_pos()  # Получаем позицию мыши
        if mass[0] == 1:
            nameButton.xslide = (posMouse[0] - self.x - 289) / nameButton.width  # Конвертируем координаты в 0.0/1.0
        if self.xslide * self.width < 0:  # Ограничитель минимального положения
            self.xslide = 0.0
        elif self.xslide * self.width > self.width:  # Ограничитель максимального положения
            self.xslide = 1.0
        pygame.draw.rect(win, self.secondcolor, (self.x, self.y, self.width, self.height))  # Рисуем полосу
        if board:  # Рисуем борт ползунка (если включено)
            pygame.draw.circle(win, self.secondcolor, (self.x + self.xslide * self.width,
                                                       (self.height / 2) + self.y), self.radius + board)
        # Рисуем ползунок
        pygame.draw.circle(win, self.maincolor, (self.x + self.xslide * self.width,
                                                 (self.height / 2) + self.y), self.radius)
        mass[1] = self.xslide  # Возвращаем состояние слайдера

    def CheckMouseInButton(self, positionMouse):  # Функция проверки положения мыши
        if self.x - self.radius <= positionMouse[0] - 290 <= self.x + self.width + self.radius:
            if self.y <= positionMouse[1] - 100<= self.y + self.height:
                return True
        return False

# Класс (библиотека) для создания булевых кнопок
class BoolButton:
    # Основные параметры класса
    def __init__(self, color, x, y, width, height, text = ''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, mass, thick = 2, sfont = 20, indent = 5):  # Функция отрисовки
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), thick)  # Рисуем борта кнопки
        font = pygame.font.Font('Font/Font.ttf', sfont)  # Подключаем шрифт
        text = font.render(self.text, True, self.color)  # Создаём надпись
        # Наложение текста справа от кнопки
        win.blit(text, (self.x + self.width + 5 + thick / 2, self.y + (self.height / 2) - sfont / 2))
        # Квадрат состояния кнопки (спавнится от центра, следовательно разрещается любая ширина бортов)
        indent_rect = ((self.x + self.width / 2) - ((self.width / 2) - indent - thick / 2),
                       (self.y + self.height / 2) - ((self.height / 2) - indent - thick / 2),
                       self.width - (indent * 2) - thick + 1, self.height - (indent * 2) - thick + 1)
        if mass[1] == 1:  # Рисуем кубик состояния
            pygame.draw.rect(win, self.color, indent_rect)

    @staticmethod
    def buttonActive(nameButton, positionMouse, mass, type=None):  # Функция активности кнопки
        # Комментарии лишние...
        if type:
            if nameButton.CheckMouseInButton(positionMouse) and mass[0] == 0:
                mass[0] = 1
        if not type:
            if nameButton.CheckMouseInButton(positionMouse) and mass[0] == 1:
                if mass[1] == 0:
                    mass[0], mass[1] = 0, 1
                else:
                    mass[0], mass[1] = 0, 0
            if not nameButton.CheckMouseInButton(positionMouse) and mass[0] == 1:
                mass[0] = 0
            elif mass[1] == 0:
                mass[0] = 0

    def CheckMouseInButton(self, positionMouse):  # Функция проверки положения мыши
        if self.x + 289 < positionMouse[0] < self.x + self.width + 289:
            if self.y + 100 < positionMouse[1] < self.y + self.height + 100:
                return True
        return False

# Класс (библиотека) для создания кнопок
class Button:
    # Основные параметры класса
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, ghost=None, sfont=None, y=None):  # Функция отрисовки
        if not sfont:  # Если размер шрифта не указан
            sfont = 40
        if ghost:  # Если тень включена
            # Рисуем тот же rect на y + 3 ниже
            Ghost = pygame.Rect((self.x, self.y + 3, self.width, self.height))
            pygame.draw.rect(win, ghost, Ghost, 0)
        pygame.draw.rect(win, self.color, (self.x, self.y + y, self.width, self.height), 0)  # Рисуем кнопку
        if self.text != '':  # Если имя кнопки введено
            font = pygame.font.Font('Font/Font.ttf', sfont)  # Подкллючаем шрифт
            text = font.render(self.text, 1, (0, 0, 0))  # Создаём надпись
            # Рисуем надпись посреди кнопки
            win.blit(text, (self.x + (self.width / 2 - text.get_width() / 2),
                            self.y + (self.height / 2 - text.get_height() / 2) + y))

    @staticmethod
    def buttonActive(nameButton, positionMouse, mass, type=None):  # Функция активности
        # Коментарии лишние...
        if not type:
            if nameButton.CheckMouseInButton(positionMouse):
                mass[0], mass[1] = 3, 1
        if type == 1:
            if nameButton.CheckMouseInButton(positionMouse) and mass[1] == 1:
                mass[0], mass[1] = 0, 0
                return True
            else:
                mass[0], mass[1] = 0, 0
        elif type == 2:
            if nameButton.CheckMouseInButton(positionMouse) and mass[1] == 1:
                if mass[2] == 0:
                    mass[1], mass[2] = 0, 1
                else:
                    mass[0], mass[1], mass[2] = 0, 0, 0
            elif mass[2] == 0:
                mass[0], mass[1] = 0, 0

    def CheckMouseInButton(self, positionMouse):  # Функция проверки положение мыши
        if self.x < positionMouse[0] < self.x + self.width:
            if self.y < positionMouse[1] < self.y + self.height:
                return True
        return False

    @staticmethod
    def ChangeColor(nameButton, positionMouse, mainColor, ChangedColor):  # Функция смены цвета, при наведении
        if nameButton.CheckMouseInButton(positionMouse):
            nameButton.color = ChangedColor
        else:
            nameButton.color = mainColor

# Функция меню
def Menu(music):
    global score_menu
    state_menu = OpenSetting()  # Открытие настроек
    op_score = True  # Контроль одноразового чтения настроек
    infoImage = pygame.image.load('Image/info.bmp')  # Загрузка картинки инструкции

    # Кнопки меню
    start_state = [0, 0, 0]
    startButton = Button(DARKORANGE, 50, 115, 203, 50, 'Старт')
    color_setting = DARKORANGE
    setting_state = [0, 0, 0, 0]
    settingButton = Button(color_setting, 50, 185, 203, 50, 'Настройки')
    color_record = DARKORANGE
    record_state = [0, 0, 0, 0]
    recordButton = Button(color_record, 50, 255, 203, 50, 'Рекорды')
    exit_state = [0, 0, 0]
    exitButton = Button(RED, 50, 560, 203, 50, 'Выход')

    #  Элементы настроек
    ghostBoolButton = BoolButton(DARKORANGE, 10, 10, 30, 30, 'Тень')
    ghost_bool_state = [0, 0]
    dropBoolButton = BoolButton(DARKORANGE, 10, 65, 30, 30, 'Сброс')
    drop_bool_state = [0, 0]
    gridBoolButton = BoolButton(DARKORANGE, 10, 120, 30, 30, 'Сетка')
    grid_bool_state = [0, 0]
    dificultBoolButton = BoolButton(DARKORANGE, 10, 175, 30, 30, 'Hard')
    dificult_bool_state = [0, 0]
    # Слайдер музыки
    volume_music = 0.5
    sliderMusic = Slider(DARKORANGE, BLACK, 20, 385, 200, 15, 12, volume_music)
    music_slider_state = [0, 0]
    # ImputBox
    text_input = named
    name_box_state = 0
    nameImputBox = ImputBox(DARKORANGE, RED, 10, 270, 220, 40, text_input, name_box_state)

    boot_score = False  # Открытие меню счёта
    boot_setting = False  # Открытие настроек
    # Проверка наличия настроек
    if state_menu:
        ghost_bool_state[1] = state_menu[0]  # Настройка тени
        if ghost_bool_state[1] == 1:
            ghost_bool_state[0] = 1
        drop_bool_state[1] = state_menu[1]  # Настройка дропа
        if drop_bool_state[1] == 1:
            drop_bool_state[0] = 1
        grid_bool_state[1] = state_menu[2]  # Настройка сетки
        if grid_bool_state[1] == 1:
            grid_bool_state[0] = 1
        dificult_bool_state[1] = state_menu[3]  # Настройка сложности
        if dificult_bool_state[1] == 1:
            dificult_bool_state[0] = 1
        sliderMusic.xslide = state_menu[4]  # Настройка громкости музыки
        state_menu.clear()  # Очистка массива настроек
    if music:
        pygame.mixer.music.play(loops=-1)  # Запуск музыки (цикл)
    # Цикл меню
    while True:
        volume_music = sliderMusic.xslide  # Выгрузка значений громкости в слайдер
        pygame.mixer.music.set_volume(volume_music)  # Изменение громкости
        menu.fill(BLACK)  # Очистка экрана меню
        setting_area.fill(BLACK)  # Очистка экрана настроек
        pygame.draw.lines(menu, DARKORANGE, True, boorders_menu, 5)  # Отрисовка линий меню
        # Отрисовка кнопок меню
        startButton.draw(menu, BLACKORANGE, 20, start_state[0])
        settingButton.draw(menu, BLACKORANGE, 20, setting_state[0])
        recordButton.draw(menu, BLACKORANGE, 20, record_state[0])
        exitButton.draw(menu, DARKRED, 20, exit_state[0])
        # Отрисовка поверхности настроек
        if not boot_setting and not boot_score:  # Отрисовка инструкции
            menu.blit(infoImage, (289, 100))
            menu.blit(font_label.render("Управление", True, DARKORANGE), (320, 60))

        if boot_setting:
            setting_area.fill(BLACK)  # Очистка поверхности настроек
            menu.blit(font_label.render("Настройки", True, DARKORANGE), (330, 60))  # Добавление надписи на поверхность
            # Отрисовка прямоугольников компонентов настроек
            for i_set in range(4):
                pygame.draw.rect(setting_area, GRAY, settingMasRect[i_set])  # Прямоугольники булевых внопок
                if i_set < 2:
                    pygame.draw.rect(setting_area, GRAY, settingMasBigRect[i_set])  # Прямоугольник музыки и ImputBox'а
            setting_area.blit(font_label.render("Музыка", True, DARKORANGE), (65, 345))  # Добавление надписи слайдера
            sliderMusic.draw(setting_area, music_slider_state, sliderMusic, 4)  # Отрисовка слайдера
            nameImputBox.draw(setting_area, 20, 3)  # Отрисовка ImputBox'а
            text_input = nameImputBox.text  # Выгрузка ника из класса
            setting_area.blit(font_label.render("Игровой   ник", True, DARKORANGE), (27, 235))  # Добавление надписи настроек
            # Отрисовка булевых кнопок
            ghostBoolButton.draw(setting_area, ghost_bool_state, 2, 20, 5)
            dropBoolButton.draw(setting_area, drop_bool_state, 2, 20, 5)
            gridBoolButton.draw(setting_area, grid_bool_state, 2, 20, 5)
            dificultBoolButton.draw(setting_area, dificult_bool_state, 2, 20, 5)
            # Наложение поверхности настроек на поверхность меню
            menu.blit(setting_area, (289, 100))
        Titles(False)  # Отрисовка надписи "Tetris" на экране меню
        score_menu = RecordList(op_score, boot_score)  # Загрузка лучшего счёта
        if not score_menu:
            score_menu = 0  # Если рекорда нет, то присваивается 0
        op_score = False  # Отключаем чтение настроек
        # Блок кнопок (настройки/рекорды)
        # Кнопки переключаются и меняют цвет
        if setting_state[2] == 0:
            boot_setting = False
            settingButton.color = color_setting
        if record_state[2] == 0:
            boot_score = False
            recordButton.color = color_record
        # Блок проверки действий пользователя
        for event_run in pygame.event.get():
            pos = pygame.mouse.get_pos()  # Получаем положение мыши в переменную
            # Действие на кнопку закрытия (окно)
            if event_run.type == pygame.QUIT:
                # Загрузка настроек в массив
                state_menu.append(ghost_bool_state[1])
                state_menu.append(drop_bool_state[1])
                state_menu.append(grid_bool_state[1])
                state_menu.append(dificult_bool_state[1])
                state_menu.append(volume_music)
                SaveSetting(state_menu)  # Сохраняем массив в файл
                pygame.quit()
                exit()
            # Действия на нажатие кнопки мыши
            if event_run.type == pygame.MOUSEBUTTONDOWN:
                # Проверка активности кнопок меню
                startButton.buttonActive(startButton, pos, start_state)
                settingButton.buttonActive(settingButton, pos, setting_state)
                recordButton.buttonActive(recordButton, pos, record_state)
                exitButton.buttonActive(exitButton, pos, exit_state)
                # Блок проверки активности на поверхности настроек
                if boot_setting:
                    # Проверка активности булевых кнопок настроек
                    ghostBoolButton.buttonActive(ghostBoolButton, pos, ghost_bool_state, True)
                    dropBoolButton.buttonActive(dropBoolButton, pos, drop_bool_state, True)
                    gridBoolButton.buttonActive(gridBoolButton, pos, grid_bool_state, True)
                    dificultBoolButton.buttonActive(dificultBoolButton, pos, dificult_bool_state, True)
                    # Проверка активности слайдера
                    if sliderMusic.CheckMouseInButton(pos):
                        music_slider_state[0] = 1
                    # Проверка активности ImputBox'а
                    if nameImputBox.mass == 1:
                        nameImputBox.mass = 0
                    if nameImputBox.CheckMouseInButton(pos):
                        nameImputBox.mass = 1
            # Действия на отжатие кнопки мыши
            if event_run.type == pygame.MOUSEBUTTONUP:
                # Действия на кнопкку "Старт"
                if startButton.buttonActive(startButton, pos, start_state, 1):
                    # Загрузка настроек в массив
                    state_menu.append(ghost_bool_state[1])
                    state_menu.append(drop_bool_state[1])
                    state_menu.append(grid_bool_state[1])
                    state_menu.append(dificult_bool_state[1])
                    state_menu.append(volume_music)
                    state_menu.append(int(score_menu))
                    if len(text_input) > 0:  # Защита от отсутствия ника
                        state_menu.append(text_input)
                    else:
                        state_menu.append('Guest')
                    SaveSetting(state_menu)  # Сохранение настроек
                    pygame.time.wait(200)  # Задержка
                    return state_menu  # Возвращаем массив с настройками в основной цикл игры
                # Действия кнопки "Настройки"
                settingButton.buttonActive(settingButton, pos, setting_state, 2)
                if setting_state[2] == 1:
                    boot_setting = True  # Запуск меню
                    if setting_state[3] == 0:
                        # Обнуление значений кнопки "Рекорды"
                        record_state[0], record_state[1], record_state[2] = 0, 0, 0
                        setting_state[3] = 1
                    record_state[3] = 0
                    settingButton.color = DARKOBLACKORANGE  # Изменение цвета кнопки
                # Действия кнопки "Рекорды"
                recordButton.buttonActive(recordButton, pos, record_state, 2)
                if record_state[2] == 1:
                    boot_score = True  # Запуск рекордов
                    if record_state[3] == 0:
                        # Обнуление значений кнопки "Настройки"
                        setting_state[0], setting_state[1], setting_state[2] = 0, 0, 0
                        record_state[3] = 1
                    setting_state[3] = 0
                    recordButton.color = DARKOBLACKORANGE  # Изменение цвета кнопки
                # Действия кнопки "Выход"
                if exitButton.buttonActive(exitButton, pos, exit_state, 1):
                    # Сохранение настроек
                    state_menu.append(ghost_bool_state[1])
                    state_menu.append(drop_bool_state[1])
                    state_menu.append(grid_bool_state[1])
                    state_menu.append(dificult_bool_state[1])
                    state_menu.append(volume_music)
                    SaveSetting(state_menu)
                    pygame.quit()
                    exit()
                # Действия на открытой поверхности настроек
                if boot_setting:
                    # Обработка булевых кнопок
                    ghostBoolButton.buttonActive(ghostBoolButton, pos, ghost_bool_state, False)
                    dropBoolButton.buttonActive(dropBoolButton, pos, drop_bool_state, False)
                    gridBoolButton.buttonActive(gridBoolButton, pos, grid_bool_state, False)
                    dificultBoolButton.buttonActive(dificultBoolButton, pos, dificult_bool_state, False)
                    # Опустошение активности слайдера
                    music_slider_state[0] = 0
            # Действие на нажатие кнопок
            if event_run.type == pygame.KEYDOWN:
                nameImputBox.imput(event_run)  # Обработка кнопок для текстового поля
        main_win.blit(menu, (0, 0))  # Наложение поверхности меню на главное окно
        pygame.display.flip()  # Переворот окна для отрисовки "заранее"
        clock.tick(FPS)  # Частота отрисовки

# Функция меню проигрыша
def LoseMenu(score_end, name):
    read_position_mas = openScore()  # Загрузка списка рекордов
    # Кнопки поверхности
    restartButton = Button(DARKORANGE, 40, 507, 495, 50, 'Заново')
    restart_state = [0, 0, 0]
    exitButton = Button(RED, 293, 567, 242, 50, 'Выйти')
    exit_state = [0, 0, 0]
    menuButton = Button(DARKORANGE, 40, 567, 242, 50, 'Меню')
    menu_state = [0, 0, 0]
    end = True  # Запуск основного цикла проигрыша
    # Цикл поиска позиции игрока в списке
    while True:
        name_position = read_position_mas[0].index(name)
        score_position = read_position_mas[1].index(score_end)
        if score_position == name_position:
            break
        elif name_position < score_position:
            read_position_mas[0].insert(name_position, " ")
        elif name_position > score_position:
            read_position_mas[1].insert(score_position, " ")
    # Основной цикл
    while end:
        lose_menu_area.fill(BLACK)  # Очистка поверхности
        # Отрисовка интерфейса (надписи/линии)
        pygame.draw.lines(lose_menu_area, DARKORANGE, True, boorders_lose_menu, 5)
        lose_menu_area.blit(font_tetris.render("Игра   окончена", True, DARKORANGE), (55, 50))
        score_str = font_end.render("Очки:   " + str(score_end), True, DARKORANGE)
        pos_str = font_end.render("Вы   заняли   " + str(name_position + 1) + "   место", True, DARKORANGE)
        lose_menu_area.blit(score_str, ((InfoWSize[0] - score_str.get_width()) / 2, 120))
        lose_menu_area.blit(pos_str, ((InfoWSize[0] - pos_str.get_width()) / 2, 170))
        # Отрисовка кнопок
        restartButton.draw(lose_menu_area, BLACKORANGE, 30, restart_state[0])
        exitButton.draw(lose_menu_area, DARKRED, 30, exit_state[0])
        menuButton.draw(lose_menu_area, BLACKORANGE, 30, menu_state[0])
        # Цикл отработки активностей
        for event_end in pygame.event.get():
            pos = pygame.mouse.get_pos()  # Получение позиции мыши
            if event_end.type == pygame.QUIT:  # Выход
                pygame.quit()
                quit()
            if event_end.type == pygame.MOUSEBUTTONDOWN:  # Нажатие кнопок мыши
                # Проверка нажатий кнопок
                restartButton.buttonActive(restartButton, pos, restart_state)
                exitButton.buttonActive(exitButton, pos, exit_state)
                menuButton.buttonActive(menuButton, pos, menu_state)
            if event_end.type == pygame.MOUSEBUTTONUP:  # Отжатие кнопок мыши
                # Отработка нажатий кнопок
                if restartButton.buttonActive(restartButton, pos, restart_state, 1):
                    end = False
                    break
                if exitButton.buttonActive(exitButton, pos, exit_state, 1):
                    pygame.quit()
                    exit()
                if menuButton.buttonActive(menuButton, pos, menu_state, 1):
                    return True
        main_win.blit(lose_menu_area, (0, 0))  # Наложение поверхности
        pygame.display.flip()
        clock.tick(FPS)

# Функция сортировки файла с рекордами
def RecordSorted(bool_val):
    scoreval = openScore()  # Чтение файла
    if scoreval:
        # Получение копий счета и имени
        scorelist = deepcopy(scoreval[1])
        namelist = deepcopy(scoreval[0])
        lenMaslist = len(scorelist)  # Находим кол-во рекордов
        indexscoresave = sorted(scorelist, reverse=True)  # Реверсивная сортировка массива счёта
        indexnamesave = []  # Масссив для имён
        masses_out = []  # Массив для возврата
        for i in range(lenMaslist):  # Цикл идексации и замены имён в массиве
            index = scorelist.index(indexscoresave[i])  # Находим индекс нового счёта в старом массиве
            indexnamesave.append(namelist[index])  # Добавление в новый массив имени найденого индеком
            scorelist.pop(index)  # Удаляем значение в массиве в ячейке индекса
            scorelist.insert(index, str(0))  # Подменяем име в массиве нулём
        saveScore(indexnamesave, indexscoresave, lenMaslist, 'w')  # Сохраняем отсортированные массивы
        # Возврат массивов
        if bool_val:
            masses_out.append(indexnamesave)
            masses_out.append(indexscoresave)
            masses_out.append(lenMaslist)
            return masses_out
    else:
        return False  # Возврат False если рекордов нет

# Функция создания меню рекордов
def RecordList(op_score, bool_hide):
    global len_list, indexname, indexscore, mass_record
    # Отображение надписи на поверхности
    if bool_hide:
        menu.blit(font_label.render("Рекорды", True, DARKORANGE), (350, 60))
    # Открытие счёта
    if op_score:
        mass_record = RecordSorted(True)  # Получаем сортированный список рекордов
        if mass_record:
            indexname = mass_record[0]
            indexscore = mass_record[1]
            len_record = mass_record[2]
            # Считаем кол-во рекордов
            if len_record > RecordValue:
                len_list = RecordValue
            else:
                len_list = len_record
    if mass_record:
        # Наложение поверхности на меню
        if bool_hide:
            menu.blit(record_area, (289, 105))
        record_area.fill(BLACK)  # Очищаем поверхность
        # Создаём прямоугольники равные кол-ву рекордов
        for i in range(len_list):
            if len(indexname[i]) > 7:  # Выводим всего 7 символов ника
                timed_index = indexname[i]
                indexname[i] = timed_index[0:7:1] + "*"
            # Рисуем квадраты
            pygame.draw.rect(record_area, GRAY, recordMasNameRect[i])
            pygame.draw.rect(record_area, GRAY, recordMasScoreRect[i])
            record_area.blit(font_score.render(indexname[i], True, DARKORANGE),
                             (7, recordMasNameRect[i].y + (HieghtRecord / 2) - 10))
            record_area.blit(font_score.render(str(indexscore[i]), True, DARKORANGE),
                             (130, recordMasNameRect[i].y + (HieghtRecord / 2) - 10))
        return indexscore[0]  # Возвращаем лучший рекорд
    # Если список пуст
    else:
        record_area.fill(GRAY)
        record_area.blit(font_label.render("Список   пуст", True, DARKORANGE), (27, (RecordWSize[1] / 2) - 10))
        if bool_hide:
            menu.blit(record_area, (289, 100))
        return False

# Функция сохранения счёта
def saveScore(nm, scr, ln, form_file):
    # Выгружаем массивы данных
    masscore = deepcopy(scr)
    masname = deepcopy(nm)
    with open('Score.txt', form_file) as file:
        for i_save in range(ln):
            file.write(str(len(str(len(masname[i_save])))))  # Считаем длинну длинны ника
            file.write(str(len(masname[i_save])))  # Считаем длинну ника
            file.write(masname[i_save])  # Записываем ник
            file.write(str(len(str(masscore[i_save]))))  # Считаем длинну счёта
            file.write(str(masscore[i_save]) + '\n')  # Записываем счёт с Enter

# Функция открытия счёта
def openScore():
    # Пееременные для будущей загрузки данных
    namein = []
    scorein = []
    try:
        with open('Score.txt') as file:
            # Подсчёт кол-ва строк в файле
            len_open_file = len(re.findall(r"[\n']+", open('Score.txt').read()))
            if len_open_file == 0:
                return False  # Если файл пустой
            for i_len in range(len_open_file):  # Читаем данные
                while True:
                    n_n_time = file.read(1)
                    if not n_n_time == '\n':  # Защита от enter'ов
                        n = int(n_n_time)
                        break
                # Считаем данные
                n_time = int(file.read(n))
                namein.append(file.read(n_time))
                n = int(file.read(1))
                scorein.append(int(file.read(n)))
            return [namein, scorein]  # Возвращаем массивы с данными
    except FileNotFoundError:  # Если файла нет, то создаём
        with open('Score.txt', 'w') as file:
            file.write("")

# Сохранение настроек
def SaveSetting(setting):
    with open('Setting', 'w') as sett:
        for linesa in range(5):
            sett.write(str(len(str(setting[linesa]))))  # Сохранение длинны значения
            sett.write(str(setting[linesa]) + '\n')  # Сохранение значения

# Открытие настроек
def OpenSetting():
    setting = []  # Для выгрузки в будущем настроек
    try:
        with open('Setting') as sett:
            for lineop in range(5):
                setting.append(float(sett.read(int(sett.read(1)))))  # Читаем настройку
                sett.read(1)  # Убираем перенос строки
    except FileNotFoundError:  # Если файла нет, возвращаем пустой массив
        return setting
    return setting  # Возвращаем массив с настройками

# Функция проверки фигуры в пределах поля
def Borders(figurebord):
    # Проверка по оси x
    if figurebord[i].x < 0 or figurebord[i].x > rows - 1:
        return False
    # Проверка по оси y (достижение дна)
    elif figurebord[i].y > columns - 1 or zeroMas[figurebord[i].y][figurebord[i].x]:
        return False
    return True

# Функция отрисовки следующей фигуры
def DrawNextPocketFigure(index, frg, area, color):
    for i_next in range(4):
        # Условия для разных фигур для центровки их в окне
        if index == 0:
            one_rect_figure.x = frg[i_next].x * size_block - 73
            one_rect_figure.y = frg[i_next].y * size_block + 45
        elif index == 4:
            one_rect_figure.x = frg[i_next].x * size_block - 100
            one_rect_figure.y = frg[i_next].y * size_block + 32
        elif index == 2:
            one_rect_figure.x = frg[i_next].x * size_block - 70
            one_rect_figure.y = frg[i_next].y * size_block + 30
        elif index == 1:
            one_rect_figure.x = frg[i_next].x * size_block - 74
            one_rect_figure.y = frg[i_next].y * size_block + 30
        else:
            one_rect_figure.x = frg[i_next].x * size_block - 75
            one_rect_figure.y = frg[i_next].y * size_block + 30
        # Рисуем
        pygame.draw.rect(area, figures_color[figures.index(color)], one_rect_figure)

# Функция отрисовки фигуры
def DrawFigure(figureGostMain, type):
    for i_draw in range(4):
        one_rect_figure.x = figureGostMain[i_draw].x * size_block + 1
        one_rect_figure.y = figureGostMain[i_draw].y * size_block + 1
        if type:
            # Если тень активирована, то рисуем
            pygame.draw.rect(game_area, figures_color[figures.index(colorType)], one_rect_figure)
        if not type:
            pygame.draw.rect(game_area, DARKGRAY, one_rect_figure)  # Рисуем фигуру

# Функция отрисовки надписей
def Titles(var):
    if var:  # Для игрового окна
        main_win.blit(font_tetris.render('TETRIS', True, DARKORANGE), (343, 30))
        main_win.blit(font_label.render('Next  figure', True, DARKORANGE), (370, 260))
        main_win.blit(font_label.render('Score:  ' + str(score), True, DARKORANGE), (350, 610))
        main_win.blit(font_label.render('High  score:', True, DARKORANGE), (350, 550))
        main_win.blit(font_label.render(str(high_score), True, DARKORANGE), (350, 580))
        main_win.blit(font_label.render('Pocket', True, DARKORANGE), (400, 460))
        main_win.blit(font_label.render('Lines:  ' + str(lines_score), True, DARKORANGE), (350, 520))
    elif not var:  # Для меню
        menu.blit(font_tetris.render('TETRIS', True, DARKORANGE), (30, 30))

# Основной цикл игры
while True:
    rotate = False  # Активация поворота
    change = False  # Активация кармана
    pause = [0, 1]  # Параметры паузы
    move_x = 0  # Парамент перемещения по оси x
    # Вызов меню игры
    if menu_run:
        if music_run:  # Для однократного запуска музыки
            state = Menu(True)
            music_run = False
        else:
            state = Menu(False)
        high_score = state[5]  # Выгрузка лучшего счёта
        named = state[6]  # Выгрузка nickname'а
        menu_run = False  # Отключение запуска меню
    # Заполнение поверхностей и наложение на основное окно
    main_win.fill(BLACK)
    main_win.blit(game_area, (30, 30))
    main_win.blit(next_area, (DistanceRightArea, 100))
    main_win.blit(pocket_area, (DistanceRightArea, 300))
    pocket_area.fill(BLACK)
    game_area.fill(BLACK)
    next_area.fill(BLACK)
    # Добавление информативного текста на экран
    Titles(True)
    # Задержка удаления строк
    if lines > 0:
        pygame.time.wait(100)
    # Обработка нажатий клавиш клавиатуры и окна
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        # Обработка нажатий клавищ
        if event.type == pygame.KEYDOWN:
            # Перемещение влево
            if event.key == pygame.K_LEFT:
                move[0] = 1
                move_x -= 1
            # Перемещение вправо
            if event.key == pygame.K_RIGHT:
                move[0] = 2
                move_x = 1
            # Ускоренное падение фигуры
            if event.key == pygame.K_DOWN:
                if state[1] == 1:
                    MaxSpeed = 50  # Моментальный сброс
                else:
                    drop = True  # Падение по 1 блоку
            # Поворот фигуры
            if event.key == pygame.K_UP:
                rotate = True
            # Активация кармана
            if event.key == pygame.K_RSHIFT:
                change = True
            # Активация паузы
            if event.key == pygame.K_ESCAPE:
                pause[0] = 1
        # Отжатие клавиш клавиатуры
        if event.type == pygame.KEYUP:
            # Очистка массивов перемещения
            if event.key == pygame.K_LEFT:
                move[0], move[1]= 0, 0
            if event.key == pygame.K_RIGHT:
                move[0], move[1]= 0, 0
    # Цикл паузы
    while pause[0]:
        for event_pause in pygame.event.get():
            # Возможность закрыть игру
            if event_pause.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Обработка отключения паузы
            if event_pause.type == pygame.KEYDOWN:
                if event_pause.key == pygame.K_ESCAPE:
                    pause[0] = 0
        # Разовая отрисовка интерфейса
        if pause[1]:
            pause_area.fill((0, 0, 0, 200))  # (*, *, *, VAL) - VAL - Значение прозрачности
            text_pause = font_tetris.render("ПАУЗА", True, DARKORANGE)
            # Размещение текста по центру
            pause_area.blit(text_pause, (InfoWSize[0] / 2 - text_pause.get_width() / 2,
                                         InfoWSize[1] / 2 - text_pause.get_height() / 2))
            main_win.blit(pause_area, (0, 0))
            pause[1] = 0
        pygame.display.flip()
    #  Быстрое перемещение при зажатой кнопке
    # Быстрое перемещение включится после 0.66 сек (FPS / 40) FPS = 60
    if move[0] == 1:
        move[1] += 1  # Включаем таймер
        if move[1] >= 40:
            move_x = -1
    elif move[0] == 2:
        move[1] += 1  # Включаем таймер
        if move[1] >= 40:
            move_x = 1
    # Движение по x и ограничение
    save_figure = deepcopy(figure)  # Делаем копию фигуры
    for i in range(4):
        figure[i].x += move_x  # Перемещаем пока можно
        if not Borders(figure):  # Если вышли за предел
            figure = deepcopy(save_figure)  # Загружаем копию
            break
    # Падение фигруы (1 клетка за нажатие)
    if state[1] == 0 and drop:
        save_figure = deepcopy(figure)  # Копия фигуры
        for i_drop in range(4):
            figure[i_drop].y += 1  # Перемещать на 1 клетку вниз
            drop = False  # Выключаем дроп
            # Проверяем пересечения фигуры с фигурами/бортами
            if figure[i_drop].y > columns - 1 or zeroMas[figure[i_drop].y][figure[i_drop].x]:
                figure = deepcopy(save_figure)  # Иначе загружаем копию
                break
    # Движение по y и ограничение
    ZeroPosY += Speed  # "Таймер" падения фигуры
    if ZeroPosY > MaxSpeed:
        ZeroPosY = 0  # Обнуляем "таймер"
        save_figure = deepcopy(figure)  # Делаем копию фигуры
        for i in range(4):
            figure[i].y += 1  # Перемещение фигуры на 1 блок вниз
            if not Borders(figure):
                for j in range(4):
                    # Перенос цветов фигуры в массив состояния
                    zeroMas[save_figure[j].y][save_figure[j].x] = figures_color[figures.index(colorType)]
                colorType = deepcopy(colorTypeNext)  # Копируем индекс из следующей фигуры
                figure = deepcopy(next_figure)  # Копируем фигуру из следующей
                colorTypeNext = choice(figures)  # Случайно выбираем индекс для следующей фигуры
                next_figure = deepcopy(colorTypeNext)  # Создаём фигуру
                figure_index = figures.index(colorTypeNext)  # Находим фигуру в списке
                buffer = deepcopy(figure)  # Сохраняем в буффер фигуру
                score_pocket = 1  # Активация возможности использовать карман
                shadow_figure = deepcopy(figure)  # Копируем фигуру для тени
                score += 2  # Добавляем очки за падение
                MaxSpeed = 1000  # Возвращаем максимальную скорость
                break
    # Поворот фигуры
    center_rotate = figure[0]  # Получаем центр вращения из первой координаты фигуры
    save_figure = deepcopy(figure)  # Делаем копию фигуры
    if rotate:
        for i in range(4):
            # Вычитаем из координаты фигуры центр вращения
            x = figure[i].y - center_rotate.y
            y = figure[i].x - center_rotate.x
            # Вычитаем и прибавляем x и y к центрам вращения
            figure[i].x = center_rotate.x - x
            figure[i].y = center_rotate.y + y
            if not Borders(figure):  # Если фигуры после разворота выходит за края или входит в фигуру
                figure = deepcopy(save_figure)  # Возвращаем копию
                break
    # Алгоритм замены фигур и внесения новой (карман)
    while change:
        if score_pocket == 1:  # Запрет на замену более 1 раза до падения
            if not pocket:  # Если карман не заполнен
                score_pocket = 0  # Запрещаем замену
                color_pocket = colorType  # Переносим индексацию
                pocket = deepcopy(color_pocket)  # Делае грубокую копию индекса в фигуру
                # Выгружаем следующую фигуру в активное поле
                colorType = deepcopy(colorTypeNext)
                figure = deepcopy(colorType)
                # Создание новой случайной фигуры
                colorTypeNext = choice(figures)
                next_figure = deepcopy(colorTypeNext)
                pocket_index = figures.index(color_pocket)
            else:  # Если карман имеется
                score_pocket = 0  # Делаем запрет
                buffer1 = deepcopy(pocket)  # Копируем в буффер карман
                figure, pocket = deepcopy(pocket), deepcopy(buffer)  # Обмениваем фигуры
                colorType, color_pocket = color_pocket, colorType  # Обмениваем цвета
                buffer = deepcopy(figure)  # Заносим фигуру в буфер
                pocket_index = figures.index(color_pocket)  # Находим индекс кармана
        change = False  # Выключаем карман
    # Проверка линий
    line = columns - 1  # 19 из 20 линий (20я проверяется на проигрыш)
    lines = 0  # Кол-во срезанных линий за раз
    for value in range(columns - 1, -1, -1):
        const = 0  # Счётчик квадратов в одной строке
        for i_check in range(rows):
            if zeroMas[value][i_check]:
                const += 1  # Если квадрат обнаружен - увеличиваем значение счётчика
            zeroMas[line][i_check] = zeroMas[value][i_check]
        if const < rows:  # Если линия не заполнена, спускаемся на 1 вниз
            line -= 1
        else:  # Иначе:
            if state[3] == 1:  # Увеличиваем скорость (если включено)
                Speed += 1
            lines += 1  # Увеличиваем счётик линий среза
            lines_score += 1  # Постоянный счётчик срезанных линий
    # Начисление счёта
    score += scores[lines]
    # Рисуем сетку
    if state[2] == 1:
        [pygame.draw.rect(game_area, GRAY, i_grid, 1) for i_grid in grid]
    # Добавляем эффект гостинга фигуры
    if state[0] == 1:
        active_shadow = True
        for i_move in range(4):  # Перемещаем тень на место основной фигуры
            shadow_figure[i_move].y = figure[i_move].y
            shadow_figure[i_move].x = figure[i_move].x
        break_shadow_figure = True  # Переменная остановки тени
        while break_shadow_figure:  # Цикл "дропа" тени
            backup_shadow = deepcopy(shadow_figure)  # Глубокая копия тени
            for i in range(4):  # Сохраняем положение тени по оси x от основной и спускаем вниз
                shadow_figure[i].x = figure[i].x
                shadow_figure[i].y += 1
                if not Borders(shadow_figure):  # Загружаем копию, если фигура вышла за поля игры/фигур и отключаем
                    shadow_figure = deepcopy(backup_shadow)
                    break_shadow_figure = False
                    break
        # Отключение тени фигур при достижении её
        for i in range(4):
            for j in range(4):
                if shadow_figure[i].y != figure[j].y:  # Сравниваем координаты всех квадратов фигур
                    active_shadow = True  # Включаем тень
                else:
                    active_shadow = False  # Отключаем тень
                    break
        if active_shadow:
            DrawFigure(shadow_figure, False)  # Рисуем тень
    # Рисуем фигуру
    DrawFigure(figure, True)
    # Отрисовка матрицы с состоянием игрового поля (наличия фигур в клетках)
    for y, row in enumerate(zeroMas):
        for x, column in enumerate(row):
            if column:
                one_rect_figure.x = x * size_block + 1
                one_rect_figure.y = y * size_block + 1
                pygame.draw.rect(game_area, column, one_rect_figure)
    # Рисуем рамки белого цвета
    pygame.draw.lines(game_area, WHITE, True, boorders_rect, 5)
    pygame.draw.lines(next_area, WHITE, True, boorders_next_rect, 5)
    pygame.draw.lines(pocket_area, WHITE, True, boorders_next_rect, 5)
    # Рисуем следущую фигуру
    DrawNextPocketFigure(figure_index, next_figure, next_area, colorTypeNext)
    # Рисуем карман
    if pocket:  # Если карман не пустой
        DrawNextPocketFigure(pocket_index, pocket, pocket_area, color_pocket)
    # Обработка проигрыша
    for i in range(rows):
        if zeroMas[0][i]:  # Проверка 20го ряда
            # Ели найден объект
            saveScore([named], [score - 2], 1, 'a')  # Сохранение счёта
            RecordSorted(False)  # Сортируем файл с рекордами
            zeroMas = [[0 for x in range(rows)] for y in range(columns)]  # Очистка массива элементов полял
            if score > high_score:  # Подмена лучшего счёта
                high_score = score - 2
            Speed = SpeedMain  # Возврат скорости в исходное значение (если был включен режим hard)
            lines_score = 0  # Обнуляем кол-во срезанных линий
            score_pocket = 1  # Активируем карман
            pocket.clear()  # Очищаем карман
            for i_grid in grid:
                pygame.draw.rect(game_area, choice(figures_color), i_grid)  # Заполнение поля случайными цветами
                # Рисуем интерфейс
                pygame.draw.lines(game_area, WHITE, True, boorders_rect, 5)
                main_win.blit(game_area, (30, 30))
                pygame.display.flip()
                clock.tick(200)
            menu_run = LoseMenu(score - 2, named)  # Вызываем меню проигрыша
            score = 0  # Очищаем счёт
            if not menu_run:  # Если нажата кнопка "заново" в меню проигрыша
                # Обновление компонентов экрана
                main_win.fill(BLACK)
                main_win.blit(game_area, (30, 30))
                main_win.blit(next_area, (DistanceRightArea, 100))
                main_win.blit(pocket_area, (DistanceRightArea, 300))
                pocket_area.fill(BLACK)
                next_area.fill(BLACK)
                Titles(True)
                # Стераем постепенно нарисованные квадраты и начинаем заново
                for i_grid in grid:
                    pygame.draw.rect(game_area, BLACK, i_grid)
                    pygame.draw.rect(game_area, GRAY, i_grid, 1)
                    pygame.draw.lines(game_area, WHITE, True, boorders_rect, 5)
                    main_win.blit(game_area, (30, 30))
                    pygame.display.flip()
                    clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)
