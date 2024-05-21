import tkinter as tk
import random

# Configuración inicial del juego
WIDTH, HEIGHT = 800, 750
BALLOON_COUNT = 10
BALLOON_SIZE = 30
PROJECTILE_SIZE = 6
PROJECTILE_SPEED = 16
MAX_PROJECTILE_SPEED = 35
BALLOON_SPEED = 1.5
LEVEL_UP_SPEED_INCREASE = .1
POWER_UP_CHANCE = 0.1
OBSTACLE_CHANCE = 0.1

class BalloonGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Balloon Pop Game") # Título de la app
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='lightblue')  # Determina el lienzo
        self.canvas.pack()
        self.balloons = []  # Lista para almacenar los globos en juego
        self.projectile = None  # Referencia al proyectil en el lienzo
        self.projectile_velocity = [0, 0]  # Velocidad inicial del proyectil
        self.score = 0  # Puntaje del jugador
        self.game_over = False  # Bandera para indicar si el juego ha terminado
        self.level = 1  # Nivel actual del juego
        self.balloon_speed = BALLOON_SPEED  # Velocidad inicial de los globos
        self.score_label = tk.Label(root, text=f"Score: {self.score} Level: {self.level}", font=('Helvetica', 16), bg='lightblue')  # Etiqueta para mostrar puntaje y nivel
        self.score_label.pack()
        self.create_balloons()  # Crear globos iniciales
        self.setup_projectile()  # Configurar el proyectil inicial
        self.canvas.bind("<Button-1>", self.mouse_click)  # Enlazar clic de ratón a método para disparar proyectil
        self.retry_button = tk.Button(self.root, text="Retry", command=self.retry_game)  # Botón para reintentar el juego
        self.retry_button.pack()
        self.retry_button.place_forget()
        self.win_text_id = None  # Identificador de texto de victoria
        self.update()  # Comenzar el bucle principal de actualización del juego

    # Método para crear globos iniciales
    def create_balloons(self):
        for _ in range(BALLOON_COUNT):
            x = random.randint(0, WIDTH - BALLOON_SIZE)
            y = -BALLOON_SIZE
            balloon_type = 'normal'
            # Determinar si el globo será un power-up o un obstáculo
            if random.random() < POWER_UP_CHANCE:
                balloon_type = 'power-up'
            elif random.random() < OBSTACLE_CHANCE:
                balloon_type = 'obstacle'
            # Crear globo en el lienzo
            if balloon_type == 'obstacle':
                # Crear globo obstáculo como un polígono
                balloon = self.canvas.create_polygon(x, y + BALLOON_SIZE // 2, x + BALLOON_SIZE // 2, y, x + BALLOON_SIZE, y + BALLOON_SIZE // 2, x + BALLOON_SIZE // 2, y + BALLOON_SIZE, fill='red')
            else:
                # Crear globo normal o power-up como un óvalo
                balloon = self.canvas.create_oval(x, y, x + BALLOON_SIZE, y + BALLOON_SIZE, fill=random.choice(['#FF6666', '#66FF66', '#6666FF', '#FFFF66']))
            # Agregar globo a la lista de globos en juego
            self.balloons.append((balloon, self.balloon_speed, balloon_type))

    # Método para configurar el proyectil inicial
    def setup_projectile(self):
        x = (WIDTH - PROJECTILE_SIZE) // 2
        y = HEIGHT - PROJECTILE_SIZE * 2
        # Crear proyectil en el lienzo
        self.projectile = self.canvas.create_oval(x, y, x + PROJECTILE_SIZE, y + PROJECTILE_SIZE, fill='darkgrey')

    # Método llamado al hacer clic en el lienzo para disparar el proyectil
    def mouse_click(self, event):
        if self.projectile_velocity == [0, 0] and not self.game_over:
            self.projectile_velocity = [0, -PROJECTILE_SPEED]
            projectile_pos = self.canvas.coords(self.projectile)
            self.canvas.coords(self.projectile, event.x, projectile_pos[1], event.x + PROJECTILE_SIZE, projectile_pos[3])

    # Método para actualizar el estado del juego
    def update(self):
        global PROJECTILE_SPEED
        if not self.game_over:
            # Mover el proyectil
            self.canvas.move(self.projectile, *self.projectile_velocity)
            projectile_pos = self.canvas.coords(self.projectile)
            # Iterar sobre todos los globos en juego
            for balloon, speed, balloon_type in self.balloons:
                balloon_pos = self.canvas.coords(balloon)
                # Mover el globo
                self.canvas.move(balloon, 0, speed)
                # Verificar colisión entre proyectil y globo
                if self.check_collision(projectile_pos, balloon_pos):
                    self.canvas.delete(balloon)
                    self.balloons.remove((balloon, speed, balloon_type))
                    # Actualizar puntaje según tipo de globo
                    if balloon_type == 'normal':
                        self.score += 10
                    elif balloon_type == 'power-up':
                        self.score += 50
                        PROJECTILE_SPEED = min(PROJECTILE_SPEED * 2, MAX_PROJECTILE_SPEED)
                    elif balloon_type == 'obstacle':
                        self.game_over = True
                        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", font=('Helvetica', 36), fill='red')
                        self.retry_button.place(x=WIDTH // 2 - 30, y=HEIGHT // 2 + 50)
                        break
                    # Actualizar etiqueta de puntaje
                    self.score_label.config(text=f"Score: {self.score} Level: {self.level}")
                # Verificar si algún globo llegó al fondo de la pantalla
                if balloon_type != 'obstacle' and balloon_pos[3] > HEIGHT:
                    self.game_over = True
                    self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", font=('Helvetica', 36), fill='red')
                    self.retry_button.place(x=WIDTH // 2 - 30, y=HEIGHT // 2 + 50)
                    break
            # Verificar si todos los globos son obstáculos y no hay más en juego
            if not any(balloon_type != 'obstacle' for _, _, balloon_type in self.balloons) and not self.game_over:
                self.canvas.delete(self.win_text_id)
                self.next_level()
            # Reiniciar posición del pro

            if projectile_pos[1] < 0:
                self.projectile_velocity = [0, 0]
                self.canvas.coords(self.projectile, (WIDTH - PROJECTILE_SIZE) // 2, HEIGHT - PROJECTILE_SIZE * 2, (WIDTH + PROJECTILE_SIZE) // 2, HEIGHT)
            if not self.game_over:
                self.root.after(50, self.update)

    def check_collision(self, projectile_pos, balloon_pos):
        return (projectile_pos[2] > balloon_pos[0] and
                projectile_pos[0] < balloon_pos[2] and
                projectile_pos[3] > balloon_pos[1] and
                projectile_pos[1] < balloon_pos[3])

    def next_level(self):
        self.level += 1
        self.score_label.config(text=f"Score: {self.score} Level: {self.level}")
        global BALLOON_SPEED
        BALLOON_SPEED += LEVEL_UP_SPEED_INCREASE
        self.balloon_speed += LEVEL_UP_SPEED_INCREASE
        self.create_balloons()
        self.win_text_id = self.canvas.create_text(WIDTH // 2, HEIGHT // 4, text="You win! Next level...", font=('Helvetica', 24), fill='green')
        self.root.after(1500, self.check_next_level)  

    def check_next_level(self):
        if not self.game_over:
            self.canvas.delete(self.win_text_id)
            self.update() 

    def retry_game(self):
        self.canvas.delete("all")
        self.score = 0
        self.score_label.config(text=f"Score: {self.score} Level: {self.level}")
        self.balloons.clear()
        self.balloon_speed = BALLOON_SPEED  
        self.create_balloons()
        self.setup_projectile()
        self.game_over = False
        self.retry_button.place_forget()
        self.update()

root = tk.Tk()
game = BalloonGame(root)
root.mainloop()



