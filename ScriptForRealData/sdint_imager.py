from imagerhelpers.imager_base import PySynthesisImager
from imagerhelpers.input_parameters import ImagerParameters
execfile('sdint_helper.py')

class SDINT_imager:
    """
    Joint imaging of Single Dish and Interferometer Data

    Use Cases :
        Input Data : Joint SD+INT data,  SD-only data,  INT-only data (i.e. tclean)
        Spectral Modes : Spectral Cubes and Continuum (Multi-term) 

    Image Names : 
        Interferometer images : imagename.int.{residual,psf,image}.* 
        Single Dish images : imagename.sd.{residual,psf}
        Joint images : imagename.joint.{residual,psf}

    """

    def __init__(self,

                  ## Data Selection - Interferometer
                 vis='Data/mysky.ms',
                 field='',
                 spw='',

                 ## Single Dish Data - Images
                 sdimage='',
                 sdpsf='',
                 sdgain=1.0,
                 dishdia=100.0,

                 ## Pick what data to use. 'int' or 'sd' or 'sdint'
                 usedata = 'sdint',
                 ## Image Definition
                 imagename='',
                 imsize=512,
                 cell='10.0arcsec',
                 phasecenter='',
                 weighting='natural',
                 specmode='cube',

                 ## Gridding/Imaging options for Cubes
                 gridder='standard',
                 nchan=3,
                 reffreq='1.5GHz',
                 width = '',
                 pblimit=0.2,
                 interpolation='nearest',
                 wprojplanes=1,

                 ## Imaging/Deconvolution options for Multi-term continuum.
                 deconvolver='hogbom',
                 scales=[],
                 nterms=2,
                 pbmask=0.2,

                 ## Iteration control
                 niter=10,
                 cycleniter=200,
                 threshold='',
                 mask='' ):

        ## Data Selection - Interferometer
        self.vis=vis
        self.field=field
        self.spw=spw

        ## Single Dish Data - Images
        self.sdimage=sdimage
        self.sdpsf=sdpsf
        self.sdgain=sdgain
        self.dishdia=dishdia

        ## What mode to run in
        self.usedata=usedata

        ## Image Definition
        self.imagename=imagename
        self.imsize=imsize
        self.cell=cell
        self.phasecenter=phasecenter
        self.weighting=weighting
        self.specmode=specmode

        ## Gridding/Imaging options for Cubes
        self.gridder=gridder
        self.nchan=nchan
        self.reffreq=reffreq
        self.width = width
        self.pblimit=pblimit
        self.interpolation=interpolation
        self.wprojplanes=wprojplanes
        
        ## Imaging/Deconvolution options for Multi-term continuum.
        self.deconvolver=deconvolver
        self.scales=scales
        self.nterms=nterms
        self.pbmask=pbmask
        
        ## Iteration control
        self.niter=niter
        self.cycleniter=cycleniter
        self.threshold=threshold
        self.mask=mask

        ############# Internal variables
        self.imagertool  = None
        self.deconvolvertool = None
        self.lib = SDINT_helper()
        
        self.applypb=False
        if self.gridder=='mosaic' or gridder=='awproject':
            self.applypb=True
 
    def setup_imager(self,imagename=''):
        """
        Cube imaging for major cycles.
        """
        params = ImagerParameters(msname=self.vis, field=self.field,spw=self.spw,
                                  imagename=imagename,
                                  imsize=self.imsize, cell=self.cell, phasecenter=self.phasecenter, 
                                  weighting=self.weighting,
                                  gridder=self.gridder, pblimit=self.pblimit,wprojplanes=self.wprojplanes,
                                  specmode='cube',nchan=self.nchan, 
                                  reffreq=self.reffreq, width=self.width, interpolation=self.interpolation,
                                  deconvolver='hogbom', niter=0,
                                  wbawp=True)
        
        self.imagertool = PySynthesisImager(params=params)
        self.imagertool.initializeImagers()
        self.imagertool.initializeNormalizers()
        self.imagertool.setWeighting()

        self.imagertool.makePSF()
        self.imagertool.makePB()
        self.imagertool.runMajorCycle()
        
        self.lib.copy_restoringbeam(fromthis=imagename+'.psf', tothis=imagename+'.residual')


    def setup_deconvolver(self,imagename=''):
        """
        Cube or MFS minor cycles. 
        """
        params = ImagerParameters(msname=self.vis, field=self.field,spw=self.spw,
                                  imagename=imagename,
                                  imsize=self.imsize, cell=self.cell, phasecenter=self.phasecenter, 
                                  weighting=self.weighting,
                                  gridder=self.gridder, pblimit=self.pblimit,wprojplanes=self.wprojplanes,
                                  specmode=self.specmode,nchan=self.nchan, 
                                  reffreq=self.reffreq, width=self.width,interpolation=self.interpolation,
                                  deconvolver=self.deconvolver, scales=self.scales,nterms=self.nterms,
                                  niter=self.niter,cycleniter=self.cycleniter, threshold=self.threshold,
                                  mask=self.mask,interactive=False)
        
        self.deconvolvertool = PySynthesisImager(params=params)

        ## Why are we initializing these ? 
        self.deconvolvertool.initializeImagers()
        self.deconvolvertool.initializeNormalizers()
        self.deconvolvertool.setWeighting()

        
        ### These three should be unncessary.  Need a 'makeimage' method for csys generation. 
        self.deconvolvertool.makePSF() ## Make this to get a coordinate system
        self.deconvolvertool.makePB()  ## Make this to turn .weight into .pb maps
        self.deconvolvertool.runMajorCycle() ## Make this to make template residual images.

        ## Initialize deconvolvers. ( Order is important. This cleans up a leftover tablecache image.... FIX!)
        self.deconvolvertool.initializeDeconvolvers()
        self.deconvolvertool.initializeIterationControl()

    
    def setup_sdimaging(self,template='',output=''):
        """
        Make the SD cube Image and PSF

        Option 1 : Use/Regrid cubes for the observed image and PSF
        Option 2 : Make the SD image and PSF cubes using 'tsdimager's usage of the SD gridder option.

        Currently, only Option 1 is supported. 

        """
        
        ## Regrid the input SD image and PSF cubes to the target coordinate system. 
        imregrid(imagename=self.sdpsf, template=template+'.psf', 
                 output=output+'.psf',overwrite=True,axes=[0,1])
        imregrid(imagename=self.sdimage, template=template+'.residual', 
                 output=output+'.residual',overwrite=True,axes=[0,1])
        imregrid(imagename=self.sdimage, template=template+'.residual', 
                 output=output+'.image',overwrite=True,axes=[0,1])

        ## Apply the pbmask from the INT image cube, to the SD cubes.
        #TTB: Create *.mask cube  

        self.lib.addmask(inpimage=output+'.residual', pbimage=template+'.pb', pblimit=self.pblimit)
        self.lib.addmask(inpimage=output+'.image', pbimage=template+'.pb', pblimit=self.pblimit)


    def do_reconstruct(self):

        ## Image names
        int_cube = self.imagename+'.int.cube'
        sd_cube = self.imagename+'.sd.cube'
        joint_cube = self.imagename+'.joint.cube'
        joint_multiterm = self.imagename+'.joint.multiterm'

        if self.specmode=='mfs':
            decname = joint_multiterm
        else:
            decname = joint_cube

        ## Initialize INT_imager, JOINT_deconvolver, SD_imager
        self.setup_imager(imagename=int_cube)
        self.setup_deconvolver(imagename=decname)
        self.setup_sdimaging(template=int_cube, output=sd_cube)

        ## Feather INT and SD residual images (feather in flat-sky. output has common PB)
        self.feather_residual(int_cube, sd_cube, joint_cube)
 
        ## Feather INT and SD psfs
        self.lib.feather_int_sd(sdcube=sd_cube+'.psf', 
                                intcube=int_cube+'.psf', 
                                jointcube=joint_cube+'.psf',
                                sdgain=self.sdgain,
                                dishdia=self.dishdia,
                                usedata=self.usedata)

        if self.specmode=='mfs':
            ## Calculate Spectral PSFs and Taylor Residuals
            self.lib.cube_to_taylor_sum(cubename=joint_cube+'.psf', 
                                        mtname=joint_multiterm+'.psf',
                                        nterms=self.nterms, reffreq=self.reffreq, dopsf=True)
            self.lib.cube_to_taylor_sum(cubename=joint_cube+'.residual', 
                                        mtname=joint_multiterm+'.residual',
                                        nterms=self.nterms, reffreq=self.reffreq, dopsf=False)
        
        ## Check for deconvolver convergence criteria
        self.deconvolvertool.hasConverged()
        self.deconvolvertool.updateMask()

        ## Start image reconstruction loops
        while ( not self.deconvolvertool.hasConverged() ):
            ## Run the deconvolver. It produces a joint model of the sky x fixed PB
            self.deconvolvertool.runMinorCycle()
            
            ## Prepare the joint model cube for INT and SD major cycles
            if self.specmode=='mfs':
                ## Convert Taylor model coefficients into a model cube : int_cube.model
                self.lib.taylor_model_to_cube(cubename=int_cube, ## output 
                                              mtname=joint_multiterm,  ## input
                                              nterms=self.nterms, reffreq=self.reffreq)
            else:
                ## Copy the joint_model cube to the int_cube.model
                shutil.rmtree(int_cube+'.model',ignore_errors=True)
                shutil.copytree(joint_cube+'.model', int_cube+'.model')


            if self.applypb==True:
                ## Take the int_cube.model to flat sky. 
                self.lib.modify_with_pb(inpcube=int_cube+'.model', 
                                        pbcube=int_cube+'.pb', 
                                        action='div', pblimit=self.pblimit,freqdep=False)

            ## copy the int_cube.model to the sd_cube.model
            shutil.rmtree(sd_cube+'.model',ignore_errors=True)
            shutil.copytree(int_cube+'.model', sd_cube+'.model')

            if self.applypb==True:
                ## Multiply flat-sky model with freq-dep PB
                self.lib.modify_with_pb(inpcube=int_cube+'.model', 
                                        pbcube=int_cube+'.pb', 
                                        action='mult', pblimit=self.pblimit, freqdep=True)
            ## Major cycle for interferometer data 
            self.imagertool.runMajorCycle()

            ## Major cycle for Single Dish data (uses the flat sky cube model in sd_cube.model )
            self.lib.calc_sd_residual(origcube=sd_cube+'.image', 
                                      modelcube=sd_cube+'.model', 
                                      residualcube=sd_cube+'.residual',  ## output
                                      psfcube=sd_cube+'.psf')

            ## Feather the residuals
            self.feather_residual(int_cube, sd_cube, joint_cube)

            if self.specmode=='mfs':
                ## Calculate Spectral Taylor Residuals
                self.lib.cube_to_taylor_sum(cubename=joint_cube+'.residual', 
                                            mtname=joint_multiterm+'.residual',
                                            nterms=self.nterms, reffreq=self.reffreq, dopsf=False)
 

            self.deconvolvertool.updateMask()
        
            print 'Finished a cycle'

        self.deconvolvertool.restoreImages()

        self.closeTools()

        ## PBcor for the intensity image.
        if self.applypb==True:
            if self.specmode=='mfs':
                impbcor(imagename=decname+'.image.tt0' ,  pbimage=decname+'.pb.tt0' , mode='divide', cutoff=self.pblimit,outfile=decname+'.image.tt0.pbcor')
            else:
                self.lib.modify_with_pb(inpcube=joint_cube+'.image', 
                                        pbcube=int_cube+'.pb', 
                                        action='div', pblimit=self.pblimit, freqdep=False)

        return decname

    
    def feather_residual(self,int_cube, sd_cube, joint_cube):
       
        if self.applypb==True:
            ## Take initial INT_dirty image to flat-sky. 
            self.lib.modify_with_pb(inpcube=int_cube+'.residual', 
                                    pbcube=int_cube+'.pb', 
                                    action='div',
                                    pblimit=self.pblimit,
                                    freqdep=True)
            
        ## Feather flat-sky INT dirty image with SD image
        self.lib.feather_int_sd(sdcube=sd_cube+'.residual', 
                                intcube=int_cube+'.residual', 
                                jointcube=joint_cube+'.residual', ## output
                                sdgain=self.sdgain,
                                dishdia=self.dishdia,
                                usedata=self.usedata)

        if self.applypb==True:
            ## Multiply new JOINT dirty image by a common PB to get the effect of conjbeams. 
            self.lib.modify_with_pb(inpcube=joint_cube+'.residual', 
                                pbcube=int_cube+'.pb', 
                                action='mult',
                                pblimit=self.pblimit,
                                freqdep=False)


    def closeTools(self):
        """
        Close the PySynthesisImagers
        """
        self.imagertool.deleteTools()
        self.deconvolvertool.deleteTools()


