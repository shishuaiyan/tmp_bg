# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import math

# 画笔类。负责管理加载画笔笔刷，调整画笔颜色、大小以及画笔绘制的工作。
class Brush:
    def __init__(self, screen):
        self.screen = screen
        self.color = (0, 0, 0)
        self.size = 1
        self.drawing = False
        self.last_pos = None
        self.style = True
        self.brush = pygame.image.load("images/brush.png").convert_alpha()
        self.brush_now = self.brush.subsurface((0, 0), (1, 1))

    def start_draw(self, pos):
        # 开始绘制，并记录当前坐标
        self.drawing = True
        self.last_pos = pos

    def end_draw(self):
        # 结束绘制
        self.drawing = False

    def set_brush_style(self, style):
        # 设置笔刷的样式
        print("* set brush style to", style)
        self.style = style

    def get_brush_style(self):
        # 获取笔刷的类型
        return self.style

    def get_current_brush(self):
        # 获取当前笔刷
        return self.brush_now

    def set_size(self, size):
        # 设置笔刷大小
        if size < 1:
            size = 1
        elif size > 32:
            size = 32
        print("* set brush size to", size)
        self.size = size
        self.brush_now = self.brush.subsurface((0, 0), (size*2, size*2))

    def get_size(self):
        # 获取笔刷大小
        return self.size

    def set_color(self, color):
        # 设置笔刷大小
        self.color = color
        for i in range(self.brush.get_width()):
            for j in range(self.brush.get_height()):
                self.brush.set_at((i, j),
                                  color + (self.brush.get_at((i, j)).a,))

    def get_color(self):
        # 获取笔刷大小
        return self.color

    # 绘制
    def draw(self, pos):
        if self.drawing:
            for p in self._get_points(pos):
                if self.style:
                    self.screen.blit(self.brush_now, p)
                else:
                    pygame.draw.circle(self.screen, self.color, p, self.size)
            self.last_pos = pos

    # 获取前一个点与当前点之间的所有需要绘制的点
    def _get_points(self, pos):
        points = [(self.last_pos[0], self.last_pos[1])]
        len_x = pos[0] - self.last_pos[0]
        len_y = pos[1] - self.last_pos[1]
        length = math.sqrt(len_x ** 2 + len_y ** 2)
        step_x = len_x / length
        step_y = len_y / length
        for i in range(int(length)):
            points.append((points[-1][0] + step_x, points[-1][1] + step_y))
        # 对 points 中的点坐标进行四舍五入取整
        points = map(lambda x: (int(0.5 + x[0]), int(0.5 + x[1])), points)
        # 去除坐标相同的点
        return list(set(points))


