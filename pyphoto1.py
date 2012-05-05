import sys, math, os
from Tkinter import *
from tkFileDialog import SaveAs, Directory

import Image                                  # PIL Image: also in Tkinter
from ImageTk import PhotoImage                # PIL photo widget replacement
from viewer_thumbs import makeThumbs          # developed earlier in book

# remember last dirs across all windows
saveDialog = SaveAs(title='Save As (filename gives image type)')
openDialog = Directory(title='Select Image Directory To Open')
appname = 'PyPhoto 1.0: '

# testing 123

class ScrolledCanvas(Canvas):
    """
    a canvas in a container that automatically makes
    vertical and horizontal scroll bars for itself
    """
    def __init__(self, container):
        Canvas.__init__(self, container)
        self.config(borderwidth=0)
        vbar = Scrollbar(container)
        hbar = Scrollbar(container, orient='horizontal')

        vbar.pack(side=RIGHT,  fill=Y)                 # pack canvas after bars
        hbar.pack(side=BOTTOM, fill=X)                 # so clipped first
        self.pack(side=TOP, fill=BOTH, expand=YES)

        vbar.config(command=self.yview)                # call on scroll move
        hbar.config(command=self.xview)
        self.config(yscrollcommand=vbar.set)           # call on canvas move
        self.config(xscrollcommand=hbar.set)


class ViewOne(Toplevel):
    """
    open a single image in a pop-up window when created;
    a class because photoimage obj must be saved, else
    erased if reclaimed; scroll if too big for display;
    on mouse clicks, resizes to window's height or width:
    stretches or shrinks; on I/O keypress, zooms in/out;
    both resizing schemes maintain original aspect ratio;
    code is factored to avoid redundancy here as possible;
    """
    def __init__(self, imgdir, imgfile, forcesize=( )):
        Toplevel.__init__(self)
        helptxt = '(click L/R or press I/O to resize, S to save, D to open)'
        self.title(appname + imgfile + '  ' + helptxt)
        imgpath = os.path.join(imgdir, imgfile)
        imgpil  = Image.open(imgpath)
        self.canvas = ScrolledCanvas(self)
        self.drawImage(imgpil, forcesize)
        self.canvas.bind('<Button-1>', self.onSizeToDisplayHeight)
        self.canvas.bind('<Button-3>', self.onSizeToDisplayWidth)
        self.bind('<KeyPress-i>',      self.onZoomIn)
        self.bind('<KeyPress-o>',      self.onZoomOut)
        self.bind('<KeyPress-s>',      self.onSaveImage)
        self.bind('<KeyPress-d>',      onDirectoryOpen)
        self.focus( )

    def drawImage(self, imgpil, forcesize=( )):
        imgtk = PhotoImage(image=imgpil)                  # not file=imgpath
        scrwide, scrhigh = forcesize or self.maxsize( )   # wm screen size x,y
        imgwide  = imgtk.width( )                         # size in pixels
        imghigh  = imgtk.height( )                        # same as imgpil.size

        fullsize = (0, 0, imgwide, imghigh)              # scrollable
        viewwide = min(imgwide, scrwide)                 # viewable
        viewhigh = min(imghigh, scrhigh)

        canvas = self.canvas
        canvas.delete('all')                             # clear prior photo
        canvas.config(height=viewhigh, width=viewwide)   # viewable window size
        canvas.config(scrollregion=fullsize)             # scrollable area size
        canvas.create_image(0, 0, image=imgtk, anchor=NW)

        if imgwide <= scrwide and imghigh <= scrhigh:    # too big for display?
            self.state('normal')                         # no: win size per img
        elif sys.platform[:3] == 'win':                  # do windows fullscreen
            self.state('zoomed')                         # others use geometry( )
        self.saveimage = imgpil
        self.savephoto = imgtk                           # keep reference on me
        print (scrwide, scrhigh), imgpil.size

    def sizeToDisplaySide(self, scaler):
        # resize to fill one side of the display
        imgpil = self.saveimage
        scrwide, scrhigh = self.maxsize( )                 # wm screen size x,y
        imgwide, imghigh = imgpil.size                     # img size in pixels
        newwide, newhigh = scaler(scrwide, scrhigh, imgwide, imghigh)
        if (newwide * newhigh < imgwide * imghigh):
            filter = Image.ANTIALIAS                      # shrink: antialias
        else:                                             # grow: bicub sharper
            filter = Image.BICUBIC
        imgnew  = imgpil.resize((newwide, newhigh), filter)
        self.drawImage(imgnew)

    def onSizeToDisplayHeight(self, event):
        def scaleHigh(scrwide, scrhigh, imgwide, imghigh):
            newhigh = scrhigh
            newwide = int(scrhigh * (float(imgwide) / imghigh))
            return (newwide, newhigh)
        self.sizeToDisplaySide(scaleHigh)

    def onSizeToDisplayWidth(self, event):
        def scaleWide(scrwide, scrhigh, imgwide, imghigh):
            newwide = scrwide
            newhigh = int(scrwide * (float(imghigh) / imgwide))
            return (newwide, newhigh)
        self.sizeToDisplaySide(scaleWide)

    def zoom(self, factor):
        # zoom in or out in increments
        imgpil = self.saveimage
        wide, high = imgpil.size
        if factor < 1.0:                     # antialias best if shrink
            filter = Image.ANTIALIAS         # also nearest, bilinear
        else:
            filter = Image.BICUBIC
        new = imgpil.resize((int(wide * factor), int(high * factor)), filter)
        self.drawImage(new)

    def onZoomIn(self, event, incr=.10):
        self.zoom(1.0 + incr)
    def onZoomOut(self, event, decr=.10):
        self.zoom(1.0 - decr)

    def onSaveImage(self, event):
        # save current image state to file
        filename = saveDialog.show( )
        if filename:
           self.saveimage.save(filename)


