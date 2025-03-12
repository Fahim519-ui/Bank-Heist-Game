"""Defines classes convenient for game creation and display with the curses module.

A collection of classes that inherit the base class Entity. Having properties and
methods useful for representing virtual objects and their interractions, integrated
with the curses module to display these objects to a terminal.
"""

from heist.constants import Displacements as displacements
from heist.constants import Colors as colors
from heist import graphics
from math import copysign
from time import sleep

class Entity:
    """Contains all properties to call curses window.addstr()

    Attributes:
        win: A curses window.
        y: An integer of y coordinate.
        x: An integer of x coordinate.
        character: A string of what is displayed.
        color: An integer corresponding to a curses color pair.
    """

    def __init__(self, win, y=0, x=0, model=None, color=256, state='static'):
        self.win = win
        self.y = y
        self.x = x
        self.model = model
        self.state = state
        self.color = color
        self.show()

    def show(self):
        """Displays model of current state at (y, x)"""
        for i in range(len(self.model[self.state])):
            self.win.addstr(self.y + i, self.x, self.model[self.state][i], self.color)

    def hide(self):
        """Replaces model at (y, x) with the space ' ' character"""
        for i in range(len(self.model[self.state])):
            self.win.addstr(self.y + i, self.x, ' ' * len(self.model[self.state][0]), colors.YELLOW_BLACK)


class Counter(Entity):
    """Contains the counters used to show turn / score count in the game"""   
    def __init__(self, win, y=0, x=0, model=None, color=256, state='static'):
        self.count = 0
        super().__init__(win, y, x, model, color, state)


    def show(self):
        """Displays the counter, and the count"""
        for i in range(len(self.model[self.state])):
            self.win.addstr(self.y + i, self.x, self.model[self.state][i], self.color)
            #4 digits
            
            self.win.addstr(self.y + i + 4, self.x, graphics.display_number[(self.count - self.count % 1000) % 10000 / 1000][i], self.color)
            self.win.addstr(self.y + i + 4, self.x + 4, graphics.display_number[(self.count - self.count % 100) % 1000 / 100][i], self.color)
            self.win.addstr(self.y + i + 4, self.x + 8, graphics.display_number[(self.count - self.count % 10) % 100 / 10][i], self.color)
            self.win.addstr(self.y + i + 4, self.x + 12, graphics.display_number[self.count % 10][i], self.color)


class Movable(Entity):
    """Contains movable items in the game."""
    def __init__(self, win, current_map, y, x, model, color, state):
        super().__init__(win, y, x, model, color, state)
        self.current_map = current_map
        self.covering = None
        self.covered = None
        self.count = 0

    def front_point(self):
        """Convert the coordinate of the object into the coordinate of its front point, enabling checking of path ahead"""
        point = None
        match self.state:
            case 'right':
                point = (self.y -1, self.x + 8)
            case 'left':
                point = (self.y - 1, self.x - 5)
            case 'up':
                point = (self.y - 2, self.x - 3)
            case 'down':
                point = (self.y + 4, self.x - 3)
        return point

    def can_move_to(self, y, x):
        """Check if the path is clear for the object to move"""
        point = self.front_point()

        if self.win.inch(*point) & 0xFF == ord(' ') or (point in Interactable.entities and Interactable.entities[point].state == 'open'):
            
            #136 matches the output of the '█', 156 matches that of character '▜'.
            inched = self.win.inch(y, x) & 0xFF
            if inched == 136 or inched == 156:
                self.covering = (y, x)
                return False

            elif self.win.inch(y, x + 1) & 0xFF == ord(' '):
                self.covered = self.covering
                self.covering = None

            else:
                self.covering = (y, x)

            return True

        return False

    def move_to(self, y, x):
        """Move the object to given coordinate"""
        if not self.can_move_to(y, x):
            self.show()
            return False

        y_difference = y - self.y
        x_difference = x - self.x

        if y_difference:
            increment = int(copysign(2, y_difference))
            for i in range(3):
                self.hide()
                self.y += increment
                self.show()
                sleep(0.05)
                self.current_map.render()
        elif x_difference:
            increment = int(copysign(4, x_difference))
            for i in range(3): 
                self.hide()
                self.x += increment
                self.show()
                sleep(0.06)
                self.current_map.render()

        self.hide()
        if self.covered and self.covered in Interactable.entities:
            Interactable.entities[self.covered].show()
        self.x = x
        self.y = y
        self.show()
        self.current_map.render()

        return True
        
    def move_by(self, displacement):
        """Move the object by given displacement"""
        return self.move_to(self.y + displacement[0], self.x + displacement[1])

    def move(self, direction):
        """Return the displacement corresponding to the direcion"""
        self.state = direction
        match direction:
            case 'down':
                return self.move_by(displacements.STEP_DOWN)
            case 'up':
                return self.move_by(displacements.STEP_UP)
            case 'right':
                return self.move_by(displacements.STEP_RIGHT)
            case 'left':
                return self.move_by(displacements.STEP_LEFT)


class Interactable(Entity):
    """Contains objects which allow in-game interaction."""
    entities = {}

    def __init__(self, win, y, x, model, color, state):
        super().__init__(win, y, x, model, color, state)
        self.entities[(self.y, self.x)] = self

  
