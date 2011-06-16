'''
* This file is part of Touhou SRPG.
* Copyright (c) Hans Lo
*
* Touhou SRPG is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Touhou SRPG is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with Touhou SRPG.  If not, see <http://www.gnu.org/licenses/>.
'''

import pygame
from pygame.locals import *

from core.input_session import IOSession
from core.ui import UI, Menu
from core.graphics.animated import Animated
from core.graphics.graphic import GraphicAbsPositioned
import core.misc.astar as astar

from touhou_level import TouhouLevel, TouhouCreature
from touhou_ui import *
from touhou_graphic import OBJECTEVENT
from touhou_names import *

from tools.sprite_rules import *

class TouhouPlay(IOSession):
    SCROLL_SPEED = 5
    def __init__(self, level_state):
        IOSession.__init__(self)
        self.level = level_state
        self.map = self.level.map
        self.ui = TouhouUI(self.level)
        
        #test code
        test_reimu = Animated("./content/gfx/sprites/reimu.png", "./content/metadata/reimu.spr")
        test_reimu.set_facing(S)
        test_reimu.set_action("idle")
        self.map.place_object(test_reimu, (6,1), "reimu")
        
        reimu_data = TouhouCreature("reimu")
        reimu_data.set_speed(4)
        reimu_data.set_max_hp(70)
        reimu_data.set_max_ap(100)
        self.level.add_creature("reimu", reimu_data) 

        #test code
        test_suika = Animated("./content/gfx/sprites/suika.png", "./content/metadata/suika.spr")
        test_suika.set_facing(S)
        test_suika.set_action("idle")
        self.map.place_object(test_suika, (6,2), "suika")
        
        suika_data = TouhouCreature("suika")
        suika_data.set_speed(3)
        suika_data.set_max_hp(70)
        suika_data.set_max_ap(100)
        self.level.add_creature("suika", suika_data) 

        monster = Graphic("./content/gfx/sprites/monster.png")
        monster_data = TouhouCreature("monster")
        monster_data.set_max_hp(50)
        monster_data.set_speed(3)
        self.level.add_creature("monster",None)
        self.map.place_object(monster, (8,3), "monster")

        #sample character menu
        reimu_menu = Menu("Reimu")
        reimu_menu.set_body_graphic("./content/gfx/gui/menu_body.png")
        reimu_menu.set_entry_hover_graphic("./content/gfx/gui/menu_option.png")
        reimu_menu.set_w(80)
        reimu_menu.set_header_height(30)
        reimu_menu.set_entry_height(30)
        reimu_menu.add_entry("Move", self.ui.option_move)
        reimu_menu_placed = GraphicAbsPositioned(reimu_menu,(0,0))
        self.ui.add_menu(reimu_data, reimu_menu_placed)

        suika_menu = Menu("Suika")
        suika_menu.set_body_graphic("./content/gfx/gui/menu_body.png")
        suika_menu.set_entry_hover_graphic("./content/gfx/gui/menu_option.png")
        suika_menu.set_w(80)
        suika_menu.set_header_height(30)
        suika_menu.set_entry_height(30)
        suika_menu.add_entry("Move", self.ui.option_move)
        suika_menu_placed = GraphicAbsPositioned(suika_menu,(0,0))
        self.ui.add_menu(suika_data, suika_menu_placed)

        pygame.time.set_timer(USEREVENT+1,200)
        pygame.time.set_timer(USEREVENT+5,400)
        pygame.time.set_timer(USEREVENT+2,50)
        
        self.register_event(USEREVENT+1,test_reimu.update) #frame graphics
        self.register_event(USEREVENT+2,self.map.update_objects) #movement
        self.register_event(USEREVENT+3,self.ui_events)#UI events
        self.register_event(USEREVENT+4,self.object_events)#obj events
        self.register_event(USEREVENT+5,test_suika.update) #frame graphics

    def process(self, event_list):
        #self.test_reimu.update()
        self.ui.update(self.mouse_coords, self.mouse_state, self.keybuffer,(self.x,self.y))
        self.process_ui()
        self.register_draw(self.map.draw_ground())
        self.register_draw(self.ui.draw_under())
        self.register_draw(self.map.draw_sprites())
        self.register_draw(self.ui.draw())
        IOSession.process(self, event_list)
        self.scroll_map()

    # Respond to changes in UI interface
    def process_ui(self):
        data = self.ui.data
        if data.mode == I_BROWSE:
            pass
        elif data.mode == I_MOVE:
            if data.dest:
                path = astar.path(self.map, data.selected.pos, data.dest)
                x,y = self.ui.data.selected.pos
                self.map.grid[x][y].move_path(path)

    def ui_events(self, e):
        if e.subtype == MOVETO:
            self.move_character(e)
        elif e.subtype == ENDTURN:
            self.level.end_turn()
        
    def object_events(self, e):
        if e.subtype == OBJECTEVENT:
            self.map.update_obj_pos(e.obj)
            if not e.obj.moving:
                self.ui.set_browse()

    def move_character(self, e):
        pos = self.map.obj_list[e.name]
        path = astar.path(self.map, pos, e.dest)
        x,y = pos
        self.map.grid[x][y].move_path(path)

    def scroll_map(self):
        if self.keybuffer[K_UP]:
            self.shift((0,-self.SCROLL_SPEED))
        elif self.keybuffer[K_DOWN]:
            self.shift((0,self.SCROLL_SPEED))
        if self.keybuffer[K_LEFT]:
            self.shift((self.SCROLL_SPEED,0))
        elif self.keybuffer[K_RIGHT]:
            self.shift((-self.SCROLL_SPEED,0))
