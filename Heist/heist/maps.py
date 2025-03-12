"""
Defines classes for display and running the game with the curses module.

A collection of classes that inherit the base classes Map and Game. Using classes
defined in entity.py, the first set of classes are used to display the menus and 
maps, and the second set of classes run game loops based on given maps.
"""

from heist import graphics
from heist import entity
from heist.constants import Colors as colors
from time import sleep

class Map:
    """Contains all properties related to the actual display and processes in the game.

    Attributes:
        curses: Enabling the use of the curses library.
        user: The current user.
        keys: Enabling receiving keyboard input.
    """
    #Default height and width
    HEIGHT = 10
    WIDTH = 10
    def __init__(self, curses, user, keys):
        self.curses = curses 
        self.user = user
        self.keys = keys
        self.pad = curses.newpad(self.HEIGHT + 1, self.WIDTH + 1)
        self.y = 0
        self.x = 0
        self.pad.keypad(True)
        self.pad.scrollok(False)
        self.pad.leaveok(True)
        self.restart = False
        self.turn = 0
        self.cash = 0
        self.stop = False

    def background(self):
        """Draw a background for display"""
        graphics.draw_box(self.pad, 0, 0, self.HEIGHT, self.WIDTH, ' ', colors.WHITE_BLACK)

    def render(self):
        """Render the current map, enabling scrolling the terminal"""
        height = (self.HEIGHT - 1 + self.y) if (self.HEIGHT + self.y < self.user.rows) else (self.user.rows - 1)
        width = (self.WIDTH - 1 + self.x) if (self.WIDTH + self.x < self.user.cols) else (self.user.cols - 1)
        self.pad.refresh(0, 0, self.y, self.x, height, width)

    def play(self):
        """Loop the game loop"""
        self.render()

        while not self.stop:
            self.loop()
        sleep(4)

        entity.Interactable.entities.clear()

                                                                                                                                                        
