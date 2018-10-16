import psutil
from PIL import Image
from math import log2

# set this if you don't want it to eat up your system's memory
MAX_MEM = psutil.virtual_memory().total
class MemoryPredictor:
    def __init__(self):
        self.prev = psutil.virtual_memory().used
        self.iteration = 0
        self.average_slope = 0
    def predict(self):
        current = psutil.virtual_memory().used
        self.average_slope = (self.iteration * self.average_slope + log2(current)-log2(self.prev)) / (self.iteration+1)
        self.prev = current
        self.iteration += 1
        return current * pow(2,self.average_slope)

def step(clip,canvas,verbose,squish):
    if squish:
        clip = clip.resize((x//2,y//2))
    x,y = clip.size
    mask = None
    if canvas:
        if clip.mode == 'RGBA':
            mask = clip
        canvas = canvas.resize((x*2,y*2))
    else:
        canvas = Image.new(clip.mode,(x*2,y*2))
    canvas.paste(clip,(x//2,0),mask)
    if verbose:
        print("Top triangle pasted")
    canvas.paste(clip,(0,y)   ,mask)
    if verbose:
        print("Bottom left triangle pasted")
    canvas.paste(clip,(x,y)   ,mask)
    if verbose:
        print("Bottom right triangle pasted")
    return canvas

def sierpinski(seed,iterations,recursive_background,verbose,no_squish,max_dim):
    if max_dim:
        max_x,max_y = max_dim
    pred = MemoryPredictor()
    triangle = seed
    in_bounds = True
    squish = False
    for i in range(iterations):
        if verbose:
            print("Iteration: {}".format(i))
        if recursive_background:
            canvas = seed
        else:
            canvas = None
        triangle = step(triangle,canvas,verbose,squish)
        ram_usage = pred.predict()
        if verbose:
            print("Predicted RAM usage for next iteration: {:,} bytes".format(ram_usage))
        cur_x,cur_y = triangle.size
        if max_dim:
            in_bounds = (cur_x*2 < max_x and cur_y*2 < max_y)
        if (ram_usage > MAX_MEM) or not in_bounds:
            if no_squish:
                return triangle
            else:
                print("Triangle will now be squished due to RAM limit")
                squish = True
    return triangle

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-W','--max-width',help='Max width in pixels')
    parser.add_argument('-H','--max-height',help='Max height in pixels')
    parser.add_argument('-r','--resize-input',metavar = 'dim',help = 'resize input image to W * H',type = int,nargs = 2)
    parser.add_argument('-y','--recursive-background', action = 'store_true', help = 'backdrop for subtriangles is the input image')
    parser.add_argument('-v','--verbose',action = 'store_true',help = 'verbosity (helps with REALLY big images that take ages and eat memory)')
    parser.add_argument('-o','--output',help = 'output filename (Note: this will infuence output image format as well)')
    parser.add_argument('-q','--no-squish',action = 'store_true',help = "don't squish when out of memory")
    parser.add_argument('input',help = 'input image used as template')
    parser.add_argument('iterations',help = 'number of steps to take',type = int)
    args = parser.parse_args()
    print(args)
    if args.output:
        filename = args.output
    else:
        filename = 'output.png'
    seed = Image.open(args.input)
    final = sierpinski(seed,args.iterations,args.recursive_background,args.verbose,args.no_squish,(args.max_width,args.max_height))
    final.save(filename)