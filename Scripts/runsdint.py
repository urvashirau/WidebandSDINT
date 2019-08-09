import pylab as pl
execfile('../Scripts/sdint_imager.py')

## Suggested runs : 

## Remove the mask (set mask='' in the onetest method below) to trigger divergence
##            Note that INT-only or specmode='cube' runs diverge easily without a mask. 
##            Note that joint reconstructions (wideband or sdint) do not need the mask. 


def runtest(num=1):

    print num

    if num==1:
        ## One pointing, Wideband Multi-Term Imaging. 
        ## SD+INT data
        ## Source intensity and spectral index are accurate at all spatial scales.
        ## No primary beams in the simulation or imaging
        onetest(runtype='SinglePointing',
                specmode='mfs', 
                usedata='sdint')

    if num==2:
        ## One pointing, Wideband Multi-Term Imaging.
        ## INT-only data
        ## Source intensity is low and spectral index is completely wrong at large scales
        ## No primary beams in the simulation or imaging
        onetest(runtype='SinglePointing',
                specmode='mfs', 
                usedata='intonly')

    if num==3:
        ## One pointing, Wideband Multi-Term Imaging.
        ## SD-only data
        ## Example of wide-band multi-term deconvolution on SD data alone.
        ## No primary beams in the simulation or imaging
        onetest(runtype='SinglePointing',
                specmode='mfs', 
                usedata='sdonly')

    if num==4:
        ## One pointing, Spectral Cube imaging 
        ## SD+INT data
        ## Source intensity and spectral index are accurate at all spatial scales.
        ## No primary beams in the simulation or imaging
        onetest(runtype='SinglePointing',
                specmode='cube', 
                usedata='sdint')

    if num==5:
        ## One pointing, Wideband Multi-Term Imaging.
        ## INT-only data
        ## Source intensity is low and spectral index is completely wrong at large scales
        ## No primary beams in the simulation or imaging
        onetest(runtype='SinglePointing',
                specmode='cube', 
                usedata='intonly')

    if num==6:
        ## One pointing, Wideband Multi-Term Imaging.
        ## SD-only data
        ## Example of wide-band multi-term deconvolution on SD data alone.
        ## No primary beams in the simulation or imaging
        onetest(runtype='SinglePointing',
                specmode='cube', 
                usedata='sdonly')

    elif num==7:
        ## 25 pointing mosaic, Wideband Multi-Term Imaging.
        ## Source intensity and spectral index are accurate at all spatial scales.
        onetest(runtype='Mosaic',
                specmode='mfs', 
                usedata='sdint')

    if num==8:
        ## 25 pointing mosaic, Wideband Multi-Term Imaging.
        ## INT-only data
        ## Source intensity is low and spectral index is too steep (but better than with the single pointing uv-coverage)
        onetest(runtype='Mosaic',
                specmode='mfs', 
                usedata='intonly')

    if num==9:
        ## 25 pointing mosaic, Wideband Multi-Term Imaging.
        ## SD-only data
        ## Should be the same as the single pointing run, but just operating under mosaic mode with INT PB manipulations
        onetest(runtype='Mosaic',
                specmode='mfs', 
                usedata='sdonly')

    if num==10:
        ## 25 pointing mosaic, Spectral Cube imaging 
        ## SD+INT data
        ## Source intensity and spectral index are accurate at all spatial scales.
        onetest(runtype='Mosaic',
                specmode='cube', 
                usedata='sdint')

    if num==11:
        ## 25 pointing mosaic,  Spectral Cube Imaging
        ## INT-only data
        ## Source intensity is low and spectral index is completely wrong at large scales. Diverges easily.
        onetest(runtype='Mosaic',
                specmode='cube', 
                usedata='intonly')

    if num==12:
        ## 25 pointing mosaic, Spectral Cube Imaging.
        ## SD-only data
        onetest(runtype='Mosaic',
                specmode='cube', 
                usedata='sdonly')


