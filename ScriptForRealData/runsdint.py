execfile('sdint_imager.py')

vis = 'papersky_mosaic.ms'
sdimage = 'papersky_mosaic.sdimage'
sdpsf = 'papersky_mosaic.sdpsf'

deconvolver='mtmfs'
specmode='mfs'
gridder='mosaic'

phasecenter='J2000 19:59:28.500 +40.44.01.50'
imsize=800
cell='9.0arcsec'
reffreq='1.5GHz'
dishdia=100.0 # in meters
niter=10000
cycleniter= 500
scales=[0,12,20,40,60,80,100]
pblimit=0.2
mythresh='.050mJy'
mask='papersky_mosaic.true.im.masklist'  ## region file, or mask image with 1,0.

#Joint reconstruction file name
jointname = 'tryit'

os.system('rm -rf '+jointname+'*')

jointim = SDINT_imager(vis=vis,
                           
                           sdimage=sdimage,
                           sdpsf=sdpsf,
                           sdgain=1.0,
                           dishdia=dishdia,

                           usedata='sdint',  ## or 'sdonly' or 'intonly'
                           
                           imagename=jointname,
                           imsize=imsize,
                           cell=cell,
                           phasecenter=phasecenter,
                           weighting='natural',
                           specmode=specmode,
                           
                           gridder=gridder,
                           nchan=3,
                           reffreq=reffreq,
                           width='',
                           pblimit=pblimit, 
                           interpolation='nearest',
                           wprojplanes=1,
                           
                           deconvolver=deconvolver,
                           scales=scales,
                           nterms=2,
                           pbmask=0.2,
                           
                           niter=niter,
                           cycleniter=cycleniter,
                           threshold=mythresh,
                           mask=mask)
    

decname = jointim.do_reconstruct()

###################################



