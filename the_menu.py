import pygame
import sys
import the_board
import socket
import threading


pygame.init()

#CONSTANTS
#region
MENU_WIDTH = 400
MENU_HEIGHT = 500
THE_BG_COLOR = (48,46,43,255)
BUTTON_GREEN = (129,182,76,255)
BUTTON_RED = (255,0,50,255)
TEXT_COLOR = (255,255,255,255)
NAME_BOX_COLOR = (0,0,255,255)
DARK_GREY = (56,55,52,255)
#endregion

#BOARD THEMES
#region
# Define themes
board_themes = {
    "Classic": ((235, 236, 208), (115, 149, 82)),  # Light and dark green
    "Blue": ((173, 216, 230), (0, 102, 204)),      # Light blue and dark blue
    "Dark": ((50, 50, 50), (100, 100, 100)),       # Dark shades
}

piece_themes = {
    "Classic": "Classic",
    "Neo"  : "Neo",
    "Alpha" : "Alpha",
}

move_methods = {
    "Click":"Click",
    "Drag" : 'Drag',
}

sound_options = {
    "On" :'On',
    'Off' : 'Off',
}

stale_mate = {
    "On" :'On',
    'Off' : 'Off',
}

castling = {
    "On" :'On',
    'Off' : 'Off',
}

en_passant = {
    "On" :'On',
    'Off' : 'Off',
}

promotion = {
    "On" :'On',
    'Off' : 'Off',
}

highlight_options = {
    'On' : 'On',
    'Off' : 'Off',
}

# Default theme
current_board_theme = "Classic"
current_piece_theme = "Neo"
current_move_method = "Click" 
current_sound_option = 'On'
current_en_passant_option = 'On'
current_stalemate_option = 'On'
current_castling_option = 'On'
current_promotion_option = 'On'
current_highlight_option = 'On'
#endregion


font = pygame.font.Font(None,34)
font_select = pygame.font.Font(None,25)
screen = pygame.display.set_mode((MENU_WIDTH,MENU_HEIGHT))

pygame.display.set_caption('Intro Menu')

class Button:
    def __init__(self,text,xpos,ypos,width,height,color,hover_color):
        self.text = text
        self.rect = pygame.Rect(xpos,ypos,width,height)
        self.color = color
        self.hover_color = hover_color 
        self.clicked = False

    def draw(self,screen):
        mouse_pos = pygame.mouse.get_pos()
        #rectangle and square of the button
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen,self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen,self.color, self.rect)
        #text inside the button
        text_surface = font.render(self.text,True,TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface,text_rect)

    #handle button click || also avoid multiple clicks
    def handle_event(self,event):
        #on click press
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self.clicked:
                self.clicked = True
                return True
        #release click
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.clicked = False

        #otherwise
        return False

class InputBox:
    def __init__(self,xpos,ypos,width,height,text=""):
        self.rect = pygame.Rect(xpos,ypos,width,height)
        self.color = NAME_BOX_COLOR
        self.text = text
        self.txt_surface = font.render(text,True,TEXT_COLOR)
        self.active = False
    
    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            #activate input box on click
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        
        if event.type == pygame.KEYDOWN  and self.active:
            if event.key == pygame.K_RETURN:
                print(f"Entered name: {self.text}")
                self.text=""
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1] #remove last charachter on backspace
            else:
                self.text += event.unicode
            
            self.txt_surface = font.render(self.text, True, TEXT_COLOR)
        
    def draw(self,screen):
        #draw text
        screen.blit(self.txt_surface,(self.rect.x+10, self.rect.y+10))
        #draw rectangle
        pygame.draw.rect(screen,self.color,self.rect, 2 if self.active else 1)

