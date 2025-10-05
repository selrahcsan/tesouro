import random

TILE_SIZE = 32
WIDTH = 1024
HEIGHT = 768
TITLE = "Caça ao Tesouro"

game_state = "menu"
is_animating = False
music_on = True
score = 0
lives = 2
idle_timer = 0.0
total_treasures = 0

try:
    music.play("background_music.mp3")
    music.set_volume(0.3)
except Exception:
    print("Aviso: 'background_music.mp3' não encontrado.")

def snap_to_grid(pos):
    """Alinha o grid (x, y)"""
    x = round((pos[0] - TILE_SIZE / 2) / TILE_SIZE) * TILE_SIZE + TILE_SIZE / 2
    y = round((pos[1] - TILE_SIZE / 2) / TILE_SIZE) * TILE_SIZE + TILE_SIZE / 2
    return (x, y)
class Character(Actor):
    """Classe Mãe para os personagens"""
    def __init__(self, image_prefix, start_pos, speed):
        """Inicializa um personagem com seus atributos."""
        super().__init__(f"{image_prefix}_idle_1", start_pos)
        self.image_prefix = image_prefix
        self.idle_frames = [f"{image_prefix}_idle_1", f"{image_prefix}_idle_2"]
        self.walk_frames = [f"{image_prefix}_walk_1", f"{image_prefix}_walk_2"]
        self.current_frame = 0
        self.animation_timer = 0.0
        self.is_moving = False
        self.speed = speed

    def update_animation(self, dt):
        """Atualiza o estado (parado ou andando)."""
        self.animation_timer += dt
        frames = self.walk_frames if self.is_moving else self.idle_frames
        if self.animation_timer > 0.25:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]
            self.animation_timer = 0

    def start_move(self):
        """Seta o personagem para 'andando'."""
        self.is_moving = True

    def stop_move(self):
        """Seta o personagem para 'parado'."""
        self.is_moving = False
class Player(Character):
    """Classe para os atributos do jogador."""
    def __init__(self, start_pos):
        """Cria o jogador com seus requisitos."""
        super().__init__("player", start_pos, speed=4)
class Enemy(Character):
    """Classe para os atributos dos inimigos."""
    def __init__(self, start_pos):
        """Cria um inimigo seus requisitos."""
        super().__init__("enemy", start_pos, speed=1.5)

player = Player((0, 0))
enemies, treasures, obstacles, hides = [], [], [], []
menu_background = Actor("menu_background", topleft=(0,0))
menu_background.width, menu_background.height = WIDTH, HEIGHT
start_button = Actor("button_start", center=(WIDTH / 2, HEIGHT / 2 - 50))
sound_button = Actor("button_sound_on", center=(WIDTH / 2, HEIGHT / 2 + 50))
exit_button = Actor("button_exit", center=(WIDTH / 2, HEIGHT / 2 + 150))
menu_buttons = [start_button, sound_button, exit_button]

