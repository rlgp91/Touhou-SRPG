import pygame
import glFreeType
from pygame.locals import *
import pickle
from OpenGL.GL import *
import os.path

import objects
import widgets

x, y   = None, None
w, h = None, None
widgets_list = {}

def main():
    width, height = 640, 480
    pygame.display.init()
    pygame.display.set_caption("Animator")
    display = pygame.display.set_mode((width, height), OPENGL|DOUBLEBUF)
    running = True

    set_up(width, height)

    while running:
        running = process()
        draw()

def f():
    print "lol"

def set_up(width, height):
    font = glFreeType.font_data( "free_sans.ttf", 30 )
    glOrtho(0.0, width, 0.0, height,-1.0,1.0)
    glClearColor(0.0,0.0,0.0,0.0)    
    
    widgets_list["object_text"] = widgets.Text_Box(0,300, "Object", "default")
    widgets_list["frame_text"] = widgets.Text_Box(200,300, "Frame", "default")
    widgets_list["object_button"] = widgets.Button(50, 300, "button.png", "button_down.png", load_spritesheet, (widgets_list["object_text"],))
    widgets_list["spritesheet"] = widgets.Null_Widget()

def process():
    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        if event.type == KEYDOWN:
            for w in widgets_list:
                widgets_list[w].process_key(event)
        if event.type == MOUSEBUTTONDOWN:
            for w in widgets_list:
                widgets_list[w].process_click(*pygame.mouse.get_pos())
        if event.type == MOUSEBUTTONUP:
            for w in widgets_list:
                widgets_list[w].process_release(*pygame.mouse.get_pos())
    return True
    
def draw():
    global widgets_list
    glClear(GL_COLOR_BUFFER_BIT)
        
    for w in widgets_list:
        widgets_list[w].draw()

    pygame.display.flip()

def load_spritesheet(spritesheet):
    
    text = spritesheet.text()
    
    try:
        open(text)
    except IOError:
        print "This file does not exist"
        return
    widgets_list["spritesheet"] = objects.Graphic(0,0,1.0, text,1.0)

if __name__ == "__main__":
    main()
