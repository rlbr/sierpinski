from PIL import Image
def step(image,backdrop,png = True):
    dim = image.size
    if png:
        backdrop.paste(image,(dim[0]//2,0),mask = image)
        print('stage 1 done')
        backdrop.paste(image,(0,dim[1]),mask = image)
        print('stage 2 done')
        backdrop.paste(image,dim,mask = image)
        print('stage 3 done')
    else:
        backdrop.paste(image,(dim[0]//2,0))
        print('stage 1 done')
        backdrop.paste(image,(0,dim[1]))
        print('stage 2 done')
        backdrop.paste(image,dim)
        print('stage 3 done')
    return backdrop
i = Image.open(r"%userprofile%\Desktop\doge.jpg")
back = i
n = i.size
png = False
print(n)
for iteration in range(90):
    if input('Continue?:') == 'no':
        break
    print(iteration+1)
    _n = tuple(map(lambda x: x*2,n))
    print(n)
    thing = back.resize(_n)
    thing_2  = i.resize(n)
    if iteration < 9:
        print('doubled')
        n = _n
##    i.show()
    i = step(thing_2,thing,png)
i.save(r"%userprofile%\Pictures\fatdog.png")