# 菜单类。负责管理和绘制菜单。菜单的功能包括允许切换画笔，调整画笔大小和选择画笔颜色。
class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.brush = None
        # 画板预定义的颜色值
        self.colors = [
            (0xff, 0x00, 0xff), (0x80, 0x00, 0x80),
            (0x00, 0x00, 0xff), (0x00, 0x00, 0x80),
            (0x00, 0xff, 0xff), (0x00, 0x80, 0x80),
            (0x00, 0xff, 0x00), (0x00, 0x80, 0x00),
            (0xff, 0xff, 0x00), (0x80, 0x80, 0x00),
            (0xff, 0x00, 0x00), (0x80, 0x00, 0x00),
            (0xc0, 0xc0, 0xc0), (0xff, 0xff, 0xff),
            (0x00, 0x00, 0x00), (0x80, 0x80, 0x80),
        ]
        # 计算每个色块在画板中的坐标值，便于绘制
        self.colors_rect = []
        for (i, rgb) in enumerate(self.colors):
            rect = pygame.Rect(10 + i % 2 * 32, 254 + i / 2 * 32, 32, 32)
            self.colors_rect.append(rect)
        # 两种笔刷的按钮图标
        self.pens = [
            pygame.image.load("images/pen1.png").convert_alpha(),
            pygame.image.load("images/pen2.png").convert_alpha(),
        ]
        # 计算坐标，便于绘制
        self.pens_rect = []
        for (i, img) in enumerate(self.pens):
            rect = pygame.Rect(10, 10 + i * 64, 64, 64)
            self.pens_rect.append(rect)

        # 调整笔刷大小的按钮图标
        self.sizes = [
            pygame.image.load("images/big.png").convert_alpha(),
            pygame.image.load("images/small.png").convert_alpha()
        ]
        # 计算坐标，便于绘制
        self.sizes_rect = []
        for (i, img) in enumerate(self.sizes):
            rect = pygame.Rect(10 + i * 32, 138, 32, 32)
            self.sizes_rect.append(rect)

    def set_brush(self, brush):
        self.brush = brush

    # 绘制菜单栏
    def draw(self):
        # 绘制画笔样式按钮
        for (i, img) in enumerate(self.pens):
            self.screen.blit(img, self.pens_rect[i].topleft)
        # 绘制 + - 按钮
        for (i, img) in enumerate(self.sizes):
            self.screen.blit(img, self.sizes_rect[i].topleft)
        # 绘制用于实时展示笔刷的小窗口
        self.screen.fill((255, 255, 255), (10, 180, 64, 64))
        pygame.draw.rect(self.screen, (0, 0, 0), (10, 180, 64, 64), 1)
        size = self.brush.get_size()
        x = 10 + 32
        y = 180 + 32
        # 如果当前画笔为 png 笔刷，则在窗口中展示笔刷
        # 如果为铅笔，则在窗口中绘制原点
        if self.brush.get_brush_style():
            x = x - size
            y = y - size
            self.screen.blit(self.brush.get_current_brush(), (x, y))
        else:
            # BUG
            pygame.draw.circle(self.screen,
                               self.brush.get_color(), (x, y), size)
        # 绘制色块
        for (i, rgb) in enumerate(self.colors):
            pygame.draw.rect(self.screen, rgb, self.colors_rect[i])

    # 定义菜单按钮的点击响应
    def click_button(self, pos):
        # 笔刷
        for (i, rect) in enumerate(self.pens_rect):
            if rect.collidepoint(pos):
                self.brush.set_brush_style(bool(i))
                return True
        # 笔刷大小
        for (i, rect) in enumerate(self.sizes_rect):
            if rect.collidepoint(pos):
                # 画笔大小的每次改变量为 1
                if i:
                    self.brush.set_size(self.brush.get_size() - 1)
                else:
                    self.brush.set_size(self.brush.get_size() + 1)
                return True
        # 颜色
        for (i, rect) in enumerate(self.colors_rect):
            if rect.collidepoint(pos):
                self.brush.set_color(self.colors[i])
                return True
        return False


# 画板类。是整个程序最核心的类，负责统筹其它两个类对象的调度以及事件的监听。
class Painter:
    def __init__(self):
        # 设置了画板窗口的大小与标题
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Painter")
        # 创建 Clock 对象
        self.clock = pygame.time.Clock()
        # 创建 Brush 对象
        self.brush = Brush(self.screen)
        # 创建 Menu 对象，并设置了默认笔刷
        self.menu = Menu(self.screen)
        self.menu.set_brush(self.brush)

    def run(self):
        self.screen.fill((255, 255, 255))
        # 程序的主体是一个循环，不断对界面进行重绘，直到监听到结束事件才结束循环
        while True:
            # 设置帧率
            self.clock.tick(30)
            # 监听事件
            for event in pygame.event.get():
                # 结束事件
                if event.type == QUIT:
                    return
                # 键盘按键事件
                elif event.type == KEYDOWN:
                    # 按下 ESC 键，清屏
                    if event.key == K_ESCAPE:
                        self.screen.fill((255, 255, 255))
                # 鼠标按下事件
                elif event.type == MOUSEBUTTONDOWN:
                    # 若是当前鼠标位于菜单中，则忽略掉该事件
                    # 否则调用 start_draw 设置画笔的 drawing 标志为 True
                    if event.pos[0] <= 74 and self.menu.click_button(event.pos):
                        pass
                    else:
                        self.brush.start_draw(event.pos)
                # 鼠标移动事件
                elif event.type == MOUSEMOTION:
                    self.brush.draw(event.pos)
                # 松开鼠标按键事件
                elif event.type == MOUSEBUTTONUP:
                    # 调用 end_draw 设置画笔的 drawing 标志为 False
                    self.brush.end_draw()
                    pygame.image.save(self.screen, 'saved_img.png')
            # 绘制菜单按钮
            self.menu.draw()
            # 刷新窗口
            pygame.display.update()


def main():
    app = Painter()
    app.run()

if __name__ == '__main__':
    main()
