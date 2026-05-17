#!/usr/bin/env python3
"""Snake - Retro Pixel Art Edition"""

import os
import pygame
import sys

import settings as S
from settings import cfg, PHASES, SH2, SB2, SO2
from snake import Snake
from food import spawn_food
from powerups import spawn_powerup, apply_powerup
from obstacles import generate_obstacles
from sounds import init_sounds, play
from highscore import hs_load, hs_save
import renderer as R
import security
from security import (auth_event, reset_auth, create_token,
                      send_magic_link, SMTPConfigError, get_smtp_config,
                      start_auth_server, stop_auth_server)

TRANSITION_MS = 2500   # phase transition announcement duration
SLOW_MS       = 5000   # slow power-up duration
N_OBSTACLES   = 12     # wall segments placed in phase 2


def _make_snakes(mode):
    s1 = Snake()
    s2 = Snake(cfg['cols'] * 3 // 4, cfg['rows'] // 2, (-1, 0)) if mode == '2p' else None
    return s1, s2


def main():
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
    except Exception:
        pass
    pygame.init()

    screen = pygame.display.set_mode((cfg['win_w'], cfg['win_h']))
    pygame.display.set_caption("Snake - Retro Edition")
    clock  = pygame.time.Clock()
    sounds = init_sounds()

    hs   = hs_load()
    best = hs[0] if hs else 0

    # ── Game state ──────────────────────────────────────────────────────────
    selected_mode = '1p'
    snake1, snake2 = _make_snakes(selected_mode)
    food      = spawn_food(snake1.body)
    obstacles = set()
    powerup   = None
    score     = 0
    score2    = 0
    speed     = cfg['base_speed']
    since_speedup = 0
    slow_end  = 0      # ms timestamp; 0 = inactive
    phase_idx = 0
    trans_start = 0    # ms timestamp of phase transition start
    new_best  = False
    winner    = None   # None=1P death, 0=draw, 1=P1 wins, 2=P2 wins
    state     = 'menu'

    # ── Auth state ──────────────────────────────────────────────────────────
    current_user   = None
    email_input    = ''
    login_error    = ''
    cursor_timer   = 0
    cursor_visible = True
    auth_port      = int(os.environ.get('AUTH_PORT', 8765))

    def reset():
        nonlocal snake1, snake2, food, obstacles, powerup
        nonlocal score, score2, speed, since_speedup, slow_end
        nonlocal phase_idx, new_best, winner, screen

        if phase_idx != 0:
            cfg.update({**PHASES[0], 'hud_h': S.HUD_H})
            screen = pygame.display.set_mode((cfg['win_w'], cfg['win_h']))
            R.clear_font_cache()
            phase_idx = 0

        snake1, snake2  = _make_snakes(selected_mode)
        occupied        = set(snake1.body + (snake2.body if snake2 else []))
        food            = spawn_food(occupied)
        obstacles       = set()
        powerup         = None
        score = score2  = 0
        speed           = cfg['base_speed']
        since_speedup   = 0
        slow_end        = 0
        new_best        = False
        winner          = None

    # ── Main loop ────────────────────────────────────────────────────────────
    while True:
        now = pygame.time.get_ticks()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                stop_auth_server()
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if state == 'login':
                    if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        addr = email_input.strip()
                        if '@' not in addr or '.' not in addr.split('@')[-1]:
                            login_error = 'INVALID EMAIL ADDRESS'
                        else:
                            try:
                                get_smtp_config()
                                reset_auth()
                                tok = create_token(addr)
                                send_magic_link(addr, tok, auth_port)
                                start_auth_server(auth_port)
                                login_error = ''
                                state = 'awaiting_auth'
                            except SMTPConfigError as e:
                                login_error = str(e)[:42]
                            except OSError:
                                login_error = f'PORT {auth_port} IN USE'
                            except Exception:
                                login_error = 'SEND FAILED - CHECK SMTP CONFIG'
                    elif ev.key == pygame.K_BACKSPACE:
                        email_input = email_input[:-1]
                        login_error = ''
                    elif ev.key == pygame.K_ESCAPE:
                        stop_auth_server()
                        pygame.quit(); sys.exit()
                    else:
                        if ev.unicode and len(email_input) < 48:
                            email_input += ev.unicode
                            login_error = ''

                elif state == 'awaiting_auth':
                    if ev.key == pygame.K_ESCAPE:
                        stop_auth_server()
                        reset_auth()
                        state = 'login'

                elif state == 'menu':
                    if ev.key in (pygame.K_UP, pygame.K_DOWN):
                        selected_mode = '2p' if selected_mode == '1p' else '1p'
                    elif ev.key == pygame.K_SPACE:
                        reset()
                        state = 'playing'
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == 'playing':
                    if   ev.key == pygame.K_UP:    snake1.steer( 0, -1)
                    elif ev.key == pygame.K_DOWN:  snake1.steer( 0,  1)
                    elif ev.key == pygame.K_LEFT:  snake1.steer(-1,  0)
                    elif ev.key == pygame.K_RIGHT: snake1.steer( 1,  0)
                    if snake2:
                        if   ev.key == pygame.K_w: snake2.steer( 0, -1)
                        elif ev.key == pygame.K_s: snake2.steer( 0,  1)
                        elif ev.key == pygame.K_a: snake2.steer(-1,  0)
                        elif ev.key == pygame.K_d: snake2.steer( 1,  0)
                    if ev.key == pygame.K_p:
                        state = 'paused'
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == 'paused':
                    if ev.key == pygame.K_p:
                        state = 'playing'
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == 'game_over':
                    if ev.key == pygame.K_SPACE:
                        reset()
                        state = 'playing'
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == 'phase_transition':
                    pass  # auto-advances after TRANSITION_MS

        # ── Update ───────────────────────────────────────────────────────────
        if state == 'playing':
            # Restore speed when slow effect expires
            if slow_end and now >= slow_end:
                speed    = min(speed * 2, cfg['max_speed'])
                slow_end = 0

            # Power-up timeout
            if powerup and powerup.expired():
                powerup = None

            snake1.step()
            if snake2:
                snake2.step()

            # ── Collision detection ──────────────────────────────────────────
            s1_dead = snake1.dead(obstacles)
            s2_dead = snake2 is not None and snake2.dead(obstacles)

            if snake2:
                # Head-on
                if snake1.head == snake2.head:
                    s1_dead = s2_dead = True
                # Cross-body
                if snake1.head in snake2.body[1:]:
                    s1_dead = True
                if snake2.head in snake1.body[1:]:
                    s2_dead = True

            if s1_dead or s2_dead:
                play(sounds, 'die')
                if snake2:
                    if s1_dead and s2_dead:
                        winner = 0
                    elif s1_dead:
                        winner = 2
                    else:
                        winner = 1
                    final = max(score, score2)
                else:
                    winner = None
                    final  = score
                hs       = hs_save(final)
                best     = hs[0] if hs else 0
                new_best = final > 0 and final == best
                state    = 'game_over'

            else:
                # ── Food eaten ───────────────────────────────────────────────
                ate = None
                if snake1.head == food:
                    ate = snake1; score += 1
                elif snake2 and snake2.head == food:
                    ate = snake2; score2 += 1

                if ate:
                    ate.eat()
                    play(sounds, 'eat')
                    since_speedup += 1

                    # Speed-up (skip while slow is active)
                    if since_speedup >= cfg['speedup_every'] and not slow_end:
                        since_speedup = 0
                        speed = min(speed + cfg['speed_increment'], cfg['max_speed'])

                    # Phase transition trigger
                    if speed >= cfg['max_speed'] and phase_idx == 0:
                        phase_idx = 1
                        cfg.update({**PHASES[1], 'hud_h': S.HUD_H})
                        screen = pygame.display.set_mode((cfg['win_w'], cfg['win_h']))
                        R.clear_font_cache()
                        snake1, snake2 = _make_snakes(selected_mode)
                        protected = set(snake1.body + (snake2.body if snake2 else []))
                        obstacles  = generate_obstacles(N_OBSTACLES, protected)
                        food       = spawn_food(protected | obstacles)
                        powerup    = None
                        slow_end   = 0
                        since_speedup = 0
                        play(sounds, 'phase_up')
                        trans_start = now
                        state = 'phase_transition'
                    else:
                        # Spawn new food and maybe a power-up
                        occupied = set(snake1.body + (snake2.body if snake2 else [])) | obstacles
                        food = spawn_food(occupied)
                        if powerup is None:
                            new_pu = spawn_powerup(occupied | ({food} if food else set()))
                            if new_pu:
                                powerup = new_pu

                # ── Power-up collected ───────────────────────────────────────
                elif powerup:
                    collector = None
                    if snake1.head == powerup.pos:
                        collector = snake1
                    elif snake2 and snake2.head == powerup.pos:
                        collector = snake2
                    if collector:
                        score, speed, slow_active = apply_powerup(powerup, collector, score, speed)
                        if slow_active:
                            slow_end = now + SLOW_MS
                        play(sounds, 'powerup')
                        powerup = None

        elif state == 'phase_transition':
            if now - trans_start >= TRANSITION_MS:
                state = 'playing'

        elif state == 'login':
            if now - cursor_timer >= 530:
                cursor_visible = not cursor_visible
                cursor_timer = now

        elif state == 'awaiting_auth':
            if auth_event.is_set():
                current_user = security.auth.authenticated_email
                stop_auth_server()
                auth_event.clear()
                state = 'menu'

        # ── Draw ─────────────────────────────────────────────────────────────
        screen.fill(S.BG)
        R.draw_grid(screen)
        R.draw_obstacles(screen, obstacles)
        R.draw_food(screen, food)
        if powerup:
            R.draw_powerup(screen, powerup)
        R.draw_snake(screen, snake1)
        if snake2:
            R.draw_snake(screen, snake2, head_color=SH2, body_color=SB2, outline_color=SO2)
        R.draw_hud(screen, score, speed, best,
                   mode=selected_mode, score2=score2 if snake2 else None,
                   user=current_user)

        if state == 'login':
            R.draw_login(screen, email_input, cursor_visible, login_error or None)
        elif state == 'awaiting_auth':
            R.draw_awaiting_auth(screen, email_input.strip())
        elif state == 'menu':
            R.draw_menu(screen, hs, selected_mode)
        elif state == 'paused':
            R.draw_pause(screen)
        elif state == 'game_over':
            R.draw_gameover(screen, score, score2, new_best, winner)
        elif state == 'phase_transition':
            R.draw_phase_transition(screen, phase_idx + 1)

        pygame.display.flip()
        clock.tick(speed if state == 'playing' else 30)


if __name__ == '__main__':
    main()