class Exit(Entity):
    """The exit of a map"""
    def __init__(self, win, y=0, x=0, color=colors.WHITE_BLACK):
        super().__init__(win, y, x, graphics.exit, color)


class Safe(Interactable):
    """The safes in a map"""
    def __init__(self, win, y=0, x=0, color=colors.YELLOW_BLACK, state='closed'):
        super().__init__(win, y, x, graphics.safe, color, state)
        self.value = 100

    def interact(self, player):
        """Add score to player when interacted"""
        if self.state == 'closed':
            self.state = 'open'
            player.score += self.value
        else:
            self.state = 'open'



class Door(Interactable):
    """The vertical doors in a map"""
    def __init__(self, win, y=0, x=0, color=colors.WHITE_BLACK, state='closed'):
        super().__init__(win, y, x, graphics.door, color, state)

    def interact(self):
        """Open or close when interacted"""
        if self.state == 'open':
            self.state = 'closed'
        else:
            self.state = 'open'
        self.show()
        return True


class Hatch(Interactable):
    """The horizontal doors in a map"""
    def __init__(self, win, y, x, color=colors.WHITE_BLACK, state='closed'):
        super().__init__(win, y, x, graphics.hatch, color, state)

    def interact(self):
        """Open or close when interacted"""
        if self.state == 'open':
            self.state = 'closed'
        else:
            self.state = 'open'
        self.show()
        return True


class Camera(Interactable):
    """
    The cameras in a map

    Attributes:
    direction: the direction the camera is facing to
    """
    def __init__(self, win, y, x, direction, color=colors.RED_BLACK):
        super().__init__(win, y, x, graphics.camera, color, f'clear_{direction}')
        self.direction = direction
        self.broken = False
        self.triggered = False

    def can_see(self, entity):
        """Check if the player is in front of the camera"""
        y_difference = entity.y - self.y
        x_difference = entity.x - self.x

        if y_difference == 1:
            if self.direction == 'right':
                if x_difference == 5:
                    return True
            
            elif self.direction == 'left':
                if x_difference == -8:
                    return True

        elif x_difference == 3:
            if self.direction == 'up':
                if y_difference == -4:
                    return True

            elif self.direction == 'down':
                if y_difference == 2:
                    return True

    def surveil(self, player):
        """React to detecting player"""
        if self.broken:
            return

        if self.can_see(player):
            self.state = f'seen_{self.direction}'
            self.triggered = True
            self.show()

    def interact(self):
        """Allow being broken by the player from the back"""
        if self.state == f'clear_{self.direction}':
            self.state = f'broken_{self.direction}'
            self.broken = True
            self.color = colors.WHITE_BLACK
            self.show()
            return True


class Player(Movable):
    """The player character"""
    def __init__(self, win, current_map, y, x, color=colors.RED_BLACK, state='down'):
        super().__init__(win, current_map, y, x, graphics.player, color, state)
        self.score = 0

        self.player = True

    def interact_front(self):
        """If able, interact with the object in front"""
        point = self.front_point()
        if point in Interactable.entities:
            return Interactable.entities[point].interact()


class Patroller(Movable):
    """The patroller character"""
    def __init__(self, win, current_map, y, x, route, cameras=None, color=colors.RED_BLACK, state='down'):
        super().__init__(win, current_map, y, x, graphics.patroller, color, state)
        self.route = route
        self.current_path = 0
        self.step = 0
        self.cameras = cameras
        self.twice = False
        self.player = False
        
    def patrol(self, player):
        """Move along the route, check if the player is on the route or adjacent, and determine if the game ends"""
        if self.current_path == len(self.route):
            self.current_path = 0

        direction = self.route[self.current_path % len(self.route)][0]

        self.step += 1

        #if len(self.route[(self.current_path - 1) % len(self.route)]) == 3:
               # self.route[(self.current_path - 1) % len(self.route)][2].interact()

        if self.move(direction):
            #Compares step to the max steps
            if self.step == self.route[self.current_path][1]:

                self.step = 0
                self.current_path += 1

                self.state = self.route[self.current_path % len(self.route)][0]
                self.show()       
        else:
            if self.covering and self.covering == (player.y, player.x):
                self.win.addch(self.y - 1, self.x + 6, '❗', self.color)
                return True
            
            if len(self.route[self.current_path]) > 2:

                self.route[self.current_path][2].interact()
                self.step -= 1

        #Adjacent detection    
        if self.x == player.x:
        
            if abs(self.y - player.y) <= 6: # tile height + 1
            
                if self.win.inch(int((self.y+player.y)//2) + 1, self.x) & 0xFF == ord(' '):
                    self.win.addch(self.y - 1, self.x + 6, '❗', self.color)
                    self.show()
                    player.show()
                    return True
   
        elif self.y == player.y:
            if abs(self.x - player.x) <= 13:
                if self.win.inch(self.y, int((self.x+player.x)//2) + 2) & 0xFF == ord(' '):
                    self.win.addch(self.y - 1, self.x + 6, '❗', self.color)
                    self.show()
                    player.show()
                    return True 
        '''
        if self.camera and self.camera.triggered and not self.twice:
            self.twice = True
            if self.patrol(player):
                return True
        '''
        for camera in self.cameras:
            if camera and camera.triggered and not self.twice:
                self.twice = True
                if self.patrol(player):
                    return True
        self.twice = False
