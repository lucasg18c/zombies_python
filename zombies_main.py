import random
import pygame

# CONSTANTES

WIDTH = 840
HEIGHT = 588

HITBOX = 40

X = 0
Y = 1

NORTE = 0
SUR = 1
ESTE = 2
OESTE = 3


# CLASES


class Jugador:
    def __init__(self):
        self.pos = [(WIDTH - HITBOX) // 2, (HEIGHT - HITBOX) // 2]
        self.vel = [0, 0]

        self.hit = [0, 0, 0, 0]
        self.HITBOX = 40

        self.inventario = [Arma('M1911', 7, 35, 34, 750, pistola_shot, pistola_shell)]
        self.arma = self.inventario[0]

        self.vida = 100
        self.puntos = 0
        self.last_buy = 0


class Ronda:
    def __init__(self):
        self.actual = 0
        self.zombies_ronda = 0
        self.zombies_cap = 5
        self.entre_ronda = False
        self.nueva_ronda = 0


class Cuadricula:
    def __init__(self, x, y):
        self.rel = [x, y]
        self.pos = [x * 84, y * 84]
        self.activo = True

        self.HITBOX = 84
        self.textura = None
        self.cerca = False

    def dibujar(self):
        if self.activo:
            ventana.blit(self.textura, (self.pos[X], self.pos[Y]))


class Pared(Cuadricula):
    def __init__(self, x, y):
        Cuadricula.__init__(self, x, y)

        self.textura = t_pared


class Wallbuy(Cuadricula):
    def __init__(self, x, y, tipo):
        Cuadricula.__init__(self, x, y)

        self.tipo = tipo
        self.comprado = 0  # Cantidad de puntos gastados
        self.sonido = buy_sound

        if self.tipo == 3:
            self.textura = wb_pistola
            self.arma = Arma('M1911', 7, 35, 34, 750, pistola_shot, pistola_shell)
            self.precio = 500

        elif self.tipo == 4:
            self.textura = wb_rifle
            self.arma = Arma('M4A1', 30, 60, 53, 300, rifle_asalto_shot, rifle_asalto_shell)
            self.precio = 1500

        elif self.tipo == 5:
            self.textura = wb_escopeta
            self.arma = Arma('Escopeta', 5, 15, 82, 2000, escopeta_shot, escopeta_shell)
            self.precio = 750

        elif self.tipo == 6:
            self.textura = wb_mp5
            self.arma = Arma('MP5', 32, 128, 23, 100, mp5_shot, pistola_shell)
            self.precio = 1000


class Puerta(Cuadricula):
    def __init__(self, x, y):
        Cuadricula.__init__(self, x, y)

        self.textura = t_puerta


class Piso(Cuadricula):
    def __init__(self, x, y, tipo):
        Cuadricula.__init__(self, x, y)

        if tipo == 2:
            self.textura = t_piso
        else:
            self.textura = t_spawn


class Arma:
    def __init__(self, nombre, cargador, reserva, damage, cadencia, shot, shell):
        self.nombre = nombre
        self.disparando = False

        self.cargador_total = cargador
        self.cargador = cargador

        self.reserva_total = reserva
        self.reserva = reserva

        self.comienzo_recarga = 0
        self.recargando = False

        self.cadencia = cadencia
        self.ready = True
        self.last_shot = 0

        self.damage = damage

        # Sonido
        self.shot = shot
        self.shell = shell

    def disparo(self, xa, ya, zomb):
        cx = j.pos[X] + HITBOX // 2
        cy = j.pos[Y] + HITBOX // 2
        self.ready = False
        self.last_shot = pygame.time.get_ticks()
        self.cargador -= 1
        self.disparando = True
        self.shot.play()
        self.shell.play()

        # Disparo Vertical
        if xa == cx:
            if ya < cy:
                for i in range(len(zomb)):
                    if j.pos[X] <= zomb[i].pos[X] <= j.pos[X] + HITBOX and zomb[i].pos[Y] < cy:
                        zomb[i].hurt()
                        return
            else:
                for i in range(len(zomb)):
                    if j.pos[X] <= zomb[i].pos[X] <= j.pos[X] + HITBOX and zomb[i].pos[Y] > cy:
                        zomb[i].hurt()
                        return
            return

        # Disparo Horizontal
        if ya == cy:
            if xa < cx:
                for i in range(len(zomb)):
                    if j.pos[Y] <= zomb[i].pos[Y] <= j.pos[Y] + HITBOX and zomb[i].pos[X] < cx:
                        zomb[i].hurt()
                        return
            else:
                for i in range(len(zomb)):
                    if j.pos[Y] <= zomb[i].pos[Y] <= j.pos[Y] + HITBOX and zomb[i].pos[X] > cx:
                        zomb[i].hurt()
                        return
            return

        # Exepción por dispararse a si mismo
        if xa == cx and ya == cy:
            xa -= 10
            ya -= 10

        # Disparo Diagonal
        orientacion = 1
        if xa < cx:
            orientacion = -1

        pend = (ya - cy) / (xa - cx)
        for x in range(cx, cx + orientacion * 1500, orientacion):
            y = pend * (x - cx) + cy

            for i in range(len(zomb)):
                z = zomb[i]
                if z.pos[X] <= x <= z.pos[X] + HITBOX and z.pos[Y] <= y <= z.pos[Y] + HITBOX:
                    zomb[i].hurt()
                    return

    def is_ready(self):
        if pygame.time.get_ticks() >= self.last_shot + self.cadencia and not j.arma.recargando:
            self.ready = True

    def recargar(self):
        # Comienzo de recarga
        if not self.recargando and self.cargador < self.cargador_total and self.reserva > 0:
            self.recargando = True
            self.ready = False
            self.comienzo_recarga = pygame.time.get_ticks()

        # Termina recarga
        if self.comienzo_recarga + 3000 <= pygame.time.get_ticks() and self.recargando:
            self.recargando = False
            self.ready = True

            if self.cargador + self.reserva >= self.cargador_total:
                self.reserva -= (self.cargador_total - self.cargador)
                self.cargador = self.cargador_total
                return
            self.cargador += self.reserva
            self.reserva = 0


class Zombie:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.vel = [0, 0]

        self.hit = [0, 0, 0, 0]
        self.HITBOX = 40

        self.salud = (ronda.actual - 1) * 8 + 100
        self.lastimado = False
        self.vivo = True

        self.golpe = False
        self.cansado = False
        self.tiempo_descanso = 0

    def dibujar(self):
        if not self.lastimado:
            pygame.draw.rect(ventana, (255, 0, 0), (self.pos[X], self.pos[Y], self.HITBOX, self.HITBOX))
        else:
            pygame.draw.rect(ventana, (50, 0, 0), (self.pos[X], self.pos[Y], self.HITBOX, self.HITBOX))

    def direccion(self):

        # Está cansado
        if self.cansado:
            self.vel = [0, 0]
            return

        # Directo verticalmente
        if j.pos[X] == self.pos[X]:
            ty = j.pos[Y] - self.pos[Y]
            if ty > 0:
                self.vel = [0, 2]
            else:
                self.vel = [0, -2]
            return

        # Directo Horizontalmente
        if j.pos[Y] == self.pos[Y]:
            tx = j.pos[X] - self.pos[X]
            if tx > 0:
                self.vel = [2, 0]
            else:
                self.vel = [-2, 0]
            return

        # Diagonalmente
        tx = j.pos[X] - self.pos[X]
        ty = j.pos[Y] - self.pos[Y]
        tvel = random.choice([(1, 2), (2, 1)])
        self.vel = [tvel[X] * (tx / abs(tx)), tvel[Y] * (ty / abs(ty))]

    def catch(self):
        self.golpe = False
        # Eje X
        if j.pos[X] + HITBOX >= self.pos[X] and j.pos[X] <= self.pos[X] + HITBOX:
            # Eje Y
            if j.pos[Y] + HITBOX >= self.pos[Y] and j.pos[Y] <= self.pos[Y] + HITBOX:
                self.golpe = True
                self.cansado = True
                self.tiempo_descanso = pygame.time.get_ticks() + 2500

    def descansar(self):
        self.golpe = False
        if self.tiempo_descanso <= pygame.time.get_ticks():
            self.cansado = False

    def hurt(self):
        self.salud -= j.arma.damage
        self.cansado = True
        self.lastimado = True
        self.tiempo_descanso = pygame.time.get_ticks() + 500
        if self.salud <= 0:
            self.vivo = False


# FUNCIONES


def generate_level(file):
    level = []
    m = open(file, 'r')
    raw_level = m.readlines()
    m.close()

    tcad = ''
    tlist = []
    for i in range(len(raw_level)):
        for car in raw_level[i]:

            if car == '#':
                break

            if car == '\n' and len(tlist):
                if tcad != '':
                    tlist.append(int(tcad))
                level.append(tlist)
                tcad, tlist = '', []
                continue

            if car == ' ' and tcad != '':
                tlist.append(int(tcad))
                tcad = ''
                continue

            try:
                int(car)
                tcad += car
            except ValueError:
                pass

    return level


def cargar_texturas():
    global t_pared, t_puerta, t_piso, wb_pistola, wb_rifle, wb_escopeta, t_spawn, wb_mp5
    t_pared = pygame.image.load('texturas/pared.png').convert()
    t_puerta = pygame.image.load('texturas/puerta.png').convert()
    t_piso = pygame.image.load('texturas/piso.png').convert()
    t_spawn = pygame.image.load('texturas/spawn.png').convert()
    wb_pistola = pygame.image.load('texturas/wallbuy_pistola.png').convert()
    wb_rifle = pygame.image.load('texturas/wallbuy_m4.png').convert()
    wb_escopeta = pygame.image.load('texturas/wallbuy_escopeta.png').convert()
    wb_mp5 = pygame.image.load('texturas/wallbuy_mp5.png').convert()


def cargar_sonido():
    global pistola_shot, pistola_shell, rifle_asalto_shot, rifle_asalto_shell, \
        buy_sound, escopeta_shot, escopeta_shell, mp5_shot

    pistola_shot = pygame.mixer.Sound('musica/Pistol_Sound.wav')
    pistola_shell = pygame.mixer.Sound('musica/pistol_shell.wav')
    pistola_shell.set_volume(0.3)

    rifle_asalto_shot = pygame.mixer.Sound('musica/M4A1_shot.wav')
    rifle_asalto_shell = pygame.mixer.Sound('musica/rifle_asalto_shell.wav')
    rifle_asalto_shell.set_volume(0.3)

    escopeta_shot = pygame.mixer.Sound('musica/escopeta_shot.wav')
    escopeta_shell = pygame.mixer.Sound('musica/escopeta_shell.wav')
    escopeta_shell.set_volume(0.3)

    mp5_shot = pygame.mixer.Sound('musica/mp5_shot.wav')

    buy_sound = pygame.mixer.Sound('musica/compra.wav')


def render():
    ventana.fill((0, 0, 0))
    for p in paredes:
        p.dibujar()

    for w in wallbuy:
        w.dibujar()

    for p in piso:
        p.dibujar()

    for s in spawn:
        s.dibujar()

    for p in puertas:
        p.dibujar()

    for z in zombies:
        z.dibujar()

    # HUD Y JUGADOR

    # Salud del Jugador
    pygame.draw.rect(ventana, (0, 0, 0), (250, HEIGHT - 50, 400, 40))
    if j.vida > 0:
        pygame.draw.rect(ventana, (0, 255, 0), (260, HEIGHT - 45, (j.vida * 3.8) // 1, 30))

    # Puntos
    score = fuente_chica.render(f'$ {j.puntos}', 1, (255, 255, 255))
    ventana.blit(score, (30, 460))

    # Ronda
    if not ronda.entre_ronda:
        ronda_label = fuente_grande.render(f'RONDA {ronda.actual}', 1, (255, 0, 0))
    else:
        ronda_label = fuente_grande.render(f'RONDA {ronda.actual}', 1, (255, 255, 0))
    ventana.blit(ronda_label, (10, 10))

    # Arma
    nomb = fuente_chica.render(j.arma.nombre, 1, (255, 255, 255))
    ventana.blit(nomb, (30, 500))
    balas = fuente_grande.render(f'{j.arma.cargador}/{j.arma.reserva}', 1, (255, 255, 255))
    ventana.blit(balas, (30, 530))

    # CargadAAor
    if j.arma.cargador == 0 and not j.arma.recargando:
        if j.arma.reserva:
            rec = fuente_chica.render('SIN MUNICIÓN...PRESIONÁ [R]', 1, (255, 0, 0))
            ventana.blit(rec, (250, 500))
        else:
            rec = fuente_chica.render('SIN MUNICIÓN', 1, (255, 0, 0))
            ventana.blit(rec, (340, 500))

    if 0 < j.arma.cargador <= j.arma.cargador_total // 3 and not j.arma.recargando:
        if j.arma.reserva:
            rec = fuente_chica.render('MUNICIÓN BAJA...PRESIONÁ [R]', 1, (255, 255, 255))
            ventana.blit(rec, (230, 500))
        else:
            rec = fuente_chica.render('MUNICIÓN BAJA', 1, (255, 255, 255))
            ventana.blit(rec, (340, 500))

    if j.arma.recargando:
        rec = fuente_chica.render('RECARGANDO...', 1, (255, 255, 255))
        ventana.blit(rec, (330, 500))

    # Jugador
    if j.arma.disparando:
        pygame.draw.rect(ventana, (255, 255, 0), (j.pos[X] - HITBOX // 2, j.pos[Y] - HITBOX // 2, HITBOX * 2, HITBOX * 2))
    else:
        pygame.draw.rect(ventana, (0, 255, 0), (j.pos[X], j.pos[Y], HITBOX, HITBOX))


def mover():
    for p in paredes:
        p.pos[X] += j.vel[X]
        p.pos[Y] += j.vel[Y]

    for w in wallbuy:
        w.pos[X] += j.vel[X]
        w.pos[Y] += j.vel[Y]

    for p in puertas:
        p.pos[X] += j.vel[X]
        p.pos[Y] += j.vel[Y]

    for z in zombies:
        z.pos[X] += j.vel[X]
        z.pos[Y] += j.vel[Y]

        if z.vel[X]:
            if z.vel[X] > 0:
                if not z.hit[ESTE]:
                    z.pos[X] += z.vel[X]
            elif not z.hit[OESTE]:
                z.pos[X] += z.vel[X]

        if z.vel[Y]:
            if z.vel[Y] > 0:
                if not z.hit[SUR]:
                    z.pos[Y] += z.vel[Y]
            elif not z.hit[NORTE]:
                z.pos[Y] += z.vel[Y]

    for p in piso:
        p.pos[X] += j.vel[X]
        p.pos[Y] += j.vel[Y]

    for s in spawn:
        s.pos[X] += j.vel[X]
        s.pos[Y] += j.vel[Y]


def hit_detect(p, ent):
    p.cerca = False

    # Eje x
    if ent.pos[X] + ent.HITBOX >= p.pos[X] and ent.pos[X] <= p.pos[X] + p.HITBOX:

        # Norte
        if p.pos[Y] + p.HITBOX - 3 <= ent.pos[Y] <= p.pos[Y] + p.HITBOX + 3:
            ent.hit[NORTE] = 1
            p.cerca = True

        # Sur
        if p.pos[Y] - 3 <= ent.pos[Y] + ent.HITBOX <= p.pos[Y] + 3:
            ent.hit[SUR] = 1
            p.cerca = True

    # Eje y
    if ent.pos[Y] + ent.HITBOX >= p.pos[Y] and ent.pos[Y] <= p.pos[Y] + p.HITBOX:

        # Este
        if p.pos[X] - 3 <= ent.pos[X] + ent.HITBOX <= p.pos[X] + 3:
            ent.hit[ESTE] = 1
            p.cerca = True

        # Oeste
        if p.pos[X] + p.HITBOX - 3 <= ent.pos[X] <= p.pos[X] + p.HITBOX + 3:
            ent.hit[OESTE] = 1
            p.cerca = True


def start_up(estructuras):
    global paredes, puertas, piso, spawn, wallbuy
    paredes = []
    puertas = []
    piso = []
    spawn = []
    wallbuy = []

    for i in estructuras:
        if len(i) == 2:
            paredes.append(Pared(i[X], i[Y]))
        elif i[2] == 0:
            spawn.append(Piso(i[X], i[Y], i[2]))
        elif i[2] == 1:
            puertas.append(Puerta(i[X], i[Y]))
        elif i[2] == 2:
            piso.append(Piso(i[X], i[Y], i[2]))
        elif i[2] >= 3:
            wallbuy.append(Wallbuy(i[X], i[Y], i[2]))

    return paredes, puertas, piso, spawn, wallbuy


def compra(w):
    print(f'{w.arma.nombre} Pos: {w.rel}')
    for a in j.inventario:
        if a.nombre == w.arma.nombre:
            if a.reserva < a.reserva_total and j.puntos >= w.precio // 2:
                print(f'Compra BALAS de {a.nombre}')
                a.reserva = a.reserva_total
                w.comprado = w.precio // 2
                w.sonido.play()
            return

    if j.puntos >= w.precio:
        if len(j.inventario) == 1:
            j.inventario.append(w.arma)
            j.arma = j.inventario[1]
            j.arma.reserva = j.arma.reserva_total
            j.arma.cargador = j.arma.cargador_total
            w.comprado = w.precio
            w.sonido.play()

        for i in range(len(j.inventario)):
            h = j.inventario[i]
            if h.nombre == j.arma.nombre:
                j.inventario[i] = w.arma
                j.arma = j.inventario[i]
                j.arma.reserva = j.arma.reserva_total
                j.arma.cargador = j.arma.cargador_total
                w.comprado = w.precio
                w.sonido.play()


# =============================================================================================
# PRINCIPAL
# =============================================================================================


def main():
    global ventana, j, WIDTH, HEIGHT, paredes, puertas, piso, zombies, spawn, \
        estructuras_init, ronda, fuente_grande, fuente_chica, zombies_muertos, wallbuy
    pygame.init()

    # INICIANDO VENTANA
    pygame.display.set_caption('Supervivencia Zombie')
    ventana = pygame.display.set_mode((WIDTH, HEIGHT))
    cargar_texturas()
    cargar_sonido()

    clock = pygame.time.Clock()

    # INICIANDO VARIABLES

    # Estructuras
    estructuras_init = generate_level('mapa_1.txt')
    paredes, puertas, piso, spawn, wallbuy = start_up(estructuras_init)
    zombies = []
    zombies_muertos = []

    # Texto
    fuente_grande = pygame.font.SysFont(None, 60)
    fuente_chica = pygame.font.SysFont(None, 40)

    # Jugador
    j = Jugador()

    # Ronda
    ronda = Ronda()

    # ----------------------------------------------------------------------------------
    # MAINLOOP
    # ----------------------------------------------------------------------------------

    run = True

    while run:

        # EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Cambio de arma
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q and len(j.inventario) > 1:
                if j.arma.recargando:
                    j.arma.recargando = False
                if j.arma == j.inventario[0]:
                    j.arma = j.inventario[1]
                else:
                    j.arma = j.inventario[0]

        # DETECTAR NUEVA RONDA
        if not len(zombies) and not ronda.entre_ronda:
            ronda.actual += 1
            print('RONDA', ronda.actual, '\n')
            ronda.zombies_ronda = ronda.actual * 3
            ronda.nueva_ronda = pygame.time.get_ticks() + 9000
            ronda.entre_ronda = True
            j.vida = 100

            if ronda.actual in (7, 10, 13, 15):
                ronda.zombies_cap = ronda.actual

        while len(zombies) < ronda.zombies_cap and ronda.zombies_ronda and ronda.nueva_ronda < pygame.time.get_ticks():
            ronda.entre_ronda = False
            random_spawn = random.choice(spawn)
            zombies.append(Zombie(random_spawn.pos[X], random_spawn.pos[Y]))
            ronda.zombies_ronda -= 1
            print(f'Zombie generado en cordenadas ({random_spawn.pos[X]}, {random_spawn.pos[Y]})')

        # COLISIONES
        j.hit = [0, 0, 0, 0]

        # Zombies muertos
        for i in reversed(zombies_muertos):
            del zombies[i]
            j.puntos += 100
        zombies_muertos = []

        # Vida
        if j.vida <= 0:
            print('JUGADOR MUERTO')
            run = False

        # Paredes
        for p in paredes:
            hit_detect(p, j)

        # WallBuys
        for w in wallbuy:
            hit_detect(w, j)
            if w.cerca and pygame.mouse.get_pressed()[2] and j.last_buy < pygame.time.get_ticks():
                compra(w)

                if w.comprado:
                    j.puntos -= w.comprado
                    j.last_buy = pygame.time.get_ticks() + 1500
                    w.comprado = 0
                    break

        # Puertas
        for p in puertas:
            if p.activo:
                hit_detect(p, j)

            # Abrir Puertas
            if p.cerca and pygame.mouse.get_pressed()[2] and j.puntos >= 500 and p.activo:
                p.activo = False
                buy_sound.play()
                j.puntos -= 500

        # Arma
        j.arma.disparando = False
        j.arma.is_ready()

        # CONTROLES
        j.vel = [0, 0]
        teclas = pygame.key.get_pressed()

        # Movimiento
        if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and not j.hit[NORTE]:
            j.vel[Y] = 4
            if teclas[pygame.K_RSHIFT] or teclas[pygame.K_LSHIFT]:
                j.vel[Y] += 2
        if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and not j.hit[SUR]:
            j.vel[Y] = -4
            if teclas[pygame.K_RSHIFT] or teclas[pygame.K_LSHIFT]:
                j.vel[Y] -= 2
        if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and not j.hit[OESTE]:
            j.vel[X] = 4
            if teclas[pygame.K_RSHIFT] or teclas[pygame.K_LSHIFT]:
                j.vel[X] += 2
        if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and not j.hit[ESTE]:
            j.vel[X] = -4
            if teclas[pygame.K_RSHIFT] or teclas[pygame.K_LSHIFT]:
                j.vel[X] -= 2

        # Disparo
        if pygame.mouse.get_pressed()[0] and j.arma.ready and j.arma.cargador:
            disparo = pygame.mouse.get_pos()
            j.arma.disparo(disparo[X], disparo[Y], zombies)

        # Recargar
        if teclas[pygame.K_r]:
            j.arma.recargar()
        if j.arma.recargando:
            j.arma.recargar()

        # Test
        if teclas[pygame.K_SPACE]:
            print(f'Jugador: ({j.pos[X]}, {j.pos[Y]})\tZombie: ({zombies[0].pos[X]}, {zombies[0].pos[Y]})')

        # UPDATE
        render()
        mover()

        # Zombies
        for i in range(len(zombies)):
            z = zombies[i]
            if not z.vivo:
                zombies_muertos.append(i)
                continue

            z.hit = [0, 0, 0, 0]
            for p in paredes:
                hit_detect(p, z)
            z.direccion()

            if not z.cansado:
                z.catch()
            else:
                z.descansar()
                if z.lastimado:
                    j.puntos += 10
                    z.lastimado = False
            if z.golpe:
                j.vida -= 30
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
