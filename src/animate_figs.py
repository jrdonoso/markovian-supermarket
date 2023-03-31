import imageio

images = []

for k in range(20):
    filename = f"./figs/anim_{k}.png" 
    images.append(imageio.imread(filename))

imageio.mimsave('supermarket_animation.gif', images, fps=1)