#!/usr/bin/env python
from game.go import Board, opponent_color
from game.ui import UI
import pygame
import time
from os.path import join

class Match:
    def __init__(self, gui=True, dir_save=None):
        """
        Initialize a new Go game match between two human players.
        BLACK always has the first move.
        """
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)
        self.dir_save = dir_save
        self.time_elapsed = None
        
        # Initialize with board size selection
        self.board_size = self._select_board_size()
        self.board = Board(board_size=self.board_size, next_color='BLACK')
        self.ui = UI(board_size=self.board_size)

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

    def _select_board_size(self):
        """Show board size selection screen and return selected size"""
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('Go Game - Select Board Size')
        
        # Create buttons
        button_9x9 = pygame.Rect(150, 50, 100, 50)
        button_13x13 = pygame.Rect(150, 120, 100, 50)
        button_19x19 = pygame.Rect(150, 190, 100, 50)
        
        while True:
            screen.fill((255, 255, 255))
            
            # Draw buttons
            for button, text, size in [(button_9x9, "9x9", 9),
                                     (button_13x13, "13x13", 13),
                                     (button_19x19, "19x19", 19)]:
                pygame.draw.rect(screen, (200, 200, 200), button)
                text_surface = self.font.render(text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=button.center)
                screen.blit(text_surface, text_rect)
            
            # Draw title
            title = self.font.render("Select Board Size", True, (0, 0, 0))
            screen.blit(title, (130, 10))
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 19  # Default to 19x19 if window is closed
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button_9x9.collidepoint(mouse_pos):
                        return 9
                    elif button_13x13.collidepoint(mouse_pos):
                        return 13
                    elif button_19x19.collidepoint(mouse_pos):
                        return 19

    def _start_game(self):
        """Start the game with GUI for human players."""
        self.ui.initialize()
        self.time_elapsed = time.time()
        
        # Main game loop
        game_ended = False
        while True:
            # Update game state display
            self.ui.draw_game_state(self.board.next, self.board)
            
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
                        continue
                    
                    # Handle board clicks
                    if self.ui.outline.collidepoint(mouse_pos):
                        # Convert mouse position to board coordinates
                        x = int(round(((mouse_pos[0] - self.ui.margin) / self.ui.cell_size), 0))
                        y = int(round(((mouse_pos[1] - self.ui.margin) / self.ui.cell_size), 0))
                        point = (x, y)
                        
                        # Try to place the stone
                        success, captured = self.board.put_stone(point)
                        if success:
                            # First remove captured stones from the board
                            for captured_point in captured:
                                self.ui.remove(captured_point)
                            
                            # Then draw the new stone
                            self.ui.draw(point, opponent_color(self.board.next))
            
            pygame.display.update()
            
            if game_ended:
                pygame.time.wait(5000)  # Show final score for 5 seconds
                break

        self.time_elapsed = time.time() - self.time_elapsed
        if self.dir_save:
            self.ui.save_image(join(self.dir_save, 'final_board.png'))

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