def onetest(runtype='SinglePointing', specmode='mfs', usedata='sdint', action='run'):
    
    if runtype == 'SinglePointing':
        vis = '../Data/papersky_standard.ms'
        sdimage = '../Data/papersky_standard.sdimage'
        sdpsf = '../Data/papersky_standard.sdpsf'
        gridder='standard'    ## Prolate spheroidal gridding
        mask='../Data/papersky_standard.true.im.masklist'
        imsize=800
        pblimit=-0.1   ## Use a negative sign to prevent a T/F mask from being applied at the pblimit.
        jointname = 'try_standard'
        
    else:     
        vis = '../Data/papersky_mosaic.ms'
        sdimage = '../Data/papersky_mosaic.sdimage'
        sdpsf = '../Data/papersky_mosaic.sdpsf'
        gridder='mosaic'
        mask='../Data/papersky_mosaic.true.im.masklist'
        imsize=1500
        pblimit=0.1  ## This is applied to the mosaic PB
        jointname = 'try_mosaic'
        
        
    #### Algorithm settings

    ## Iteration Control 
    niter=1000
    cycleniter= 200

    ## If using only INT data, it can diverge, so reduce the cycleniter to trigger more major cycles
    if usedata=='intonly':
        cycleniter=20

    ## Choose the deconvolver based on the spectral setting
    if specmode=='mfs':
        deconvolver='mtmfs'
    else:
        deconvolver='multiscale'
    
    ## Construct the image name
    imagename = jointname+'_'+specmode+'_'+deconvolver+'_'+usedata

    if action=='run':

        print 'Running Imaging for : ', imagename
    
        os.system('rm -rf '+imagename+'*')
        jointim = SDINT_imager(vis=vis,
                           
                           sdimage=sdimage,
                           sdpsf=sdpsf,
                           sdgain=1.0,
                           dishdia=100.0, # in meters
                          
                           usedata=usedata,  ## 'sdonly' or 'intonly' or 'sdint'
                           
                           imagename=imagename,
                           imsize=imsize,
                           cell='9.0arcsec',
                           phasecenter='J2000 19:59:28.500 +40.44.01.50',
                           weighting='natural',
                           #robust=2,
                           specmode=specmode,
                           start='',
                           spw='',
                           gridder=gridder,
                           nchan=3,
                           reffreq='1.5GHz',
                           width='',
                           pblimit=pblimit, 
                           interpolation='nearest',
                           wprojplanes=1,
                           
                           deconvolver=deconvolver,
                           scales=[0,12,20,40,60,80,100],
                           nterms=2,
                           pbmask=0.2,
                           
                           niter=niter,
                           cycleniter=cycleniter,
                           threshold=0.0,
                           mask=mask)
    

        decname = jointim.do_reconstruct()

    if action=='plot' or action=='run':

        pl.clf()

        print 'Displaying images for ', imagename
        labname = runtype + '.' + specmode + '.' + usedata

        if specmode=='cube':
            pl.subplot(131)
            dispim(imname = imagename+'.joint.cube.image', chan=0 )
            pl.title(labname+' : Int(chan0)')
            pl.subplot(132)
            dispim(imname = imagename+'.joint.cube.image', chan=1 )
            pl.title(labname+' : Int(chan1)')
            pl.subplot(133)
            dispim(imname = imagename+'.joint.cube.image', chan=2 )
            pl.title(labname+' : Int(chan2)')
            
        if specmode=='mfs':
            pl.subplot(121)
            dispim(imname = imagename+'.joint.multiterm.image.tt0' )
            pl.title(labname+' : Intensity')
            pl.subplot(122)
            dispim(imname = imagename+'.joint.multiterm.alpha' )
            pl.title(labname+' : Alpha')

        pl.savefig('fig.'+imagename+'.png')

###################################

def dispim(imname='',subplot=111,chan=0, vmin=0.0, vmax=1.0):
    print 'Opening', imname
    
    ia.open(imname)
    pix = ia.getchunk()
    ia.close()

    vmin=0.0
    vmax=1.0

    if imname.count('mosaic')==0:
        arr = pix[:,:,0,chan]
    else:
        arr = pix[350:1150, 350:1150, 0, chan]
    
    if imname.count('sdonly')>0:
        vmax=5.0

    if imname.count('alpha')==0:
        pl.imshow(pl.rot90(  np.sign(arr)*np.sqrt(np.fabs(arr)) ), interpolation=None,cmap='jet',vmin=vmin, vmax=vmax)
    else:
        pl.imshow(pl.rot90(  arr ), interpolation=None,cmap='jet',vmin=-3.0, vmax=1.0)
        

#    pl.imshow(pl.rot90(pix[:,:,chan,0]), interpolation=None,cmap='jet')
    pl.colorbar()