def onDirectoryOpen(event):
    """
    open a new image directory in new pop up
    available in both thumb and img windows
    """
    dirname = openDialog.show( )
    if dirname:
        viewThumbs(dirname, kind=Toplevel)


def viewThumbs(imgdir, kind=Toplevel, numcols=None, height=400, width=500):
    """
    make main or pop-up thumbnail buttons window;
    uses fixed-size buttons, scrollable canvas;
    sets scrollable (full) size, and places
    thumbs at abs x,y coordinates in canvas;
    no longer assumes all thumbs are same size:
    gets max of all (x,y), some may be smaller;
    """
    win = kind( )
    helptxt = '(press D to open other)'
    win.title(appname + imgdir + '  ' + helptxt)
    quit = Button(win, text='Quit', command=win.quit, bg='beige')
    quit.pack(side=BOTTOM, fill=X)
    canvas = ScrolledCanvas(win)
    canvas.config(height=height, width=width)       # init viewable window size
                                                    # changes if user resizes
    thumbs = makeThumbs(imgdir)                     # [(imgfile, imgobj)]
    numthumbs = len(thumbs)
    if not numcols:
        numcols = int(math.ceil(math.sqrt(numthumbs)))  # fixed or N x N
    numrows = int(math.ceil(numthumbs / float(numcols)))

    # thumb=(name, obj), thumb.size=(width, height)
    linksize = max([max(thumb[1].size) for thumb in thumbs])
    print linksize
    fullsize = (0, 0,                                   # upper left  X,Y
        (linksize * numcols), (linksize * numrows) )    # lower right X,Y
    canvas.config(scrollregion=fullsize)                # scrollable area size

    rowpos = 0
    savephotos = []
    while thumbs:
        thumbsrow, thumbs = thumbs[:numcols], thumbs[numcols:]
        colpos = 0
        for (imgfile, imgobj) in thumbsrow:
            photo   = PhotoImage(imgobj)
            link    = Button(canvas, image=photo)
            handler = (lambda savefile=imgfile: ViewOne(imgdir, savefile))
            link.config(command=handler, width=linksize, height=linksize)
            link.pack(side=LEFT, expand=YES)
            canvas.create_window(colpos, rowpos, anchor=NW,
                    window=link, width=linksize, height=linksize)
            colpos += linksize
            savephotos.append(photo)
        rowpos += linksize
    win.bind('<KeyPress-d>', onDirectoryOpen)
    win.savephotos = savephotos
    return win


if __name__ == '__main__':
    """
    open dir = default or cmdline arg
    else show simple window to select
    """
    imgdir = 'images'
    if len(sys.argv) > 1: imgdir = sys.argv[1]
    if os.path.exists(imgdir):
        mainwin = viewThumbs(imgdir, kind=Tk)
    else:
        mainwin = Tk( )
        mainwin.title(appname + 'Open')
        handler = lambda: onDirectoryOpen(None)
        Button(mainwin, text='Open Image Directory', command=handler).pack( )
    mainwin.mainloop( )
