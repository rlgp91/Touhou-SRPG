#! /usr/bin/env python

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
from OpenGL.GL import *

def initialize(title, dim):
    pygame.init()
    pygame.display.set_caption(title)
    pygame.display.set_mode(dim, OPENGL|DOUBLEBUF)
    glOrtho(0.0, dim[0], 0.0, dim[1],-1.0,1.0)
    glClearColor(0.0,0.0,0.0,0.0)
