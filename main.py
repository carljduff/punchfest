import os
import pygame
import asyncio

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

def load_image(name, colorkey=None, scale=1):
    fullname = name
    try:
        image = pygame.image.load(fullname).convert_alpha()
        image = pygame.transform.scale_by(image, scale)
        return image, image.get_rect()
    except Exception as e:
        print(f"Failed to load image {fullname}: {e}")
        return pygame.Surface((50, 50)), pygame.Rect(0, 0, 50, 50)

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer.get_init():
        return NoneSound()

    fullname = name
    try:
        sound = pygame.mixer.Sound(fullname)
        return sound
    except Exception as e:
        print(f"Failed to load sound {fullname}: {e}")
        return NoneSound()

class Fist(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("lady.PNG", scale=0.5)
        self.fist_offset = (-235, -80)
        self.punching = False

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.topleft = pos
        self.rect.move_ip(self.fist_offset)
        if self.punching:
            self.rect.move_ip(15, 25)

    def punch(self, target):
        if not self.punching:
            self.punching = True
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        self.punching = False

class Human(pygame.sprite.Sprite):
    def __init__(self, image_file="mollie.png", scale=0.25):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image_file, scale=scale)
        screen = pygame.display.get_surface()
        if screen is None:
            screen = pygame.display.set_mode((960, 540))
        self.area = screen.get_rect()
        self.rect.topleft = 10, 90
        self.move = 18
        self.dizzy = False

    def update(self):
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        newpos = self.rect.move((self.move, 0))
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left or self.rect.right > self.area.right:
                self.move = -self.move
                newpos = self.rect.move((self.move, 0))
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect = newpos

    def _spin(self):
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = False
            self.image = self.original
        else:
            self.image = pygame.transform.rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        if not self.dizzy:
            self.dizzy = True
            self.original = self.image

async def main():
    pygame.init()
    print("Game started")
    screen = pygame.display.set_mode((960, 540))
    pygame.display.set_caption("Smack a hoe!")
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    background = background.convert()
    background.fill((106, 93, 123))

    font = pygame.font.Font(None, 64)
    text = font.render("Pummel the WHORE!!!", True, (10, 10, 10))
    textpos = text.get_rect(centerx=background.get_width() / 2, y=10)
    background.blit(text, textpos)

    screen.blit(background, (0, 0))
    pygame.display.flip()

    whiff_sound = load_sound("whiff.wav")
    punch_sound = load_sound("punch.wav")

    human = Human()
    fist = Fist()
    all_sprites = pygame.sprite.Group(human, fist)
    clock = pygame.time.Clock()

    score = 0
    bonus_started = False

    score_font = pygame.font.Font(None, 48)

    going = True
    while going:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                going = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if fist.punch(human):
                    punch_sound.play()
                    human.punched()
                    score += 1

                    if score == 3 and not bonus_started:
                        bonus_started = True
                        human.kill()
                        human = Human("bonus_human.png", scale=0.3)
                        all_sprites.empty()
                        all_sprites.add(human, fist)
                else:
                    whiff_sound.play()
            elif event.type == pygame.MOUSEBUTTONUP:
                fist.unpunch()

        all_sprites.update()

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
