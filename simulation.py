import argparse
import time

import numpy as np

from boids import *


def animate(env, region):
    import matplotlib.pyplot as plt
    from matplotlib import animation

    plt.rcParams['animation.html'] = 'html5'

    def animate(i, scat, env):
        env.update(ARGS.dt)

        scat.set_offsets([boid.position for boid in env.population])
        return scat,

    xmin, xmax, ymin, ymax = region

    fig, ax = plt.subplots()
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal')

    scat = ax.scatter([], [])

    for goal in env.goals:
        ax.scatter(*goal.position, color='g')
    for obstacle in env.obstacles:
        if not isinstance(obstacle, Wall):
            ax.scatter(*obstacle.position, color='r')

    anim = animation.FuncAnimation(fig, animate,
                                   fargs=(scat, env),
                                   frames=ARGS.steps, interval=20, blit=True)

    anim.save(ARGS.save_name+'.gif', dpi=80, writer='imagemagick')


def main():
    region = (-100, 100, -100, 100)
    env = Environment2D(region)
    for _ in range(ARGS.agents):
        env.add_agent(Boid.random(
            100, 15, comfort_zone=3, speed_cap=15, ndim=2))

    goal = Goal(np.random.uniform(-50, 50, 2), ndim=2)
    env.add_goal(goal)
    # Create a sphere obstacle within in +/- 50 of goal's position.
    sphere = Sphere(np.random.uniform(-40, 40, 2) + goal.position, 3, ndim=2)
    env.add_obstacle(sphere)

    if ARGS.animation:  # Generate animation
        animate(env, region)
    else:  # Generate data
        position_data_all = []
        velocity_data_all = []

        prev_time = time.time()
        for i in range(ARGS.instances):
            if i % 100 == 0:
                print('Simulation {}/{}... {:.1f}s'.format(i,
                                                           ARGS.instances, time.time()-prev_time))
                prev_time = time.time()

            position_data = []
            velocity_data = []
            for _ in range(ARGS.steps):
                env.update(ARGS.dt)
                position_data.append([goal.position for goal in env.goals] +
                                     [sphere.position] +
                                     [boid.position for boid in env.population])
                velocity_data.append([np.zeros(2) for goal in env.goals] +
                                     [np.zeros(2)] +
                                     [boid.velocity for boid in env.population])

            position_data_all.append(position_data)
            velocity_data_all.append(velocity_data)

        if ARGS.data_transpose:
            # position_data_all shape: [instances, steps, agents, ndims]
            # After transposition: [instances, agents, steps, ndims]
            position_data_all = np.transpose(position_data_all, ARGS.data_transpose)
            velocity_data_all = np.transpose(velocity_data_all, ARGS.data_transpose)

        print('Simulations {0}/{0} completed.'.format(ARGS.instances))

        np.save('data/'+ARGS.save_name+'_position.npy', position_data_all)
        np.save('data/'+ARGS.save_name+'_velocity.npy', velocity_data_all)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', type=int, default=100,
                        help='number of agents')
    parser.add_argument('--steps', type=int, default=1000,
                        help='number of simulation steps')
    parser.add_argument('--instances', type=int, default=1,
                        help='number of simulation instances')
    parser.add_argument('--dt', type=float, default=0.1,
                        help='time resolution')
    parser.add_argument('--animation', action='store_true',
                        help='whether animation is generated')
    parser.add_argument('--save-name', type=str,
                        help='name of the save file')
    parser.add_argument('--data-transpose', type=int, nargs=4, default=None,
                        help='axes for data transposition')

    ARGS = parser.parse_args()

    main()