def is_level_solvable(start_actor, treasures_list, obstacles_list):
    """Verifica se há um caminho livre entre o jogador e todos os tesouros."""
    grid_width, grid_height = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
    start_node = (int(start_actor.centerx // TILE_SIZE), int(start_actor.centery // TILE_SIZE))
    obstacle_nodes = {(int(obs.centerx // TILE_SIZE), int(obs.centery // TILE_SIZE)) for obs in obstacles_list}
    treasure_nodes = {(int(tre.centerx // TILE_SIZE), int(tre.centery // TILE_SIZE)) for tre in treasures_list}
    
    queue, reachable_nodes = [start_node], {start_node}
    while queue:
        current_x, current_y = queue.pop(0)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x, next_y = current_x + dx, current_y + dy
            if (0 <= next_x < grid_width and 0 <= next_y < grid_height and
                    (next_x, next_y) not in reachable_nodes and (next_x, next_y) not in obstacle_nodes):
                reachable_nodes.add((next_x, next_y)); queue.append((next_x, next_y))
    return treasure_nodes.issubset(reachable_nodes)

def setup_level():
    """Gera um novo mapa e garante que ele seja solucionável."""
    global score, lives, total_treasures
    generation_attempts = 0
    while True:
        generation_attempts += 1
        temp_obstacles, temp_treasures, temp_hides = [], [], []
        player.pos = snap_to_grid((WIDTH / 2, HEIGHT / 2))
        temp_placed = [player]

        def get_valid_pos(padding):
            """Encontra uma posição válida na grade que não colide com nenhum objeto."""
            while True:
                pos = snap_to_grid((random.randint(TILE_SIZE, WIDTH - TILE_SIZE), random.randint(TILE_SIZE, HEIGHT - TILE_SIZE)))
                check_rect = Rect(pos, (TILE_SIZE, TILE_SIZE)).inflate(padding, padding)
                if not any(obj.colliderect(check_rect) for obj in temp_placed):
                    return pos

        num_treasures, num_enemies, num_obstacles, num_hides = 15, 3, 10, 3
        total_treasures = num_treasures

        for _ in range(num_obstacles):
            obs = Actor('obstacle', get_valid_pos(TILE_SIZE * 0.5)); temp_obstacles.append(obs); temp_placed.append(obs)
        for _ in range(num_treasures):
            tre = Actor('treasure', get_valid_pos(TILE_SIZE)); temp_treasures.append(tre); temp_placed.append(tre)
        for _ in range(num_hides):
            hid = Actor('hide', get_valid_pos(TILE_SIZE)); temp_hides.append(hid); temp_placed.append(hid)
            
        if is_level_solvable(player, temp_treasures, temp_obstacles):
            print(f"Mapa válido gerado na tentativa {generation_attempts}!")
            obstacles[:], treasures[:], hides[:] = temp_obstacles, temp_treasures, temp_hides
            enemies.clear()
            corners = [(TILE_SIZE/2, TILE_SIZE/2), (WIDTH-TILE_SIZE/2, TILE_SIZE/2), (TILE_SIZE/2, HEIGHT-TILE_SIZE/2), (WIDTH-TILE_SIZE/2, HEIGHT-TILE_SIZE/2)]
            random.shuffle(corners)
            for i in range(num_enemies): enemies.append(Enemy(snap_to_grid(corners[i % len(corners)])))
            break
        else:
            print(f"Tentativa {generation_attempts}: Mapa inválido. Gerando novamente...")

def draw():
    """Desenha a tela principal."""
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state in ["playing", "hit_pause"]:
        draw_playing()
        if game_state == "hit_pause":
            screen.draw.text("Você foi pego! Clique com o mouse para continuar", midbottom=(WIDTH / 2, HEIGHT - 20), fontsize=40, color="yellow", owidth=1, ocolor="black")
    elif game_state == "victory":
        draw_end_screen("VITÓRIA!", "yellow")
    elif game_state == "game_over":
        draw_end_screen("GAME OVER", "red")

def draw_menu():
    """Desenha o Menu."""
    menu_background.draw()
    screen.draw.text("Caça ao Tesouro", center=(WIDTH / 2, HEIGHT / 3), fontsize=70, color="white", owidth=1.5, ocolor="black")
    for button in menu_buttons:
        button.draw()

def draw_playing():
    """Desenha a cena principal do jogo."""
    screen.fill((0, 150, 0))
    for x in range(0, WIDTH, TILE_SIZE): screen.draw.line((x, 0), (x, HEIGHT), (0, 80, 0))
    for y in range(0, HEIGHT, TILE_SIZE): screen.draw.line((0, y), (WIDTH, y), (0, 80, 0))
    for actor_list in [hides, obstacles, treasures, enemies, [player]]:
        for actor in actor_list: actor.draw()
    
    treasures_remaining = len(treasures)
    screen.draw.text(f"Pontos: {score}", (10, 10), fontsize=30, color="white")
    screen.draw.text(f"Vidas: {lives}", (10, 45), fontsize=30, color="white")
    screen.draw.text(f"Tesouros Restantes: {treasures_remaining}", (WIDTH - 320, 10), fontsize=30, color="white")

def draw_end_screen(message, color):
    """Desenha as telas de 'Vitória' ou 'Game Over'."""
    screen.fill("black")
    screen.draw.text(message, center=(WIDTH / 2, HEIGHT / 3), fontsize=80, color=color)
    screen.draw.text(f"Pontuação Final: {score}", center=(WIDTH / 2, HEIGHT / 2), fontsize=50, color="white")
    screen.draw.text("Clique para retornar ao Menu", center=(WIDTH / 2, HEIGHT / 2 + 100), fontsize=30, color="gray")

def process_player_turn(key):
    """Verifica o movimento e a coleta de tesouros do personagem."""
    global is_animating, score
    target_pos = list(player.pos)
    if key == keys.UP: target_pos[1] -= TILE_SIZE
    elif key == keys.DOWN: target_pos[1] += TILE_SIZE
    elif key == keys.LEFT: target_pos[0] -= TILE_SIZE
    elif key == keys.RIGHT: target_pos[0] += TILE_SIZE
    else: return
    target_pos = tuple(target_pos)
    
    is_in_bounds = 0 <= target_pos[0] < WIDTH and 0 <= target_pos[1] < HEIGHT
    is_on_obstacle = any(o.pos == target_pos for o in obstacles)
    
    if is_in_bounds and not is_on_obstacle:
        is_animating = True
        player.start_move()
        animate(player, pos=target_pos, duration=0.2, on_finished=process_enemies_turn)
        for t in treasures[:]:
            if t.pos == target_pos:
                if music_on: sounds.collect.play();
                treasures.remove(t); score += 10

def process_enemies_turn():
    """Calcula e executa o turno dos inimigos."""
    player.stop_move()
    is_player_hidden = any(h.colliderect(player) for h in hides)
    if is_player_hidden or not enemies:
        finish_turn(); return
        
    animations_to_complete = 0
    def on_enemy_animation_finish():
        nonlocal animations_to_complete
        animations_to_complete -= 1
        if animations_to_complete == 0: finish_turn()

    for enemy in enemies:
        if player.pos == enemy.pos: continue
        enemy.start_move()
        target_pos = list(enemy.pos)
        dx, dy = player.x - enemy.x, player.y - enemy.y
        if abs(dx) > abs(dy): target_pos[0] += TILE_SIZE if dx > 0 else -TILE_SIZE
        else: target_pos[1] += TILE_SIZE if dy > 0 else -TILE_SIZE
        target_pos = tuple(target_pos)
        
        is_on_obstacle = any(o.pos == target_pos for o in obstacles)
        is_on_other_enemy = any(e.pos == target_pos for e in enemies if e != enemy)
        
        if not is_on_obstacle and not is_on_other_enemy:
            animations_to_complete += 1
            animate(enemy, pos=target_pos, duration=0.2, on_finished=on_enemy_animation_finish)
        else:
            enemy.stop_move()
            
    if animations_to_complete == 0: finish_turn()

def finish_turn():
    """Finaliza o turno, verificando colisões e/ou vitória."""
    global is_animating, lives, game_state
    for enemy in enemies:
        enemy.stop_move()
        if player.colliderect(enemy):
            if music_on: sounds.hit.play()
            lives -= 1
            if lives <= 0:
                game_state = "game_over"
            else:
                is_animating = False; game_state = "hit_pause"; player.image = 'player_hit'
            return
            
    check_for_victory()
    if game_state == "playing": is_animating = False

def check_for_victory():
    """Verifica se o jogador coletou todos os tesouros."""
    global game_state
    if not treasures:
        game_state = "victory"

def on_key_down(key):
    """Iniciar o turno do jogador, depois de verificar o as setas do teclado."""
    if game_state == "playing" and not is_animating:
        process_player_turn(key)

def on_mouse_down(pos):
    """Captura os cliques do mouse para ser usado no jogo."""
    global game_state, music_on
    if game_state == "menu":
        if start_button.collidepoint(pos): start_game()
        elif sound_button.collidepoint(pos):
            music_on = not music_on
            if music_on: music.unpause(); sound_button.image = "button_sound_on"
            else: music.pause(); sound_button.image = "button_sound_off"
        elif exit_button.collidepoint(pos): quit()
    
    elif game_state == "hit_pause":
        reset_player_and_enemies(); game_state = "playing"
        player.image = player.idle_frames[0]
    
    elif game_state in ["game_over", "victory"]:
        game_state = "menu"

def update(dt):
    """Atualiza a animação de todos."""
    if game_state == "playing":
        player.update_animation(dt)
        for enemy in enemies:
            enemy.update_animation(dt)

def reset_player_and_enemies():
    """Reseta a posição do jogador para o centro e dos inimigos para os cantos."""
    player.pos = snap_to_grid((WIDTH / 2, HEIGHT / 2))
    corners = [(TILE_SIZE/2, TILE_SIZE/2), (WIDTH-TILE_SIZE/2, TILE_SIZE/2), (TILE_SIZE/2, HEIGHT-TILE_SIZE/2), (WIDTH-TILE_SIZE/2, HEIGHT-TILE_SIZE/2)]
    random.shuffle(corners)
    for i, enemy in enumerate(enemies):
        enemy.pos = snap_to_grid(corners[i % len(corners)])

def start_game():
    """Inicializa ou reinicializa todas as variáveis para um novo jogo."""
    global game_state, score, lives, is_animating
    score, lives = 0, 2
    game_state, is_animating = "playing", False
    setup_level()

def main():
    """Funação principal"""
    pgzrun.go()
    
if __name__ == '__main__':
    main()
   