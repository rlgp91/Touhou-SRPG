import pygame
from OpenGL.GL import *
from math import *

import astar
import ui
import objects
import touhou_characters

class Module:
    """
    Stores classes that define the module:
    map: map of objects in a sigle play session
    play: play session state
    """
    def __init__(self):
        self.map = TouhouMap
        self.play = TouhouPlay

class TouhouMap:
    """The current map and what is on it"""
    def __init__(self,dimensions):
        """
        grid: w by h grid that stores where everything is
        actors: All active characters in the play session
        tileset: What to draw with OpenGL
        """
        self.w, self.h = dimensions
        #tiles dimensions and offsets
        self.dimensions = (90,60)
        self.offsets = (45,30)

        self.grid = []
        for y in xrange(self.h):
            temp = []
            for x in xrange(self.w):
                temp += [None]
            self.grid += [temp]
        self.tileset = self.temp_tileset()
        self.actors = []

    def draw(self,offsets):
        """Draws everything that is on the board."""
        glTranslatef(*offsets)
        self.draw_floor()
        self.draw_objects()
        
    def draw_floor(self):
        """Draw the board."""   
        for x in range(self.w):
            for y in range(self.h):
                self.tileset["ground"].draw_grid(x,y,self.dimensions, self.offsets)
                
    def draw_objects(self):
        """Draw Active and Inactive objects"""
        for x in range(self.w):
            x = self.w - x - 1
            for y in range(self.h):
                if self.grid[x][y]:
                    self.grid[x][y].draw_grid(x,y,self.dimensions, self.offsets)
                    

    def temp_tileset(self):
        """Temporary tileset and objects to place on map"""
        tileset = {}
        tileset["ground"] = objects.Graphic(1.0,"grass.png")
        tileset["obstacle"] = StaticObject(1.0,"tree.png")
        self.tile_w = sqrt(pow(self.offsets[0],2) + pow(self.offsets[1],2))
        return tileset

    def insert(self,instance,position):
        self.grid[position[0]][position[1]] = instance

    def grid_coordinate(self, mouse_coords, offsets):
        """return grid coordinates of mouse click, None if not within grid"""
        mouse_x, mouse_y = mouse_coords
        
        mouse_x -= offsets[0]
        mouse_y -= offsets[1] + self.offsets[1]
        
        
        theta1 = atan(float(self.offsets[0])/float(self.offsets[1]))
        theta2 = atan(float(self.offsets[1])/float(self.offsets[0]))
        x = mouse_x*cos(theta1) + mouse_y*sin(theta1)
        
        y = mouse_x*sin(theta2) - mouse_y*cos(theta2)
        
        max_x = self.tile_w*(self.w-1)
        max_y = self.tile_w*(self.h-1)
        if 0 < x < max_x and 0 < y < max_y:
            cell_x, cell_y = int(floor((x/max_x)*self.w)), int(floor((y/max_y)*self.h))
            return cell_x, cell_y
        return False

    def process_click(self, mouse_coords, offsets):
        """return object that was clicked on, returns false if nothing"""
        coords = self.grid_coordinate(mouse_coords, offsets)
        if coords:
            return self.grid[coords[0]][coords[1]]
        return False

    def relocate(self, subject, new_position):
        self.grid[new_position[0]][new_position[1]] = subject
        self.grid[subject.position[0]][subject.position[1]] = None
        subject.position = new_position
        
    def occupied(self, position):
        return self.grid[position[0]][position[1]]


