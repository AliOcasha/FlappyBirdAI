import pygame, neat
import os, sys
import random, time
pygame.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
gen = 0
Draw_Lines = True

Bird_Imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
 pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
 pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
print("Imported Bird Image Sequences!")
Pipe_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
print("Imported Pipe Image!")
Base_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
print("Imported Base Image!")
BG_Img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
print("Imported Background Image!")

STAT_FONT = pygame.font.SysFont("comicsans",50)

class Bird:
    IMGS = Bird_Imgs
    maxRot = 25
    Rot_Vel = 20
    Animt = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_index = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5            # Hoch fliegen
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2       #Up or Down Movement per Frame (Velocity)

        if d >= 16:
            d = 16      

        if d < 0:
            d -= 2

        self.y =  self.y + d        # Apply Movement to current position

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.maxRot:
                self.tilt = self.maxRot

        else:
            if self.tilt > -90:
                self.tilt -= self.Rot_Vel
    
    def draw(self, win):
        self.img_index += 1

        if self.img_index <= self.Animt:
            self.img = self.IMGS[0]
        elif self.img_index <= self.Animt*2:
            self.img = self.IMGS[1]
        elif self.img_index <= self.Animt*3:
            self.img = self.IMGS[2]
        elif self.img_index <= self.Animt*4:
            self.img = self.IMGS[1]
        elif self.img_index == self.Animt*4 + 1:
            self.img = self.IMGS[0]
            self.img_index = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_index = self.Animt*2

        rot_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rot_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rot_img, new_rect.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    gap = 200
    Vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(Pipe_Img, False, True)
        self.PIPE_BOTTOM = Pipe_Img

        self.passed = False

        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.Vel

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

class Base:
    Vel = 5
    Width = Base_Img.get_width()
    img = Base_Img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.Width

    def move(self):
        self.x1 -= self.Vel
        self.x2 -= self.Vel

        if self.x1 + self.Width < 0:
            self.x1 = self.x2 + self.Width

        if self.x2 + self.Width < 0:
            self.x2 = self.x1 + self.Width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    win.blit(BG_Img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: "+ str(score),1,(255,255,255))
    win.blit(text, (WIN_WIDTH-10 - text.get_width(),10))

    text = STAT_FONT.render("Gen: "+ str(gen),1,(255,255,255))
    win.blit(text, (10 ,10))

    base.draw(win)

    for bird in birds:
        if Draw_Lines == True:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                break
        bird.draw(win)

    pygame.display.update()
    

def main(genomes, config):
    global gen
    nets = []
    ge = []
    birds = []

    gen += 1
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)


    base = Base(WIN_HEIGHT-70) # 70 is height of Base
    pipes = [Pipe(700)]
   
 
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)

        pipe_ind = 0

        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break


        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(650)) # Abstand zwischen Röhren

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > WIN_HEIGHT-70 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                

        base.move()
        draw_window(win, birds, pipes, base, score, gen, pipe_ind)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,200)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NEATconfig.txt")
    run(config_path)