class DropDownMenu:
    def __init__(self,xpos,ypos,width,height,options):
        self.rect = pygame.Rect(xpos,ypos,width,height)
        self.color = DARK_GREY
        self.text =''
        self.options = options
        self.is_open = False
        self.selected_option = None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font_select.render(self.text or "Select", True, TEXT_COLOR)
        screen.blit(text_surface,(self.rect.x + 10, self.rect.y + 10))

        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height,self.rect.width,self.rect.height)
                option_text = font_select.render(option, True, TEXT_COLOR)
                screen.blit(option_text,(option_rect.x + 10, option_rect.y + 10))      

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height,
                                               self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_option = option
                        self.text = option

                        self.is_open = False

                        # Update the current theme based on which dropdown is interacted with
                        if self == dropdown_themes:  # For board themes
                            global current_board_theme
                            current_board_theme = option
                        elif self == dropdown_pieces:  # For piece themes
                            global current_piece_theme
                            current_piece_theme = piece_themes[option]
                        elif self == dropdown_move:  # For movement mode
                            global current_move_method
                            current_move_method = move_methods[option]  # Update movement mode
                        elif self == dropdown_sound:  # For movement mode
                            global current_sound_option
                            current_sound_option = sound_options[option]  # Update movement mode
                        elif self == dropdown_highlight:
                            global current_highlight_option
                            current_highlight_option = highlight_options[option]

                        #rules
                        elif self == dropdown_en_passant:  # For movement mode
                            global current_en_passant_option
                            current_en_passant_option = en_passant[option]
                        elif self == dropdown_stalemate:  # For movement mode
                            global current_stalemate_option
                            current_stalemate_option = stale_mate[option]
                        elif self == dropdown_castling:  # For movement mode
                            global current_castling_option
                            current_castling_option = castling[option]
                        elif self == dropdown_pawn_promotion:  # For movement mode
                            global current_promotion_option
                            current_promotion_option = promotion[option]
                        break
            else:
                self.is_open = False
                
#BUTTONS
#region
#Intro_menu
button_bots = Button('Bots',145,60,110,50,BUTTON_GREEN,BUTTON_RED)
button_2players = Button('2 players',145,140,110,50,BUTTON_GREEN,BUTTON_RED)
button_online = Button("Online",145,220,110,50,BUTTON_GREEN,BUTTON_RED)
button_settings = Button("Settings",145,300,110,50,BUTTON_GREEN,BUTTON_RED)

#Bots_levels
button_easy_levels = Button('Easy',150,60,100,50,BUTTON_GREEN,BUTTON_RED)
button_medium_levels = Button('Medium',150,140,100,50,BUTTON_GREEN,BUTTON_RED)
button_hard_levels = Button('Hard',150,220,100,50,BUTTON_GREEN,BUTTON_RED)

#BACK BUTTON
button_back = Button('Back',150,410,100,50,BUTTON_GREEN,BUTTON_RED)

#SETTINGS
button_board_settings = Button('board settings',110,60,200,50,BUTTON_GREEN,BUTTON_RED)
button_rule_settings = Button('rule settings',110,150,200,50,BUTTON_GREEN,BUTTON_RED)


#MENU LIST
menu = "Intro_menu"
history = []

#TEXT INPUT
input_box_name_1 = InputBox(100,90,200,50)
input_box_name_2 = InputBox(100,210,200,50)
button_submit = Button('Submit',140,270,120,50,BUTTON_GREEN,BUTTON_RED)

#DROP DOWN MENUS
#BOARD SETTINGS
dropdown_themes = DropDownMenu(190,50,100,40,list(board_themes.keys()))
dropdown_pieces = DropDownMenu(190,110,100,40,list(piece_themes.keys()))
dropdown_move = DropDownMenu(190,175,100,40,list(move_methods.keys()))
dropdown_sound = DropDownMenu(190,240,100,40,list(sound_options.keys()))
dropdown_highlight = DropDownMenu(220,295,100,40,list(highlight_options.keys()))

#RULE SETTINGS
dropdown_en_passant = DropDownMenu(240,95,100,40,list(en_passant.keys()))
dropdown_stalemate = DropDownMenu(240,95,100,40,list(stale_mate.keys()))
dropdown_castling = DropDownMenu(240,140,100,40,list(castling.keys()))
dropdown_pawn_promotion = DropDownMenu(240,250,100,40,list(promotion.keys()))
#endregion