class TouhouPlay:
    """The state of a Touhou play session at any given moment"""
    FRAMEUPDATE = pygame.USEREVENT + 1
    MOVE, ATTACK, BROWSE, WAIT = range(4)
    def __init__(self, touhou_map):
        """ 
        selectable: Characters that can be clicked on at a given moment
        menu: Menu options available if it is called up
        map: what is currently on the map
        
        """
        self.active = []
        self.menu_selections = {}
        self.menu_title = ""
        self.menu = ui.Menu(self.menu_title)
        
        self.map = touhou_map
        self.offsets = [0,0,0]
        self.mode = self.BROWSE
        
        self.test_objects()
        

        #Custom Events for Touhou Module
        pygame.time.set_timer(self.FRAMEUPDATE,150)
        
    def test_objects(self):
        position = (4,4)
        reimu = touhou_characters.Reimu(position,self.map,self)
        self.active += [reimu] 
        for x in range(4):
            for y in range(4):
                self.map.insert(self.map.tileset["obstacle"],(x,y))

        self.map.insert(reimu,position)
        
        #self.active[0].move_cell("N")
        
    def update(self):
        for a in self.active:
            a.update()

    def process_click(self, mouse_coords, mouse_state):
        """ What to do when user clicks """
        print self.mode
        left, middle, right = mouse_state
        #What got clicked.
        clicked_object = self.determine_clicked(mouse_coords)
                #What to do given the current state and what got clicked
        if self.mode == self.MOVE:
            destination = self.map.grid_coordinate(mouse_coords, self.offsets)
            if destination and self.map.occupied(destination) == None:
                self.selected.new_path(self.map,destination)
                self.selected.menu_off()
                self.mode = self.BROWSE
        elif self.mode == self.BROWSE:
            if clicked_object in self.active:
                
                self.selected = clicked_object
                self.selected.menu_on()
                self.selected.menu.set_pos(*mouse_coords)
                self.mode = self.MOVE
                

    def determine_clicked(self, mouse_coords):
        #TODO: see if clicked on a UI element
        
        #see if clicking within the grid
        return self.map.process_click(mouse_coords, self.offsets)


    def process_event(self,event):
        if event.type == self.FRAMEUPDATE:
            self.update()

    def process_keybuffer(self, keybuffer):
        if keybuffer[pygame.K_UP]:
            self.offsets[1] -= 3.0
        if keybuffer[pygame.K_DOWN]:
            self.offsets[1] += 3.0
        if keybuffer[pygame.K_LEFT]:
            self.offsets[0] += 3.0
        if keybuffer[pygame.K_RIGHT]:
            self.offsets[0] -= 3.0
    
    def draw_relative(self):
        """ Draw all map elements """
        self.map.draw(self.offsets)
        if self.mode == self.MOVE:
            pass

    def draw_absolute(self):
        """ Draw all UI elements """
        for a in self.active:
            a.menu.draw()

    def move_square(self, subject, direction):
        pass
        
class Actor(objects.Animated):
    MOVING, IDLE = range(2)
    def __init__(self, x,y,sprite_name, position, touhou_map, touhou, scale_factor = 1.0):
        objects.Animated.__init__(self, x,y,sprite_name, scale_factor = 1.0)
        self.selected = False
        self.set_cell_offsets(0,0)
        self.position = position
        self.state = self.IDLE
        self.tile_offsets = touhou_map.offsets
        self.map = touhou_map
        self.path = []
        self.direction = None
        self.ticks = 0
        self.play = touhou

    def process_click(self, mode):
        pass

    def draw_grid(self, x, y, dimensions, offsets):
        glPushMatrix()
        glTranslatef(self.cell_offset_x, self.cell_offset_y, 0.0)
        objects.Animated.draw_grid(self, x, y, dimensions, offsets)
        glPopMatrix()
        
    def set_cell_offsets(self, x, y):
        self.cell_offset_x, self.cell_offset_y = x, y

    def mod_cell_offsets(self, x, y):
        self.cell_offset_x += x
        self.cell_offset_y += y

    def move_cell(self, direction):
        self.state = self.MOVING
        self.direction = direction
        self.ticks = 0

    def move_inc(self):
        """Move subject incrementally in a direction until it reaches one cell away"""
        if self.direction == "N":
            d = (1,1) 
            p = (1,0)
        elif self.direction == "S":
            d = (-1,-1)
            p = (-1,0)
        elif self.direction == "E":
            d = (1,-1)
            p = (0,1)
        elif self.direction == "W":
            d = (-1,1)
            p = (0,-1)
        else:
            d = (0,0)
            p = (0,0)

        self.mod_cell_offsets(d[0]*self.tile_offsets[0]/10.0, d[1]*self.tile_offsets[1]/10.0)
        self.ticks += 1
        if self.ticks >= 10:
            #self.state = self.IDLE
            self.map.relocate(self, (self.position[0] + p[0],self.position[1] + p[1]))
            self.set_cell_offsets(0.0,0.0)
            self.path = self.path[:-1]
            self.move_to_destination()
            self.ticks = 0
                        

    def move_to_destination(self):
        try:
            next_cell = self.path[-1]
        except IndexError:
            self.state = self.IDLE
            self.play.mode = self.play.BROWSE
            return
        direction = next_cell[0] - self.position[0], next_cell[1] - self.position[1]
        if direction == (0,1):
            self.direction = "E"
            self.current_action = "idle-e"
        elif direction == (0,-1):
            self.direction = "W"
            self.current_action = "idle-w"
        elif direction == (1,0):
            self.direction = "N"
            self.current_action = "idle-n"
        elif direction == (-1,0):
            self.direction = "S"
            self.current_action = "idle-s"
        
    def update(self):
        objects.Animated.update(self)
        if self.state == self.MOVING:
            self.move_inc()
        
    def new_path(self, touhou_map, destination):
        self.state = self.MOVING
        grid = astar.Grid(touhou_map)
        path = astar.Path(grid, self.position, [destination])
        self.path = path.path
        self.move_to_destination()
        
class StaticObject(objects.Graphic):
    def __init__(self, a, texture = None, scale_factor = 1.0, w = None, h = None):
        objects.Graphic.__init__(self, a, texture, scale_factor, w, h)

    def process_click(self, mode):
        pass

class PlayerCharacter:
    pass
