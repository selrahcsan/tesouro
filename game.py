

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


def draw():
    """Desenha a Tela"""
    screen.fill((46, 204, 113))
    
    
def main():
    """Inicia o Jogo"""
    pgzero.go()

if __name__ == '__main__':
    main()