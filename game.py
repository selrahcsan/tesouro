

WIDTH = 1024
HEIGHT = 768
TITLE = 'Caça ao Tesouro'

game_state = "menu"
music_on = True

def draw():
    """Desenha a Tela"""
    screen.fill((46, 204, 113))
    
    
def main():
    """Inicia o Jogo"""
    pgzero.go()

if __name__ == '__main__':
    main()