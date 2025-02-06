import pygame
"""
This file is the GUI on top of the game backend.
"""

BACKGROUND = 'game/images/ramin.jpg'
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (219, 186, 130)


def get_rbg(color):
    if color == 'WHITE':
        return 255, 255, 255
    elif color == 'BLACK':
        return 0, 0, 0
    else:
        return 0, 133, 211


class UI:
    def __init__(self, board_size=19):
        """Create, initialize and draw an empty board."""
        self.board_size = board_size
        self.cell_size = 40  # pixels between lines
        self.margin = 45  # margin from edge
        
        # Calculate board dimensions
        self.board_pixels = (self.board_size - 1) * self.cell_size
        self.outline = pygame.Rect(self.margin, self.margin, self.board_pixels, self.board_pixels)
        self.screen = None
        self.background = None
        self.font = None
        self.score_rect = pygame.Rect(45, self.margin + self.board_pixels + 15, 720, 35)
        
        # Pass button
        self.pass_button = None
        self.pass_text = None
        
        # Timer
        self.timer_rect = pygame.Rect(self.margin + self.board_pixels + 20, 20, 130, 40)

    def initialize(self):
        """Initialize the game board."""
        pygame.init()
        pygame.display.set_caption('Go Game')
        
        # Set window size based on board size
        window_width = max(820, self.margin * 2 + self.board_pixels + 200)  # Extra space for UI elements
        window_height = self.margin * 2 + self.board_pixels + 100  # Extra space for scores and buttons
        self.screen = pygame.display.set_mode((window_width, window_height), 0, 32)
        self.background = pygame.image.load(BACKGROUND).convert()
        self.font = pygame.font.SysFont('Arial', 20)
        
        # Initialize pass button
        button_y = self.margin + self.board_pixels + 15
        self.pass_button = pygame.Rect(self.margin, button_y, 100, 30)
        self.pass_text = self.font.render('Pass Turn', True, (0, 0, 0))

        # Draw the board outline
        pygame.draw.rect(self.background, BLACK, self.outline, 3)
        
        # Draw the grid lines
        for i in range(self.board_size):
            # Vertical lines
            start_pos = (self.margin + (self.cell_size * i), self.margin)
            end_pos = (self.margin + (self.cell_size * i), self.margin + self.board_pixels)
            pygame.draw.line(self.background, BLACK, start_pos, end_pos, 1)
            
            # Horizontal lines
            start_pos = (self.margin, self.margin + (self.cell_size * i))
            end_pos = (self.margin + self.board_pixels, self.margin + (self.cell_size * i))
            pygame.draw.line(self.background, BLACK, start_pos, end_pos, 1)

        # Draw star points (hoshi)
        if self.board_size == 19:
            star_points = [(3, 3), (3, 9), (3, 15),
                          (9, 3), (9, 9), (9, 15),
                          (15, 3), (15, 9), (15, 15)]
        elif self.board_size == 13:
            star_points = [(3, 3), (3, 9),
                          (6, 6),
                          (9, 3), (9, 9)]
        else:  # 9x9
            star_points = [(2, 2), (2, 6),
                          (4, 4),
                          (6, 2), (6, 6)]

        for x, y in star_points:
            pos = (self.margin + x * self.cell_size, self.margin + y * self.cell_size)
            pygame.draw.circle(self.background, BLACK, pos, 5, 0)

        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

    def coords(self, point):
        """Return the coordinate of a stone drawn on board"""
        return (self.margin + point[0] * self.cell_size, 
                self.margin + point[1] * self.cell_size)

    def leftup_corner(self, point):
        """Return the top-left corner for the area to clear when removing a stone"""
        return (self.margin - 20 + point[0] * self.cell_size, 
                self.margin - 20 + point[1] * self.cell_size)

    def draw(self, point, color, size=18):
        """Draw a stone at the specified intersection."""
        rgb_color = get_rbg(color)
        position = self.coords(point)
        pygame.draw.circle(self.screen, rgb_color, position, size, 0)
        pygame.display.update()

    def remove(self, point):
        """Remove a stone from the board at the given point."""
        x, y = point
        screen_x = self.margin + (x * self.cell_size)
        screen_y = self.margin + (y * self.cell_size)
        
        # Get the corresponding area from the background (which has only the grid)
        area_rect = pygame.Rect(screen_x - 20, screen_y - 20, self.cell_size, self.cell_size)
        stone_area = self.background.subsurface(area_rect).copy()
        
        # Blit the clean background area (with only grid lines) onto the screen
        self.screen.blit(stone_area, area_rect)
        pygame.display.update()

    def save_image(self, path_to_save):
        pygame.image.save(self.screen, path_to_save)

    def pixel_to_board_coords(self, x, y):
        """Convert pixel coordinates to board coordinates.
        Returns None if click is outside the valid board area."""
        if self.outline.collidepoint(x, y):
            board_x = int(round(((x - self.margin) / self.cell_size), 0))
            board_y = int(round(((y - self.margin) / self.cell_size), 0))
            # Ensure coordinates are within valid board range (1-19)
            if 1 <= board_x <= self.board_size and 1 <= board_y <= self.board_size:
                return (board_x, board_y)
        return None

    def update_score_display(self, black_score, white_score, game_over=False):
        """Update the score display at the bottom of the board."""
        # Clear the score area
        pygame.draw.rect(self.screen, (255, 255, 255), self.score_rect)
        
        # Create score text
        black_text = f"Black: {black_score:.1f}"
        white_text = f"White: {white_score:.1f}"
        
        # Render score text
        black_surface = self.font.render(black_text, True, (0, 0, 0))
        white_surface = self.font.render(white_text, True, (0, 0, 0))
        
        # Position and display scores
        self.screen.blit(black_surface, (50, self.margin + self.board_pixels + 20))
        self.screen.blit(white_surface, (250, self.margin + self.board_pixels + 20))
        
        # If game is over, display winner
        if game_over:
            winner = "Black" if black_score > white_score else "White"
            winner_text = f" Winner: {winner}!"
            winner_surface = self.font.render(winner_text, True, (0, 100, 0))
            self.screen.blit(winner_surface, (450, self.margin + self.board_pixels + 20))
        
        pygame.display.update()

    def draw_game_state(self, current_player, board, time_left):
        """Draw game state information including current player, scores, and pass button"""
        # Clear the info area
        info_rect = pygame.Rect(self.margin + self.board_pixels + 20, self.margin, 180, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), info_rect)
        
        # Get current scores
        scores = board.get_score()
        
        # Draw current player
        player_text = self.font.render(f"Current: {current_player}", True, (0, 0, 0))
        self.screen.blit(player_text, (self.margin + self.board_pixels + 30, self.margin + 10))
        
        # Draw current scores
        black_text = self.font.render(f"Black score: {scores['BLACK']:.1f}", True, (0, 0, 0))
        white_text = self.font.render(f"White score: {scores['WHITE']:.1f}", True, (0, 0, 0))
        self.screen.blit(black_text, (self.margin + self.board_pixels + 30, self.margin + 40))
        self.screen.blit(white_text, (self.margin + self.board_pixels + 30, self.margin + 70))
        
        # Draw pass button
        pygame.draw.rect(self.screen, (200, 200, 200), self.pass_button)
        pass_text_rect = self.pass_text.get_rect(center=self.pass_button.center)
        self.screen.blit(self.pass_text, pass_text_rect)
        
        # If there's been a pass, show it
        if board.passes > 0:
            pass_count = self.font.render(f"Passes: {board.passes}", True, (200, 0, 0))
            self.screen.blit(pass_count, (self.margin + self.board_pixels + 30, self.margin + 100))
        
        # Draw timer
        self.draw_timer(time_left)
        
        pygame.display.update()

    def draw_timer(self, time_left):
        """Draw the countdown timer."""
        # Clear previous timer
        pygame.draw.rect(self.screen, (255, 255, 255), self.timer_rect)
        pygame.draw.rect(self.screen, BLACK, self.timer_rect, 2)
        
        # Choose color based on remaining time
        if time_left > 5:
            color = (34, 139, 34)  # Green
        elif time_left > 2:
            color = (255, 165, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        
        # Draw timer text
        timer_text = self.font.render(f'Time: {int(time_left)}s', True, color)
        text_rect = timer_text.get_rect(center=self.timer_rect.center)
        self.screen.blit(timer_text, text_rect)

    def show_game_over(self, black_score, white_score, board):
        """Display game over screen with final scores and details"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Create game over text
        game_over_font = pygame.font.SysFont('Arial', 36)
        score_font = pygame.font.SysFont('Arial', 24)
        detail_font = pygame.font.SysFont('Arial', 20)
        
        # Create text surfaces
        game_over_text = game_over_font.render("Game Over!", True, (0, 0, 0))
        
        # Black score details
        black_captures = board.captured_stones['BLACK']
        black_score_text = score_font.render(f"Black Total: {black_score:.1f}", True, (0, 0, 0))
        black_detail = detail_font.render(f"(Territory + {black_captures} captures)", True, (100, 100, 100))
        
        # White score details (including komi)
        white_captures = board.captured_stones['WHITE']
        white_score_text = score_font.render(f"White Total: {white_score:.1f}", True, (0, 0, 0))
        white_detail = detail_font.render(f"(Territory + {white_captures} captures + {board.komi} komi)", True, (100, 100, 100))
        
        winner = "Black" if black_score > white_score else "White"
        margin = abs(black_score - white_score)
        winner_text = score_font.render(f" Winner: {winner} by {margin:.1f} points!", True, (0, 100, 0))
        
        # Position text in center of screen
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        
        # Draw all text elements
        self.screen.blit(game_over_text, 
                        game_over_text.get_rect(centerx=center_x, centery=center_y - 80))
        
        # Black score
        self.screen.blit(black_score_text, 
                        black_score_text.get_rect(centerx=center_x, centery=center_y - 20))
        self.screen.blit(black_detail, 
                        black_detail.get_rect(centerx=center_x, centery=center_y))
        
        # White score
        self.screen.blit(white_score_text, 
                        white_score_text.get_rect(centerx=center_x, centery=center_y + 40))
        self.screen.blit(white_detail, 
                        white_detail.get_rect(centerx=center_x, centery=center_y + 60))
        
        # Winner
        self.screen.blit(winner_text, 
                        winner_text.get_rect(centerx=center_x, centery=center_y + 100))
        
        pygame.display.update()
