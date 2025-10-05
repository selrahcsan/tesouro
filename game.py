

WIDTH = 1024
HEIGHT = 768
TITLE = 'Caça ao Tesouro'

game_state = "menu"
music_on = True

try:
    music.play("background_music.mp3")
    music.set_volume(0.3)
except Exception:
    print("Arquivo 'background_music.mp3' não encontrado na pasta music/. A música não será tocada.")

menu_background = Actor("menu_background")
menu_background.width = WIDTH
menu_background.height = HEIGHT
menu_background.topleft = (0, 0) 

start_button = Actor("button_start", center=(WIDTH / 2, HEIGHT / 2 - 50))
sound_button = Actor("button_sound_on", center=(WIDTH / 2, HEIGHT / 2 + 50))
exit_button = Actor("button_exit", center=(WIDTH / 2, HEIGHT / 2 + 150))
menu_buttons = [start_button, sound_button, exit_button]


def draw_menu():
    """Desenha especificamente a tela do menu."""
    menu_background.draw() 
    
    for button in menu_buttons:
        button.draw()

def draw():
    """Desenha a Tela"""      
    if game_state == "menu":
        draw_menu()

def on_mouse_down(pos):
    """Cuida dos cliques do mouse."""
    global game_state, music_on
    
    if game_state == "menu":
        if start_button.collidepoint(pos):
            start_game()
        
        elif sound_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.unpause()
                sound_button.image = "button_sound_on"
                print("Música LIGADA")
            else:
                music.pause()
                sound_button.image = "button_sound_off"
                print("Música DESLIGADA")

        elif exit_button.collidepoint(pos):
            quit()    

def start_game():
    print("Inicia o Jogo")

def main():
    """Inicia o Jogo"""
    pgzero.go()

if __name__ == '__main__':
    main()