class Title(Map):
    """The title page and main menu of the game"""
    HEIGHT = 30
    WIDTH = 160

    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)
        self.load()
        self.index = 0
        self.maps = (
            Tutorial,
            First,
            Second,
            Third,
            None
        )
        
    def loop(self):
        """The main menu loop, get user input for level selection"""
        if self.restart:
            self.restart = False
            game_map = self.maps[self.index](self.curses, self.user, self.keys)
            game_map.play()

        self.level_buttons[self.index].state = 'static'
        self.level_buttons[self.index].show()

        self.curses.flushinp()
        key = self.pad.getch()

        match key:
            case self.keys.KEY_DOWN:      
                self.index += 1
                if self.index > 4:
                    self.index = 0
            case self.keys.KEY_UP:
                self.index -= 1
                if self.index < 0:
                    self.index = 4
             
            case self.keys.INTERACT:
                self.pad.clear()
                self.render()
                if not self.maps[self.index]:
                    self.stop = True
                    return
                game_map = self.maps[self.index](self.curses, self.user, self.keys)
                game_map.play()
                
                if game_map.restart:
                    self.restart = True
                    return

                self.load()
            case self.keys.RESIZE:
                self.user.resize_terminal()
                self.render()

        self.level_buttons[self.index].state = 'hover'
        self.level_buttons[self.index].show()

        self.render()
        sleep(0.05)

    def load(self):
        """Display the game title and the main menu options"""
        self.background()

        entity.Entity(self.pad, (self.HEIGHT - len(graphics.title['static']))//2 - 1, 2, graphics.title, colors.YELLOW_BLACK)

        if hasattr(self, 'level_buttons'):
            for button in self.level_buttons:
                button.show()
            return

        mid_height = (self.HEIGHT - len(graphics.title['static']))//2 + 9
        self.level_buttons = (
            entity.Entity(self.pad, mid_height - 12, (self.WIDTH + len(graphics.title['static'][-1]) - len(graphics.level_button_1['static'][0])) // 2 + 8, graphics.level_button_tutorial, colors.WHITE_BLACK, 'hover'),
            entity.Entity(self.pad, mid_height - 5,  (self.WIDTH + len(graphics.title['static'][-1]) - len(graphics.level_button_1['static'][0])) // 2 + 3, graphics.level_button_1, colors.WHITE_BLACK),
            entity.Entity(self.pad, mid_height,      (self.WIDTH + len(graphics.title['static'][-1]) - len(graphics.level_button_2['static'][0])) // 2 + 3, graphics.level_button_2, colors.WHITE_BLACK),
            entity.Entity(self.pad, mid_height + 5,  (self.WIDTH + len(graphics.title['static'][-1]) - len(graphics.level_button_3['static'][0])) // 2 + 3, graphics.level_button_3, colors.WHITE_BLACK),
            entity.Entity(self.pad, mid_height + 10, (self.WIDTH + len(graphics.title['static'][-1]) - len(graphics.level_button_3['static'][0])) // 2 + 8, graphics.level_button_quit, colors.WHITE_BLACK)
            )

 
class PauseMenu(Map):
    """The pause menu of the game"""
    HEIGHT = 30
    WIDTH = 160
    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)
        self.loaded = False
        self.index = 0
        self.actions = ('resume', 'retry', 'quit')
    
    def loop(self):
        """The pause menu loop, get user input for the options"""
        self.pause_buttons[self.index].state = 'static'
        self.pause_buttons[self.index].show()
        self.curses.flushinp()
        key = self.pad.getch()

        match key:
            case self.keys.KEY_DOWN:      
                self.index += 1
                if self.index > 2:
                    self.index = 0
            case self.keys.KEY_UP:
                self.index -= 1
                if self.index < 0:
                    self.index = 2
            case self.keys.INTERACT:
                self.pad.clear()
                self.action = self.actions[self.index]
                self.stop = True
                return
            case self.keys.RESIZE:
                self.user.resize_terminal()
                self.render()

        self.pause_buttons[self.index].state = 'hover'
        self.pause_buttons[self.index].show()

        self.render()
        sleep(0.05)

    def load(self):
        """Display the pause menu options"""
        self.background()

        #entity.Entity(self.pad, 3, (self.WIDTH - len(graphics.pause_title['static'][0]))//2, graphics.pause_title, colors.YELLOW_BLACK)
        entity.Entity(self.pad, 3, (self.WIDTH - len(graphics.pause_title['static'][0]))//2, graphics.pause_title, colors.YELLOW_BLACK)

        if hasattr(self, 'pause_buttons'):
            self.index = 0
            self.pause_buttons[self.index].state = 'hover'
            self.pause_buttons[self.index].show()
            for button in self.pause_buttons:
                button.show()
            return

        #(self.WIDTH - len(graphics.pause_button_resume['static'][0]))//2
        self.pause_buttons = (
            entity.Entity(self.pad, 8, (self.WIDTH - len(graphics.pause_button_resume['static'][0]))//2, graphics.pause_button_resume, colors.WHITE_BLACK, 'hover'),
            entity.Entity(self.pad, 15, (self.WIDTH - len(graphics.pause_button_resume['static'][0]))//2, graphics.pause_button_retry, colors.WHITE_BLACK),
            entity.Entity(self.pad, 20, (self.WIDTH - len(graphics.pause_button_resume['static'][0]))//2, graphics.pause_button_quit, colors.WHITE_BLACK),
            )

    def play(self):
        """Loop the pause menu loop"""
        self.load()
        self.render()

        self.action = None
        self.stop = False
        while not self.stop:
            self.loop()

    
class Game(Map):
    """The setup procedures based on a given map"""
    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)
        self.load()

        self.pause_menu = PauseMenu(self.curses, self.user, self.keys)

        self.player = entity.Player(self.pad, self, self.STARTING_Y, self.STARTING_X)

        self.max_score = self.MAX_SCORE

        self.turn_counter = entity.Counter(self.pad, 2, 119, graphics.turn_counter, colors.YELLOW_BLACK, 'static')                                      
        self.cash_counter = entity.Counter(self.pad, 10, 119, graphics.cash_counter, colors.YELLOW_BLACK, 'static')
        #may add another counter here :)


    def loop(self):
        """The game loop"""
        displacement = None
        action = None
        
        self.curses.flushinp()
        key = self.pad.getch()
        match key:
            case self.keys.KEY_DOWN:
                if self.player.move('down'):
                    action = 'move'
            case self.keys.KEY_UP:
                if self.player.move('up'):
                    action = 'move'
            case self.keys.KEY_RIGHT:
                if self.player.move('right'):
                    action = 'move'
            case self.keys.KEY_LEFT:
                if self.player.move('left'):
                    action = 'move'
            case self.keys.INTERACT:
                if self.player.interact_front():
                    action = 'interact'
            case self.keys.RESIZE:
                self.user.resize_terminal()
            case self.keys.QUIT:
                self.pause_menu.play()
                if self.pause_menu.action == 'retry':
                    self.restart = True
                    self.stop = True
                    return
                elif self.pause_menu.action == 'quit':
                    self.stop = True
                    return

        self.render()

        if not action:
            return   

        self.turn_counter.count += 1
        self.turn_counter.show()

        if self.player.covering and self.player.covering in entity.Interactable.entities:
            entity.Interactable.entities[self.player.covering].interact(self.player)

        self.cash_counter.count = self.player.score
        self.cash_counter.show()
    
        if self.player.covering == self.exit:
            self.stop = True
            if self.player.score == self.max_score:
                entity.Entity(self.pad, 6, 26, graphics.notice_win, colors.YELLOW_BLACK, 'static')
            else:
                entity.Entity(self.pad, 6, 26, graphics.notice_escape, colors.YELLOW_BLACK, 'static')
            score_counter = entity.Counter(self.pad, 10, 26, graphics.score_counter, colors.YELLOW_BLACK, 'static')
            score_counter.count = round((self.player.score / self.turn_counter.count), 2) * 100
            score_counter.show()
            sleep(1)
        

        self.render()

        for camera in self.cameras:
                camera.surveil(self.player)

        sleep(0.1)

        for patroller in self.patrollers:
            if not self.stop:
                if patroller.patrol(self.player):
                    self.stop = True
                    entity.Entity(self.pad, 6, 26, graphics.notice_lose, colors.RED_BLACK, 'static')
                    sleep(0.2)
                
        self.render()


class First(Game):
    """The first level setup"""
    HEIGHT = 25
    #WIDTH = 80
    WIDTH = 150
    STARTING_Y = 20
    STARTING_X = 5
    MAX_SCORE = 600

    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)

    def load(self):
        """Load the level, display the map"""
        self.background()
        graphics.draw_outline(self.pad, 0, 0, self.HEIGHT, self.WIDTH, '█', colors.WHITE_BLACK)

        #Vertical walls ordered from left to right.
        graphics.draw_box(self.pad, 1, 13, 23, 2)
        graphics.draw_box(self.pad, 6, 26, 18, 2)
        graphics.draw_box(self.pad, 12, 39, 8, 2)
        graphics.draw_box(self.pad, 12, 52, 7, 2)
        graphics.draw_box(self.pad, 1, 65, 12, 2)
        graphics.draw_box(self.pad, 6, 78, 18, 2)
        graphics.draw_box(self.pad, 6, 91, 12, 2)
        graphics.draw_box(self.pad, 1, 104, 12, 2)
        graphics.draw_box(self.pad, 1, 117, 24, 2)

        # #Horizontal walls ordered from top to bottom.
        graphics.draw_box(self.pad, 6, 39, 1, 28)
        graphics.draw_box(self.pad, 6, 78, 1, 15)
        graphics.draw_box(self.pad, 12, 26, 1, 15)
        graphics.draw_box(self.pad, 12, 52, 1, 15)
        graphics.draw_box(self.pad, 18, 65, 1, 15)
        graphics.draw_box(self.pad, 18, 104, 1, 15)

        entity.Exit(self.pad, 2, 109)
        self.exit = (2, 109)

        entity.Safe(self.pad, 2, 5),
        entity.Safe(self.pad, 20, 70),
        entity.Safe(self.pad, 14, 31),
        entity.Safe(self.pad, 8, 57),
        entity.Safe(self.pad, 8, 83),
        entity.Safe(self.pad, 20, 109)
        
        door_1 = entity.Door(self.pad, 13, 13)
        door_2 = entity.Door(self.pad, 19, 39)
        door_3 = entity.Door(self.pad, 7, 52)
        door_4 = entity.Door(self.pad, 19, 65)
        door_5 = entity.Door(self.pad, 1, 65)
        door_6 = entity.Door(self.pad, 19, 104)
        
        hatch_1 = entity.Hatch(self.pad, 6, 2)
        #hatch_2 = entity.Hatch(self.pad, 6, 28)
        hatch_2 = entity.Hatch(self.pad, 12, 80)
        #hatch_4 = entity.Hatch(self.pad, 18, 54)

        camera_1 = entity.Camera(self.pad, 1, 13, 'right')
        camera_2 = entity.Camera(self.pad, 7, 104, 'left')

        self.cameras = (camera_1, camera_2)

        route = (
            ('left', 1), ('up', 1), ('left', 1),
            ('down', 3), ('up', 3), ('right', 1),
            ('down', 1), ('right', 1), ('down', 2),
            ('right', 1), ('up', 1), ('right', 1),
            ('up', 2), ('right', 2), ('down', 3), 
            ('up', 3), ('left', 2), ('down', 2),
            ('left', 1), ('down', 1), ('left', 1), ('up', 2,)
        )

        graphics.draw_route(self.pad, 4, 20, 18, 1, 'vertical')
        graphics.draw_route(self.pad, 3, 21, 1, 12, 'horizontal')
        graphics.draw_route(self.pad, 4, 33, 5, 1, 'vertical')
        graphics.draw_route(self.pad, 9, 34, 1, 12, 'horizontal')
        graphics.draw_route(self.pad, 10, 46, 11, 1, 'vertical')
        graphics.draw_route(self.pad, 21, 47, 1, 12, 'horizontal')
        graphics.draw_route(self.pad, 16, 59, 5, 1, 'vertical')
        graphics.draw_route(self.pad, 15, 60, 1, 12, 'horizontal')
        graphics.draw_route(self.pad, 4, 72, 11, 1, 'vertical')
        graphics.draw_route(self.pad, 3, 73, 1, 25, 'horizontal')
        graphics.draw_route(self.pad, 4, 98, 18, 1, 'vertical')

        self.patrollers = (entity.Patroller(self.pad, self, 8, 44, route, self.cameras), )

class Tutorial(Game):
    """The tutorial level setup"""
    HEIGHT = 25
    #WIDTH = 80
    WIDTH = 150
    STARTING_Y = 14
    STARTING_X = 18
    MAX_SCORE = 100

    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)

    def load(self):
        """Load the level, display the map"""
        self.background()
        graphics.draw_outline(self.pad, 0, 0, self.HEIGHT, self.WIDTH, '█', colors.WHITE_BLACK)

        #Add text
        text_1 = entity.Entity(self.pad, 1, 2, graphics.tutorial_text_1, colors.YELLOW_BLACK, 'static')
        text_2 = entity.Entity(self.pad, 19, 2, graphics.tutorial_text_2, colors.YELLOW_BLACK, 'static')
        #Vertical walls ordered from left to right.
        graphics.draw_box(self.pad, 12, 12, 6, 2)
        graphics.draw_box(self.pad, 6, 78, 12, 2)
        # #Horizontal walls ordered from top to bottom.
        graphics.draw_box(self.pad, 6, 1, 1, 78)
        graphics.draw_box(self.pad, 12, 12, 1, 68)
        graphics.draw_box(self.pad, 18, 1, 1, 79)

        entity.Exit(self.pad, 8, 70)
        self.exit = (8, 70)

        
        entity.Safe(self.pad, 14, 70),
        
        
        door_1 = entity.Door(self.pad, 13, 65)
        
        hatch_3 = entity.Hatch(self.pad, 12, 41)
        

        camera_1 = entity.Camera(self.pad, 12, 54, 'down')

        self.cameras = (camera_1, )

        route = (
            ('left', 3), ('down', 1), ('up', 1), ('right', 3)
        )
        self.patrollers = (entity.Patroller(self.pad, self, 8, 44, route, self.cameras), )

class Second(Game):
    """The second level setup"""
    HEIGHT = 25
    WIDTH = 150
    STARTING_Y = 2
    STARTING_X = 109
    MAX_SCORE = 600

    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)

    def load(self):
        """Load the level, display the map"""
        self.background()
        graphics.draw_outline(self.pad, 0, 0, self.HEIGHT, self.WIDTH, '█', colors.WHITE_BLACK)

        #Vertical walls ordered from left to right.
        graphics.draw_box(self.pad, 1, 26, 7, 2)
        graphics.draw_box(self.pad, 6, 13, 7, 2)
        graphics.draw_box(self.pad, 1, 39, 7, 2)
        graphics.draw_box(self.pad, 6, 52, 7, 2)
        graphics.draw_box(self.pad, 1, 65, 7, 2)
        graphics.draw_box(self.pad, 6, 78, 7, 2)
        graphics.draw_box(self.pad, 18, 78, 7, 2)
        graphics.draw_box(self.pad, 1, 117, 25, 2)


        # #Horizontal walls ordered from top to bottom.
        graphics.draw_box(self.pad, 6, 13, 1, 15)
        graphics.draw_box(self.pad, 6, 39, 1, 15)
        graphics.draw_box(self.pad, 6, 65, 1, 15)
        graphics.draw_box(self.pad, 6, 91, 1, 28)
        graphics.draw_box(self.pad, 12, 13, 1, 15)
        graphics.draw_box(self.pad, 12, 39, 1, 15)
        graphics.draw_box(self.pad, 12, 65, 1, 15)
        graphics.draw_box(self.pad, 12, 91, 1, 15)
        graphics.draw_box(self.pad, 18, 13, 1, 28)
        graphics.draw_box(self.pad, 18, 52, 1, 15)
        graphics.draw_box(self.pad, 18, 78, 1, 15)
        graphics.draw_box(self.pad, 18, 104, 1, 15)


        entity.Exit(self.pad, 20, 109)
        self.exit = (20, 109)

        entity.Safe(self.pad, 2, 18),
        entity.Safe(self.pad, 8, 18),
        entity.Safe(self.pad, 2, 44),
        entity.Safe(self.pad, 8, 44),
        entity.Safe(self.pad, 2, 70),
        entity.Safe(self.pad, 8, 70)
        
        door_1 = entity.Door(self.pad, 1, 13)
        door_2 = entity.Door(self.pad, 19, 13)
        door_3 = entity.Door(self.pad, 7, 26)
        door_4 = entity.Door(self.pad, 7, 39)
        door_5 = entity.Door(self.pad, 19, 39)
        door_6 = entity.Door(self.pad, 1, 52)
        door_7 = entity.Door(self.pad, 19, 52)
        door_8 = entity.Door(self.pad, 7, 65)
        door_9 = entity.Door(self.pad, 13, 65)
        door_10 = entity.Door(self.pad, 1, 78)
        door_11 = entity.Door(self.pad, 13, 91)
        door_12 = entity.Door(self.pad, 13, 104)

        camera_1 = entity.Camera(self.pad, 18, 28, 'down')

        self.cameras = (camera_1, )

        route_3 = (
            ('down', 2), ('left', 2), ('up', 2), ('down', 2), ('right', 2), ('up', 2)
        )
        route_1 = (
            ('right', 4), ('left', 4)
        )
        route_2 = (
            ('up', 1), ('left', 2), ('down', 1), ('left', 1), ('down', 1), ('left', 1), 
            ('right', 1), ('up', 1), ('right', 1), ('up', 1),('right', 2), ('down', 1),
        )


        graphics.draw_route(self.pad, 15, 7, 1, 52, 'horizontal')
        graphics.draw_route(self.pad, 21, 60, 1, 12, 'horizontal')
        graphics.draw_route(self.pad, 16, 73, 5, 1, 'vertical')
        graphics.draw_route(self.pad, 15, 74, 1, 12, 'horizontal')
        graphics.draw_route(self.pad, 10, 86, 5, 1, 'vertical')
        graphics.draw_route(self.pad, 9, 87, 1, 24, 'horizontal')
        graphics.draw_route(self.pad, 10, 111, 5, 1, 'vertical')

        
        self.patrollers = (
            #entity.Patroller(self.pad, self, 2, 57, route_1, camera_1), 
            entity.Patroller(self.pad, self, 14, 5, route_1, self.cameras), 
            entity.Patroller(self.pad, self, 14, 109, route_2, self.cameras),
            
            )

class Third(Game):
    """The third level setup"""
    HEIGHT = 25
    #WIDTH = 80
    WIDTH = 150
    STARTING_Y = 2
    STARTING_X = 5
    MAX_SCORE = 600

    def __init__(self, curses, user, keys):
        super().__init__(curses, user, keys)

    def load(self):
        """Load the level, display the map"""
        self.background()
        graphics.draw_outline(self.pad, 0, 0, self.HEIGHT, self.WIDTH, '█', colors.WHITE_BLACK)

        #Vertical walls ordered from left to right.
        graphics.draw_box(self.pad, 1, 13, 6, 2)
        graphics.draw_box(self.pad, 12, 13, 7, 2)
        graphics.draw_box(self.pad, 12, 26, 7, 2)
        graphics.draw_box(self.pad, 12, 52, 7, 2)
        graphics.draw_box(self.pad, 18, 65, 7, 2)
        graphics.draw_box(self.pad, 6, 91, 13, 2)
        graphics.draw_box(self.pad, 18, 104, 7, 2)
        graphics.draw_box(self.pad, 1, 117, 25, 2)

        #graphics.draw_box(self.pad, 1, 78, 23, 2)

        # #Horizontal walls ordered from top to bottom.
        graphics.draw_box(self.pad, 6, 13, 1, 41)
        graphics.draw_box(self.pad, 6, 65, 1, 15)
        graphics.draw_box(self.pad, 6, 104, 1, 13)
        graphics.draw_box(self.pad, 12, 13, 1, 13)
        graphics.draw_box(self.pad, 12, 39, 1, 15)
        graphics.draw_box(self.pad, 12, 65, 1, 15)
        graphics.draw_box(self.pad, 12, 91, 1, 28)
        graphics.draw_box(self.pad, 18, 1, 1, 15)
        graphics.draw_box(self.pad, 18, 39, 1, 15)
        graphics.draw_box(self.pad, 18, 78, 1, 28)


        entity.Exit(self.pad, 20, 109)
        self.exit = (20, 109)

        entity.Safe(self.pad, 20, 5),
        entity.Safe(self.pad, 14, 44),
        entity.Safe(self.pad, 8, 70),
        entity.Safe(self.pad, 2, 109),
        entity.Safe(self.pad, 2, 18),
        entity.Safe(self.pad, 20, 96)
        
        #door_1 = entity.Door(self.pad, 13, 13)
        door_2 = entity.Door(self.pad, 7, 26)
        door_3 = entity.Door(self.pad, 1, 52)
        #door_4 = entity.Door(self.pad, 19, 65)
        door_5 = entity.Door(self.pad, 13, 91)
        #door_6 = entity.Door(self.pad, 7, 104)
        
        hatch_1 = entity.Hatch(self.pad, 18, 15)
        hatch_2 = entity.Hatch(self.pad, 18, 67)
        hatch_3 = entity.Hatch(self.pad, 6, 93)
        
        graphics.draw_route(self.pad, 9, 34, 1, 25, 'horizontal')
        graphics.draw_route(self.pad, 21, 34, 1, 25, 'horizontal')
        graphics.draw_route(self.pad, 9, 33, 12, 1, 'vertical')       
        graphics.draw_route(self.pad, 3, 59, 18, 1, 'vertical')
        graphics.draw_route(self.pad, 3, 60, 1, 26, 'horizontal')
        graphics.draw_route(self.pad, 15, 60, 1, 26, 'horizontal')
        graphics.draw_route(self.pad, 4, 86, 11, 1, 'vertical')

        camera_1 = entity.Camera(self.pad, 13, 13, 'left')
        camera_2 = entity.Camera(self.pad, 12, 93, 'down')

        self.cameras = (camera_1, camera_2)

        route_1 = (
            ('down', 2), ('right', 2), ('up', 2), ('left', 2)
        )
        route_2 = (
            ('right', 2), ('up', 2), ('left', 2), ('down', 2)
        )
        self.patrollers = (
            entity.Patroller(self.pad, self, 8, 31, route_1, self.cameras), 
            entity.Patroller(self.pad, self, 2, 57, route_1, self.cameras),
            
            )

