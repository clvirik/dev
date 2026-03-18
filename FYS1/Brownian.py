import pygame
import random
import math
import heapq
import subprocess
import numpy as np
from collections import defaultdict
import imageio_ffmpeg

WIDTH, HEIGHT = 900, 700
NUM_SMALL = 1000

SMALL_RADIUS = 4
BIG_RADIUS = 50

SMALL_MASS = 1
BIG_MASS = 50

MAX_SPEED = 500

FPS = 60
VIDEO_SECONDS = 20
TOTAL_FRAMES = FPS * VIDEO_SECONDS

CELL_SIZE = BIG_RADIUS*2

# ---------------- HEADLESS PYGAME ----------------
pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))  # Off-screen surface

BLACK=(0,0,0)
BLUE=(120,160,255)
RED=(255,120,120)

# ---------------- VIDEO ENCODER ----------------
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg = subprocess.Popen(
    [
        ffmpeg_path,
        "-y",
        "-f","rawvideo",
        "-vcodec","rawvideo",
        "-pix_fmt","rgb24",
        "-s",f"{WIDTH}x{HEIGHT}",
        "-r",str(FPS),
        "-i","-",
        "-an",
        "-vcodec","libx264",
        "-preset","ultrafast",
        "-crf","18",
        "-pix_fmt","yuv420p",
        "brownian_motion.mp4"
    ],
    stdin=subprocess.PIPE
)

# ---------------- PARTICLE & EVENT CLASSES ----------------
class Particle:
    def __init__(self,x,y,vx,vy,radius,mass,color):
        self.x=x; self.y=y
        self.vx=vx; self.vy=vy
        self.radius=radius; self.mass=mass
        self.color=color
        self.collisions=0

    def move(self,dt):
        self.x += self.vx*dt
        self.y += self.vy*dt

    def draw(self):
        pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),self.radius)

    def cell(self):
        return int(self.x//CELL_SIZE), int(self.y//CELL_SIZE)

class Event:
    def __init__(self,time,a,b):
        self.time=time; self.a=a; self.b=b
        self.countA=a.collisions if a else -1
        self.countB=b.collisions if b else -1

    def valid(self):
        if self.a and self.a.collisions!=self.countA: return False
        if self.b and self.b.collisions!=self.countB: return False
        return True

    def __lt__(self,other):
        return self.time < other.time

# ---------------- PARTICLE SYSTEM ----------------
particles=[]
grid = defaultdict(list)

def rebuild_grid():
    grid.clear()
    for p in particles:
        grid[p.cell()].append(p)

def neighbors(p):
    cx,cy = p.cell()
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            yield from grid[(cx+dx,cy+dy)]

# ---------------- PHYSICS ----------------
def time_to_hit(a,b):
    if a is b: return math.inf
    dx=b.x-a.x; dy=b.y-a.y
    dvx=b.vx-a.vx; dvy=b.vy-a.vy
    dvdr=dx*dvx+dy*dvy
    if dvdr>0: return math.inf
    dvdv=dvx*dvx+dvy*dvy
    drdr=dx*dx+dy*dy
    sigma=a.radius+b.radius
    d=dvdr*dvdr - dvdv*(drdr-sigma*sigma)
    if d<0: return math.inf
    return -(dvdr+math.sqrt(d))/dvdv

def time_to_vertical_wall(p):
    if p.vx>0: return (WIDTH-p.x-p.radius)/p.vx
    elif p.vx<0: return (p.radius-p.x)/p.vx
    return math.inf

def time_to_horizontal_wall(p):
    if p.vy>0: return (HEIGHT-p.y-p.radius)/p.vy
    elif p.vy<0: return (p.radius-p.y)/p.vy
    return math.inf

def bounce(a,b):
    dx=b.x-a.x; dy=b.y-a.y
    dvx=b.vx-a.vx; dvy=b.vy-a.vy
    dvdr=dx*dvx+dy*dvy
    dist=a.radius+b.radius
    J=2*a.mass*b.mass*dvdr/((a.mass+b.mass)*dist)
    Jx=J*dx/dist; Jy=J*dy/dist
    a.vx += Jx/a.mass; a.vy += Jy/a.mass
    b.vx -= Jx/b.mass; b.vy -= Jy/b.mass
    a.collisions+=1; b.collisions+=1

def bounce_vertical(p): p.vx*=-1; p.collisions+=1
def bounce_horizontal(p): p.vy*=-1; p.collisions+=1

def predict(p,pq,current_time):
    if not p: return
    for other in neighbors(p):
        dt=time_to_hit(p,other)
        if dt!=math.inf:
            heapq.heappush(pq,Event(current_time+dt,p,other))
    dt=time_to_vertical_wall(p)
    if dt!=math.inf: heapq.heappush(pq,Event(current_time+dt,p,None))
    dt=time_to_horizontal_wall(p)
    if dt!=math.inf: heapq.heappush(pq,Event(current_time+dt,None,p))

# ---------------- CREATE PARTICLES ----------------
for i in range(NUM_SMALL):
    while True:
        x=random.uniform(50,WIDTH-50)
        y=random.uniform(50,HEIGHT-50)
        ok=True
        for p in particles:
            if math.hypot(x-p.x,y-p.y) < p.radius+SMALL_RADIUS: ok=False; break
        if ok:
            vx=random.uniform(-MAX_SPEED,MAX_SPEED)
            vy=random.uniform(-MAX_SPEED,MAX_SPEED)
            particles.append(Particle(x,y,vx,vy,SMALL_RADIUS,SMALL_MASS,BLUE))
            break

particles.append(Particle(WIDTH/2,HEIGHT/2,0,0,BIG_RADIUS,BIG_MASS,RED))
rebuild_grid()

# ---------------- EVENT SYSTEM ----------------
pq=[]; sim_time=0
for p in particles: predict(p,pq,sim_time)

# ---------------- SIMULATION LOOP (HEADLESS) ----------------
frame_dt = 1/FPS
for frame_count in range(TOTAL_FRAMES):
    target_time = (frame_count+1)*frame_dt

    while pq and pq[0].time <= target_time:
        event=heapq.heappop(pq)
        if not event.valid(): continue
        dt = event.time - sim_time
        for p in particles: p.move(dt)
        sim_time = event.time
        rebuild_grid()
        a,b = event.a,event.b
        if a and b: bounce(a,b)
        elif a: bounce_vertical(a)
        elif b: bounce_horizontal(b)
        predict(a,pq,sim_time)
        predict(b,pq,sim_time)

    # move remaining time
    dt = target_time - sim_time
    for p in particles: p.move(dt)
    sim_time = target_time
    rebuild_grid()

    # draw frame
    screen.fill(BLACK)
    for p in particles: p.draw()

    frame = pygame.surfarray.array3d(screen)
    frame = np.transpose(frame,(1,0,2))
    ffmpeg.stdin.write(frame.astype(np.uint8).tobytes())

# ---------------- CLEANUP ----------------
pygame.quit()
ffmpeg.stdin.close()
ffmpeg.wait()
print("Saved brownian_motion.mp4")