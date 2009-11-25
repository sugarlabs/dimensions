# -*- coding: utf-8 -*-
#Copyright (c) 2009, Walter Bender

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

RED_STROKE = "#FF0000"
RED_FILL = "#FF9090"
BLUE_STROKE = "#0000FF"
BLUE_FILL = "#9090FF"
GREEN_STROKE = "#00D000"
GREEN_FILL = "#90D090"
PURPLE_STROKE = "#FF00FF"
PURPLE_FILL = "#FF90FF"

color_pairs = ([RED_STROKE,RED_FILL],
               [GREEN_STROKE,GREEN_FILL],
               [BLUE_STROKE,BLUE_FILL],
               [PURPLE_STROKE,PURPLE_FILL])

fill_styles = ("none","gradient","solid")

card_types = ("X","O","C")

def background(f):
    f.write("<rect width=\"74.5\" height=\"124.5\" rx=\"11\" ry=\"9\" x=\"0.25\" y=\"0.25\"\n")
    f.write("style=\"fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:0.5\" />\n")

def header(f):
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    f.write("<!-- Created with Emacs -->\n")
    f.write("<svg\n")
    f.write("   xmlns:svg=\"http://www.w3.org/2000/svg\"\n")
    f.write("   xmlns=\"http://www.w3.org/2000/svg\"\n")
    f.write("   version=\"1.0\"\n")
    f.write("   width=\"75\"\n")
    f.write("   height=\"125\">\n")
    background(f)
    f.write("<g>\n")

def footer(f):
    f.write("</g>\n")
    f.write("</svg>\n")

def circle(f, y, style, stroke, fill):
    f.write("<circle cx=\"27\" cy=\"11\" r=\"8\"\n")
    f.write("   transform=\"matrix(1.9,0,0,1.9,-15," + str(y) + ")\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:" + stroke + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    f.write("<circle cx=\"27\" cy=\"11\" r=\"8\"\n")
    f.write("   transform=\"matrix(0.9,0,0,0.9,12.5," + str(y+11) + ")\"\n")
    f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
            ";stroke-width:3.5;\" />\n")

def check(f, y, style, stroke, fill):
    f.write("<path d=\"m 28.3575,70.160499 -5.861,5.861 -5.861,-5.866001 -4.102,-4.1 c -0.747,-0.747999 -1.212,-1.784999 -1.212,-2.93 0,-2.288998 1.854,-4.145998 4.146,-4.145998 1.143,0 2.18,0.465 2.93,1.214 l 4.099,4.101999 14.102,-14.102998 c 0.754,-0.749 1.787,-1.214 2.934,-1.214 2.289,0 4.146,1.856001 4.146,4.145001 0,1.146 -0.467,2.18 -1.217,2.932 l -14.104,14.104997 z\"\n")
    f.write("   transform=\"translate(10," + str(y-40) + ")\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:" + stroke + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")

def cross(f, y, style, stroke, fill):
    f.write("<path d=\"m 33.3585,62.5035 10.102,10.1 c 0.752,0.75 1.217,1.783 1.217,2.932 0,2.287 -1.855,4.143 -4.146,4.143 -1.145,0 -2.178,-0.463 -2.932,-1.211 l -10.102,-10.103 -10.1,10.1 c -0.75,0.75 -1.787,1.211 -2.934,1.211 -2.284,0 -4.143,-1.854 -4.143,-4.141 0,-1.146 0.465,-2.184 1.212,-2.934 l 10.104,-10.102 -10.102,-10.1 c -0.747,-0.748 -1.212,-1.785 -1.212,-2.93 0,-2.289 1.854,-4.146 4.146,-4.146 1.143,0 2.18,0.465 2.93,1.214 l 10.099,10.102 10.102,-10.103 c 0.754,-0.749 1.787,-1.214 2.934,-1.214 2.289,0 4.146,1.856 4.146,4.145 0,1.146 -0.467,2.18 -1.217,2.932 l -10.104,10.105 z\"\n")
    f.write("   transform=\"translate(10," + str(y-40) + ")\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:" + stroke + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")

def check_card(f, n, style, stroke, fill):
    if n == 1:
       check(f, 41.5,style, stroke, fill)
    elif n == 2:
       check(f, 21.5,style, stroke, fill)
       check(f, 61.5,style, stroke, fill)
    else:
       check(f, 1.5,style, stroke, fill)
       check(f, 41.5,style, stroke, fill)
       check(f, 81.5,style, stroke, fill)

def cross_card(f, n, style, stroke, fill):
    if n == 1:
       cross(f, 41.5,style, stroke, fill)
    elif n == 2:
       cross(f, 21.5,style, stroke, fill)
       cross(f, 61.5,style, stroke, fill)
    else:
       cross(f, 1.5,style, stroke, fill)
       cross(f, 41.5,style, stroke, fill)
       cross(f, 81.5,style, stroke, fill)

def circle_card(f, n, style, stroke, fill):
    if n == 1:
       circle(f, 41.5,style, stroke, fill)
    elif n == 2:
       circle(f, 21.5,style, stroke, fill)
       circle(f, 61.5,style, stroke, fill)
    else:
       circle(f, 1.5,style, stroke, fill)
       circle(f, 41.5,style, stroke, fill)
       circle(f, 81.5,style, stroke, fill)

def open_file(i):
    return file("images/card-"+str(i)+".svg", "w")

def close_file(f):
    f.close()

i = 0
for t in card_types:
    for c in color_pairs:
        for n in range(1,4):
            for s in fill_styles:
                i += 1
                f = open_file(i)
                header(f)
                if t == "O":
                    circle_card(f,n,s,c[0],c[1])
                elif t == "C":
                    check_card(f,n,s,c[0],c[1])
                else:
                    cross_card(f,n,s,c[0],c[1])
                footer(f)
                close_file(f)
