'''
The app is based and an improvment of this little script i wrote a while back
'''

import os
from pdf2image import convert_from_path
from PIL import Image


def img2img(file, output, format = 'jpg'):
    if os.path.exists(output + '.' +format):
        pass
    else:
        img = Image.open(file)
        img.save(output + '.' +format)

def img2pdf(file, output):
    if os.path.exists(output + '.pdf'):
        pass
    else:
        img = Image.open(file)
        pdf = img.convert("RGB")
        pdf.save(output + '.pdf')

def pdf2img(file, output):
    if os.path.exists(output + '.jpg'):
        pass
    else:
        pdfs = convert_from_path(file)
        
        for i, pdf in enumerate(pdfs):
                pdf.save(output + '.jpeg', 'jpeg')
                pdf.save(output + '.png', 'png')

    
cwd = os.getcwd()
files = os.listdir()

for file in files:
    split = file.split('.') 
    if split[-1] == "jpg":
        img2img(file, split[0], format='png')
        img2img(file, split[0], format='jpeg')
        img2pdf(file, split[0])
    elif split[-1] == "png":
        img2img(file, split[0], format ='jpg')
        img2img(file, split[0], format ='jpeg')
        img2pdf(file, split[0])
    elif split[-1] == "jpeg":
        img2img(file, split[0], format ='png')
        img2img(file, split[0], format ='jpg')
        img2pdf(file, split[0])
    elif split[-1] == 'pdf':
        pdf2img(file, split[0])
        
        
print("all images  and pdf converted")

'''
open the folder, get the name of all the files, convert images to pdf and if image is jpg then in png else opposite.
'''

