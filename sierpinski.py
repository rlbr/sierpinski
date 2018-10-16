import psutil
import time
from PIL import Image
from threading import Thread
from numpy import exp
from scipy.optimize import curve_fit


# set this if you don't want it to eat up your system's memory
MAX_MEM = psutil.virtual_memory().total * .8
mem_vals = []
def get_total_memu():
    info  = psutil.virtual_memory()
    return info.total-info.available
class AsyncMemReader:
    def __init__(self,tick = 1):
        self.collecting = False
        self.collected_values = []
        self.tick = tick
        self.thread = None
    def collect(self):
        self.thread = Thread(target = self._collect_)
        self.thread.start()
    def _collect_(self):
        self.collecting = True
        while self.collecting:
            self.collected_values.append(
                get_total_memu()
            )
            time.sleep(self.tick)
    def read(self):
        self.collecting = False
        self.thread.join()
        ret = self.collected_values
        self.collected_values = []
        return ret
history = []
def func(x,a,b,c):
    return c + exp(a*x + b)
class MemoryPredictor(AsyncMemReader):
    def __init__(self,tick=1):
        super().__init__(tick)
        self.y = [get_total_memu()]
        self.coffs = None
    def predict(self):
        val = max(self.read())
        self.y.append(val)
        history.append(val)
        y = self.y
        x = list(range(len(y)))
        if len(y) >= 4:
            self.coffs = curve_fit(func,x,y)[0]
            return round(func(len(x)+1,*self.coffs))
        else:
            return 0
def step(clip,canvas,verbose,squish):
    x,y = clip.size
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

def sierpinski(seed,iterations,recursive_background,verbose,no_squish,max_dim,step=step):
    pred = MemoryPredictor(tick=.25)
    triangle = seed
    in_bounds = True
    squish = False
    if max_dim:
        max_x,max_y = max_dim
    for i in range(iterations):
        if squish:
            pred.reset()
        if verbose:
            print("Iteration: {}".format(i))

        if recursive_background:
            canvas = seed
        else:
            canvas = None
        pred.collect()

        triangle = step(triangle,canvas,verbose,squish)

        ram_usage = pred.predict()

        if verbose:
            print("Predicted RAM usage during next iteration: {:,} bytes".format(ram_usage))

        if max_dim:
            cur_x,cur_y = triangle.size
            in_bounds = (cur_x*2 < max_x and cur_y*2 < max_y)

        if (ram_usage > MAX_MEM) or not in_bounds:
            print("Triangle will now be squished due to RAM limit/bounds")
            if no_squish:
                if input("Quit? (y/n): ") == 'y':
                    return triangle,pred
            else:
                squish = input("Try without squishing? (y/n): ") != 'y'
    return triangle,pred

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-z','--max-size',nargs = 2,help='Max size in W * H')
    parser.add_argument('-r','--resize-input',metavar = 'dim',help = 'resize input image to W * H',type = int,nargs = 2)
    parser.add_argument('-y','--recursive-background', action = 'store_true', help = 'backdrop for subtriangles is the input image')
    parser.add_argument('-v','--verbose',action = 'store_true',help = 'verbosity (helps with REALLY big images that take ages and eat memory)')
    parser.add_argument('-o','--output',help = 'output filename (Note: this will infuence output image format as well)')
    parser.add_argument('-q','--no-squish',action = 'store_true',help = "save current result instead of squishing")
    parser.add_argument('input',help = 'input image used as template')
    parser.add_argument('iterations',help = 'number of steps to take',type = int)
    args = parser.parse_args()
    print(args)
    if args.output:
        filename = args.output
    else:
        filename = 'output.png'
    seed = Image.open(args.input)
    final,pred = sierpinski(seed,args.iterations,args.recursive_background,args.verbose,args.no_squish,args.max_size)
    if args.verbose:
        print("Saving as {}".format(filename))
    final.save(filename)
    with open('mem_vals.txt','w') as file:
        file.write(
            '\n'.join(
                map(str,history)
                )
            )