#NAVIGATE MENUS
def navigate_to(new_menu):
    global menu, history
    if new_menu != menu:
        history.append(menu)
        menu = new_menu

def go_back():
    global menu
    if history:
        menu = history.pop()

def get_player_names(input_box_name_1, input_box_name_2):
    # Get the text entered in both input boxes
    player1_name = input_box_name_1.text.strip()  # White player
    player2_name = input_box_name_2.text.strip()  # Black player

    # If names are not entered, assign default values
    if not player1_name:
        player1_name = "White Player"
    if not player2_name:
        player2_name = "Black Player"

    return player1_name, player2_name

def start_client_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 5555)  # Replace with your server's IP and port

    try:
        client_socket.connect(server_address)
        print("Connected to server.")

        # Receive player color (white or black) from the server
        color = client_socket.recv(1024).decode('utf-8')
        print(f"Assigned color: {color}")

        return color, client_socket
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return None, None
    

def main_menu():
    running = True
    global menu

    while running:
        screen.fill(THE_BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if menu == "Intro_menu":
                if button_bots.handle_event(event):
                    navigate_to('Bots_levels')
                elif button_2players.handle_event(event):
                    navigate_to('Enter_Names')
                elif button_settings.handle_event(event):
                    navigate_to("settings")
                elif button_online.handle_event(event):
                    navigate_to("Online")

            elif menu == "Bots_levels":
                if button_easy_levels.handle_event(event):
                    white_name, black_name = get_player_names(input_box_name_1, input_box_name_2)
                    
                    the_board.main_menu(current_board_theme, current_piece_theme,current_move_method,current_sound_option,current_en_passant_option,current_stalemate_option,current_castling_option,current_promotion_option,white_name,black_name,current_highlight_option,bot_val=True,time_limit=1.0)

                elif button_medium_levels.handle_event(event):
                    white_name, black_name = get_player_names(input_box_name_1, input_box_name_2)
                    
                    the_board.main_menu(current_board_theme, current_piece_theme,current_move_method,current_sound_option,current_en_passant_option,current_stalemate_option,current_castling_option,current_promotion_option,white_name,black_name,current_highlight_option,bot_val=True,time_limit=2.0)

                elif button_hard_levels.handle_event(event):
                    white_name, black_name = get_player_names(input_box_name_1, input_box_name_2)
                    
                    the_board.main_menu(current_board_theme, current_piece_theme,current_move_method,current_sound_option,current_en_passant_option,current_stalemate_option,current_castling_option,current_promotion_option,white_name,black_name,current_highlight_option,bot_val=True,time_limit=3.0)
                        
            elif menu == "Enter_Names":
                input_box_name_1.handle_event(event)
                input_box_name_2.handle_event(event)
                button_submit.handle_event(event)

            elif menu == "settings":
                if button_board_settings.handle_event(event):
                    navigate_to('board_settings')
                elif button_rule_settings.handle_event(event):
                    navigate_to('rule_settings')
            
            elif menu == "board_settings":
                dropdown_themes.handle_event(event)
                dropdown_pieces.handle_event(event)
                dropdown_move.handle_event(event)
                dropdown_sound.handle_event(event)
                dropdown_highlight.handle_event(event)
            
            elif menu == "rule_settings":
                dropdown_en_passant.handle_event(event)
                dropdown_stalemate.handle_event(event)
                dropdown_castling.handle_event(event)
                dropdown_pawn_promotion.handle_event(event)
                     
            elif menu == "Online":
                color, client_socket = start_client_connection()

                if color:
                    if color == "white":
                        menu = "Enter_White_Name"
                    else:
                        menu = "Enter_Black_Name"

        if menu == "Intro_menu":
            pygame.display.set_caption('Intro_menu')
            button_bots.draw(screen)
            button_2players.draw(screen)
            button_online.draw(screen)
            button_settings.draw(screen)

        elif menu == "Bots_levels":
            pygame.display.set_caption('Bots_levels')
            button_easy_levels.draw(screen)
            button_medium_levels.draw(screen)
            button_hard_levels.draw(screen)

        elif menu == "Enter_Names":
            pygame.display.set_caption('Enter_Names')
            label_player1 = font.render('White Player:', True, TEXT_COLOR)
            screen.blit(label_player1,(100,50))
            input_box_name_1.draw(screen)

            label_player2 = font.render('Black Player:', True, TEXT_COLOR)
            screen.blit(label_player2,(100,170))
            input_box_name_2.draw(screen)

            button_submit.draw(screen)

            # Event handling
            for event in pygame.event.get():
                # Update input boxes with user typing
                input_box_name_1.handle_event(event)
                input_box_name_2.handle_event(event)

                # Detect mouse click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_submit.rect.collidepoint(event.pos):
                        white_name, black_name = get_player_names(input_box_name_1, input_box_name_2)
                        print(f"White Player: {white_name}, Black Player: {black_name}")
            
                        the_board.main_menu(current_board_theme, current_piece_theme,current_move_method,current_sound_option,current_en_passant_option,current_stalemate_option,current_castling_option,current_promotion_option,white_name,black_name,current_highlight_option,bot_val=False)

        elif menu == "settings":
            pygame.display.set_caption('settings')
            button_board_settings.draw(screen)
            button_rule_settings.draw(screen)

        elif menu == "board_settings":
            pygame.display.set_caption('board_settings')
            
            # Render Board Theme Label and Dropdown
            label_board_theme = font.render("Board:", True, TEXT_COLOR)
            screen.blit(label_board_theme, (100, 60))
            dropdown_themes.draw(screen)

            # Calculate Y position for Pieces Label and Dropdown
            pieces_y_pos = 90 + (dropdown_themes.rect.height * len(dropdown_themes.options) if dropdown_themes.is_open else 30)

            label_piece_settings = font.render("Pieces:", True, TEXT_COLOR)
            screen.blit(label_piece_settings, (100, pieces_y_pos))
            dropdown_pieces.rect.y = pieces_y_pos
            dropdown_pieces.draw(screen)

            # Calculate Y position for Move Settings Label and Dropdown
            move_y_pos = pieces_y_pos + 30 + (dropdown_pieces.rect.height * len(dropdown_pieces.options) if dropdown_pieces.is_open else 30)

            label_move_setting = font.render('Move:', True, TEXT_COLOR)
            screen.blit(label_move_setting, (100, move_y_pos))
            dropdown_move.rect.y = move_y_pos  # Ensure the move dropdown is positioned correctly
            dropdown_move.draw(screen)

            # Calculate Y position for Move Settings Label and Dropdown
            Sound_y_pos = move_y_pos + 30 + (dropdown_move.rect.height * len(dropdown_move.options) if dropdown_move.is_open else 30)

            label_sound_setting = font.render('Sound:', True, TEXT_COLOR)
            screen.blit(label_sound_setting, (100, Sound_y_pos))
            dropdown_sound.rect.y = Sound_y_pos  # Ensure the sound dropdown is positioned correctly
            dropdown_sound.draw(screen)

            # Calculate Y position for HIghlight Settings Label and Dropdown
            highlight_y_pos = Sound_y_pos + 30 + (dropdown_sound.rect.height * len(dropdown_sound.options) if dropdown_sound.is_open else 30)

            label_highlight_setting = font.render('Highlight:', True, TEXT_COLOR)
            screen.blit(label_highlight_setting, (100, highlight_y_pos))
            dropdown_highlight.rect.y = highlight_y_pos  # Ensure the sound dropdown is positioned correctly
            dropdown_highlight.draw(screen)
                
        elif menu == 'rule_settings':
            pygame.display.set_caption('rule_settings')
            # Draw En Passant label and dropdown
            label_en_passant = font.render("En Passant:", True, TEXT_COLOR)
            screen.blit(label_en_passant, (100, 100))
            dropdown_en_passant.draw(screen)

            # Calculate Y position for Stalemate based on En Passant dropdown
            stalemate_y_pos = 145 + (dropdown_en_passant.rect.height * len(dropdown_en_passant.options) if dropdown_en_passant.is_open else 0)

            label_stalemate = font.render("Stalemate:", True, TEXT_COLOR)
            screen.blit(label_stalemate, (100, stalemate_y_pos))
            dropdown_stalemate.rect.y = stalemate_y_pos
            dropdown_stalemate.draw(screen)

            # Calculate Y position for Castling based on Stalemate dropdown
            castling_y_pos = stalemate_y_pos + 55 + (dropdown_stalemate.rect.height * len(dropdown_stalemate.options) if dropdown_stalemate.is_open else 0)

            label_castling = font.render("Castling:", True, TEXT_COLOR)
            screen.blit(label_castling, (100, castling_y_pos))
            dropdown_castling.rect.y = castling_y_pos
            dropdown_castling.draw(screen)

            # Calculate Y position for Pawn Promotion based on Castling dropdown
            promotion_y_pos = castling_y_pos + 55 + (dropdown_castling.rect.height * len(dropdown_castling.options) if dropdown_castling.is_open else 0)

            label_pawn_promotion = font.render("Promotion:", True, TEXT_COLOR)
            screen.blit(label_pawn_promotion, (100, promotion_y_pos))
            dropdown_pawn_promotion.rect.y = promotion_y_pos
            dropdown_pawn_promotion.draw(screen)

        
        # Handling player name input in the main menu
        elif menu == "Enter_White_Name":
            pygame.display.set_caption('Enter White Player Name')
            label_player = font.render('Enter White Player Name:', True, TEXT_COLOR)
            screen.blit(label_player, (100, 50))
            input_box_name_1.draw(screen)
            button_submit.draw(screen)

            # Event handling for white player name input
            for event in pygame.event.get():
                input_box_name_1.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_submit.rect.collidepoint(event.pos):
                        white_name = input_box_name_1.text  # Get entered name
                        print(f"White Player: {white_name}")

                        # Notify the server of the name
                        client_socket.send(f"NAMES:{white_name}".encode('utf-8'))

                        # Start the game
                        the_board.main_menu(
                            current_board_theme, current_piece_theme, current_move_method,
                            current_sound_option, current_en_passant_option, current_stalemate_option,
                            current_castling_option, current_promotion_option,
                            white_name, 'Player 2', current_highlight_option, bot_val=False,
                            time_limit=None, player_color="white", client_socket=client_socket
                        )

        elif menu == "Enter_Black_Name":
            pygame.display.set_caption('Enter Black Player Name')
            label_player = font.render('Enter Black Player Name:', True, TEXT_COLOR)
            screen.blit(label_player, (100, 50))
            input_box_name_2.draw(screen)
            button_submit.draw(screen)

            # Event handling for black player name input
            for event in pygame.event.get():
                input_box_name_2.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_submit.rect.collidepoint(event.pos):
                        black_name = input_box_name_2.text  # Get entered name
                        print(f"Black Player: {black_name}")

                        # Notify the server of the name
                        client_socket.send(f"NAMES:{black_name}".encode('utf-8'))

                        # Start the game
                        the_board.main_menu(
                            current_board_theme, current_piece_theme, current_move_method,
                            current_sound_option, current_en_passant_option, current_stalemate_option,
                            current_castling_option, current_promotion_option,
                            'Player 2', black_name, current_highlight_option, bot_val=False,
                            time_limit=None, player_color="black", client_socket=client_socket
                        )



        if history:
            button_back.draw(screen)
            if button_back.handle_event(event):
                go_back()


        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

def main():
    main_menu()

if __name__ == "__main__":
    main()