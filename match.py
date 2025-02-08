#!/usr/bin/env python
from game.go import Board, opponent_color
from game.ui import UI
import pygame
import time
from os.path import join

class Match:
    def __init__(self, gui=True, dir_save=None):
        """
        Initialize a new Go game match.
        Allows selection of game mode and board size.
        """
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)
        self.dir_save = dir_save
        self.time_elapsed = None
        
        # Select game mode and board size
        self.game_mode, self.board_size = self._select_game_mode_and_board_size()
        
        # Initialize board with Black starting
        self.board = Board(board_size=self.board_size, next_color='BLACK')
        self.ui = UI(board_size=self.board_size)
        
        # Timer settings
        self.turn_timer = 10  # 10 seconds per turn
        self.timer_start = None
        self.game_over = False

    @property
    def winner(self):
        return self.board.winner

    @property
    def next(self):
        return self.board.next

    @property
    def counter_move(self):
        return self.board.counter_move

    def start(self):
        self._start_game()

    def _select_game_mode_and_board_size(self):
        """
        Multi-page selection screen for board size and game mode
        First page: Board Size Selection
        Second page: Game Mode Selection
        """
        pygame.init()
        screen_width, screen_height = 600, 500
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Go Game - Configuration')
        
        # Colors
        BACKGROUND_COLOR = (240, 240, 240)  # Light gray background
        BUTTON_COLOR = (220, 220, 220)  # Slightly darker gray for buttons
        HIGHLIGHT_COLOR = (100, 200, 100)  # Green highlight
        TEXT_COLOR = (0, 0, 0)  # Black text
        
        # Fonts
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        button_font = pygame.font.SysFont('Arial', 22)  # Reduced from 28
        subtitle_font = pygame.font.SysFont('Arial', 20)  # Reduced from 22
        
        # Board size buttons with compact layout
        button_width, button_height = 250, 60
        button_spacing = 20
        board_sizes = [
            {"size": 9, "rect": pygame.Rect(0, 0, button_width, button_height), "label": "9x9 - Beginner"},
            {"size": 13, "rect": pygame.Rect(0, 0, button_width, button_height), "label": "13x13 - Intermediate"},
            {"size": 19, "rect": pygame.Rect(0, 0, button_width, button_height), "label": "19x19 - Professional"}
        ]
        
        # Dynamically calculate button positions for perfect centering
        total_height = len(board_sizes) * button_height + (len(board_sizes) - 1) * button_spacing
        start_x = (screen_width - button_width) // 2
        start_y = 220
        
        # Adjust button positions vertically
        for i, board_option in enumerate(board_sizes):
            board_option['rect'].x = start_x
            board_option['rect'].y = start_y + (button_height + button_spacing) * i
        
        # Game mode buttons with improved layout
        game_modes = [
            {"mode": "PVP", "rect": pygame.Rect(100, 180, 400, 80), "label": "Player vs Player"},
            {"mode": "AI_HUMAN", "rect": pygame.Rect(100, 280, 400, 80), "label": "Player vs AI"},
            {"mode": "AI_AI", "rect": pygame.Rect(100, 380, 400, 80), "label": "AI vs AI"}
        ]
        
        # Selection state
        selected_size = None
        selected_mode = None
        current_page = 'BOARD_SIZE'
        
        while True:
            screen.fill(BACKGROUND_COLOR)
            
            # Page logic
            if current_page == 'BOARD_SIZE':
                # Title for board size selection
                title = title_font.render("Select Board Size", True, TEXT_COLOR)
                title_rect = title.get_rect(centerx=screen_width//2, top=50)
                screen.blit(title, title_rect)
                
                # Subtitle
                subtitle = subtitle_font.render("Choose a board size that suits your skill level", True, (100, 100, 100))
                subtitle_rect = subtitle.get_rect(centerx=screen_width//2, top=100)
                screen.blit(subtitle, subtitle_rect)
                
                # Draw board size buttons
                for board_option in board_sizes:
                    # Button background
                    pygame.draw.rect(screen, BUTTON_COLOR, board_option['rect'], border_radius=10)
                    pygame.draw.rect(screen, BUTTON_COLOR, board_option['rect'], width=2, border_radius=10)
                    
                    # Button text
                    size_text = button_font.render(board_option['label'], True, TEXT_COLOR)
                    size_text_rect = size_text.get_rect(center=board_option['rect'].center)
                    screen.blit(size_text, size_text_rect)
                
                # Highlight selected board size
                if selected_size is not None:
                    for board_option in board_sizes:
                        if board_option['size'] == selected_size:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, board_option['rect'], width=4, border_radius=10)
            
            elif current_page == 'GAME_MODE':
                # Title for game mode selection
                title = title_font.render("Select Game Mode", True, TEXT_COLOR)
                title_rect = title.get_rect(centerx=screen_width//2, top=50)
                screen.blit(title, title_rect)
                
                # Subtitle
                subtitle = subtitle_font.render("Choose how you want to play Go", True, (100, 100, 100))
                subtitle_rect = subtitle.get_rect(centerx=screen_width//2, top=100)
                screen.blit(subtitle, subtitle_rect)
                
                # Draw game mode buttons
                for mode_option in game_modes:
                    # Button background
                    pygame.draw.rect(screen, BUTTON_COLOR, mode_option['rect'], border_radius=10)
                    pygame.draw.rect(screen, BUTTON_COLOR, mode_option['rect'], width=2, border_radius=10)
                    
                    # Button text
                    mode_text = button_font.render(mode_option['label'], True, TEXT_COLOR)
                    mode_text_rect = mode_text.get_rect(center=mode_option['rect'].center)
                    screen.blit(mode_text, mode_text_rect)
                
                # Highlight selected game mode
                if selected_mode is not None:
                    for mode_option in game_modes:
                        if mode_option['mode'] == selected_mode:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, mode_option['rect'], width=4, border_radius=10)
            
            pygame.display.flip()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "PVP", 19  # Default to PVP and 19x19 if window is closed
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    if current_page == 'BOARD_SIZE':
                        # Board size selection
                        for board_option in board_sizes:
                            if board_option['rect'].collidepoint(mouse_pos):
                                selected_size = board_option['size']
                                current_page = 'GAME_MODE'
                                break
                    
                    elif current_page == 'GAME_MODE':
                        # Game mode selection
                        for mode_option in game_modes:
                            if mode_option['rect'].collidepoint(mouse_pos):
                                selected_mode = mode_option['mode']
                                # Return selected mode and size
                                return selected_mode, selected_size
            
            # Optional: Add a back button or key to return to board size selection
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and current_page == 'GAME_MODE':
                current_page = 'BOARD_SIZE'

    def _start_game(self):
        """Start the game with GUI for different game modes."""
        self.ui.initialize()
        self.time_elapsed = time.time()
        self.timer_start = time.time()
        
        # Main game loop
        game_ended = False
        while True:
            current_time = time.time()
            time_left = max(0, self.turn_timer - (current_time - self.timer_start))
            
            # Handle timer expiration
            if time_left == 0:
                pygame.display.set_caption('Go Game - Time\'s Up!')
                self.board.pass_move()
                self.timer_start = time.time()
                
                # If in AI modes, trigger AI move after pass
                if (self.game_mode == "AI_HUMAN" and self.board.next == 'WHITE') or \
                   (self.game_mode == "AI_AI"):
                    pygame.time.wait(500)  # Small delay before AI move
                    self._make_ai_move()
                continue
            
            # Update game state display
            self.ui.draw_game_state(self.board.next, self.board, time_left)
            
            # AI move handling
            if (self.game_mode == "AI_HUMAN" and self.board.next == 'WHITE') or \
               (self.game_mode == "AI_AI"):
                pygame.time.wait(500)  # Small delay before AI move
                self._make_ai_move()
                self.timer_start = time.time()
                continue
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    
                    # Check if pass button was clicked
                    if self.ui.pass_button.collidepoint(mouse_pos):
                        game_ended = self.board.pass_move()
                        if game_ended:
                            self._show_game_result()
                        self.timer_start = time.time()
                        
                        # If in AI modes, trigger AI move after pass
                        if (self.game_mode == "AI_HUMAN" and self.board.next == 'WHITE') or \
                           (self.game_mode == "AI_AI"):
                            pygame.time.wait(500)  # Small delay before AI move
                            self._make_ai_move()
                        continue
                    
                    # Handle board clicks
                    if self.ui.outline.collidepoint(mouse_pos):
                        # Convert mouse position to board coordinates
                        x = int(round(((mouse_pos[0] - self.ui.margin) / self.ui.cell_size), 0))
                        y = int(round(((mouse_pos[1] - self.ui.margin) / self.ui.cell_size), 0))
                        point = (x, y)
                        
                        # In PVP mode, normal stone placement
                        if self.game_mode == "PVP":
                            success, captured = self.board.put_stone(point)
                            if success:
                                # First remove captured stones from the board
                                for captured_point in captured:
                                    self.ui.remove(captured_point)
                                
                                # Then draw the new stone
                                self.ui.draw(point, opponent_color(self.board.next))
                                self.timer_start = time.time()
                        
                        # In AI_HUMAN mode, only allow BLACK stone placement
                        elif self.game_mode == "AI_HUMAN" and self.board.next == 'BLACK':
                            success, captured = self.board.put_stone(point)
                            if success:
                                # First remove captured stones from the board
                                for captured_point in captured:
                                    self.ui.remove(captured_point)
                                
                                # Then draw the new stone
                                self.ui.draw(point, 'BLACK')
                                
                                # Trigger AI move after human move
                                pygame.time.wait(500)  # Small delay before AI move
                                self._make_ai_move()
                                
                                self.timer_start = time.time()
            
            pygame.display.update()
            
            if game_ended:
                pygame.time.wait(5000)  # Show final score for 5 seconds
                break

        self.time_elapsed = time.time() - self.time_elapsed
        if self.dir_save:
            self.ui.save_image(join(self.dir_save, 'final_board.png'))

    def _make_ai_move(self):
        """Advanced AI player with strategic move selection."""
        import random
        import math
        import copy

        def evaluate_move(point, color):
            """Evaluate the strategic value of a potential move."""
            if not self.board.is_valid_move(point):
                return float('-inf')
            
            x, y = point
            score = 0
            
            # Proximity to existing stones (encourage clustering)
            nearby_stones = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                        if self.board.board[nx][ny] is not None:
                            nearby_stones += 1
            score += nearby_stones * 2
            
            # Potential stone capture
            test_board = copy.deepcopy(self.board)
            test_board.board[x][y] = color
            captured_groups = test_board._find_captured_groups(opponent_color(color))
            score += len(captured_groups) * 10
            
            # Territory control (proximity to board center)
            center_x, center_y = self.board_size // 2, self.board_size // 2
            distance_to_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            score += (self.board_size - distance_to_center)
            
            # Avoid moves near board edges
            if x < 2 or x > self.board_size - 3 or y < 2 or y > self.board_size - 3:
                score -= 5
            
            return score

        # Find all valid moves
        valid_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board.is_valid_move((i, j)):
                    valid_moves.append((i, j))
        
        if not valid_moves:
            # If no valid moves, pass
            return self.board.pass_move()
        
        # Determine current player color
        current_color = self.board.next
        
        # Rank moves by strategic value
        ranked_moves = [(move, evaluate_move(move, current_color)) for move in valid_moves]
        ranked_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Select top moves, with some randomness to prevent predictability
        top_moves = ranked_moves[:max(3, len(ranked_moves) // 2)]
        best_move = random.choice(top_moves)[0]
        
        # Try to place the stone
        success, captured = self.board.put_stone(best_move)
        if success:
            # Remove captured stones from the board
            for captured_point in captured:
                self.ui.remove(captured_point)
            
            # Draw the new stone 
            self.ui.draw(best_move, current_color)
            return True
        
        return False

    def _show_game_result(self):
        """Display the final game result."""
        # Calculate final scores
        scores = self.board.get_score()
        
        # Show game over screen with final scores and board details
        self.ui.show_game_over(scores['BLACK'], scores['WHITE'], self.board)

def main():
    match = Match()
    match.start()

if __name__ == '__main__':
    main()
