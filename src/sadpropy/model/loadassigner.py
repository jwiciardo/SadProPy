import openseespy.opensees as ops
from utility.constants import GRAVITY_ACCELERATION

class LoadAssigner:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager

    def _assign_gravity_load(self):
        # DEFINE AND ASSIGN LOADS
        Load_dict = self.ws.loads # Defining dictionary for each load
        wDead_roof = Load_dict['Dead Roof']['Value']
        wLive_roof = Load_dict['Live Roof']['Value']
        wDead_floor = Load_dict['Dead Floor']['Value']
        wLive_floor = Load_dict['Live Floor']['Value']
        wParapet = Load_dict['Parapet']['Value']
        wCladding = Load_dict['Cladding']['Value']

        ## Load Case and Time Series Tags
        LoadOptions = self.ws.options['Load Options']
        StoreyHeight = self.ws.storeyheight
        nStoreys = self.ws.nstoreys
        SlabElements_Storey_dict = self.ws.model['Slab Elements dict']
        SlabLoad_to_Element_TributaryLength = self.ws.model['Slabload-to-Element TributaryLength']
        EdgeElements_Storey_dict = self.ws.model['Edge Elements dict']

        ## Self-weight
        if LoadOptions['Selfweight'] == 1:
            TimeseriesTag = self.tag.add('Timeseries', 'Selfweight')
            PatternTag = self.tag.add('Pattern', 'Selfweight')
                 # tsType: 'Constant', tsTag,         '-factor', factor
            ops.timeSeries('Constant', TimeseriesTag, '-factor', 1.0) # Creating Timeseries object (Represents the relationship between time and load factor)
            # patternType: 'Plain', patternTag, tsTag
            ops.pattern('Plain',    PatternTag, TimeseriesTag) # Creating Load Pattern object
            ### Column
            ElementCol_dict = self.ws.elementscol
            for ElementTag, (inode, jnode, ElementType, SectionName, SectionNameNL) in ElementCol_dict.items():
                ioffsetLength = self.ws.elementoffset[SectionName]['Offset length (i)']
                joffsetLength = self.ws.elementoffset[SectionName]['Offset length (j)']
                A = self.ws.framesections[f"{SectionName}"]['A'] # Recalling Section area from dictionary
                unitweight = self.ws.materials[self.ws.framesections[f"{SectionName}"]['Material 1']]['Unitweight'] # Recalling unitweight of section
                          # '-ele', *eleTags,   '-type', '-beamUniform', Wy,  Wz,  Wx
                ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', 0.0, 0.0, -unitweight * A) # Assigning column weight
                    # nodeTag, *loadValues (FX, FY, FZ, MX, MY, MZ) global coordinate
                ops.load(inode, *(0.0, 0.0, -unitweight * A * ioffsetLength, 0.0, 0.0, 0.0)) # Assigning i-end rigid panel zone weight
                ops.load(jnode, *(0.0, 0.0, -unitweight * A * joffsetLength, 0.0, 0.0, 0.0)) # Assigning j-end rigid panel zone weight
            ### Beam (X Direction)
            ElementBeamX_dict = self.ws.elementsbeamx
            for ElementTag, (inode, jnode, ElementType, SectionName, SectionNameNL) in ElementBeamX_dict.items():
                ioffsetLength = self.ws.elementoffset[SectionName]['Offset length (i)']
                joffsetLength = self.ws.elementoffset[SectionName]['Offset length (j)']
                A = self.ws.framesections[f"{SectionName}"]['A'] # Recalling Section area from dictionary
                unitweight = self.ws.materials[self.ws.framesections[f"{SectionName}"]['Material 1']]['Unitweight'] # Recalling unitweight of section
                          # '-ele', *eleTags,   '-type', '-beamUniform', Wy,              Wz,  Wx
                ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -unitweight * A, 0.0, 0.0) # Assigning beam X-direction weight
                    # nodeTag, *loadValues (FX, FY, FZ, MX, MY, MZ) global coordinate
                ops.load(inode, *(0.0, 0.0, -unitweight * A * ioffsetLength, 0.0, 0.0, 0.0)) # Assigning i-end rigid panel zone weight
                ops.load(jnode, *(0.0, 0.0, -unitweight * A * joffsetLength, 0.0, 0.0, 0.0)) # Assigning j-end rigid panel zone weight
            ### Beam (Y Direction)
            ElementBeamY_dict = self.ws.elementsbeamy
            for ElementTag, (inode, jnode, ElementType, SectionName, SectionNameNL) in ElementBeamY_dict.items():
                ioffsetLength = self.ws.elementoffset[SectionName]['Offset length (i)']
                joffsetLength = self.ws.elementoffset[SectionName]['Offset length (j)']
                A = self.ws.framesections[f"{SectionName}"]['A'] # Recalling Section area from dictionary
                unitweight = self.ws.materials[self.ws.framesections[f"{SectionName}"]['Material 1']]['Unitweight'] # Recalling unitweight of section
                          # '-ele', *eleTags,   '-type', '-beamUniform', Wy,              Wz,  Wx
                ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -unitweight * A, 0.0, 0.0) # Assigning beam Y-direction weight
                    # nodeTag, *loadValues (FX, FY, FZ, MX, MY, MZ) global coordinate
                ops.load(inode, *(0.0, 0.0, -unitweight * A * ioffsetLength, 0.0, 0.0, 0.0)) # Assigning i-end rigid panel zone weight
                ops.load(jnode, *(0.0, 0.0, -unitweight * A * joffsetLength, 0.0, 0.0, 0.0)) # Assigning j-end rigid panel zone weight
            ### Slab
            SlabLoad_to_Element_Tributary_dict = self.ws.model['Slabload-to-Element Tributary dict']
            for SlabData in SlabLoad_to_Element_Tributary_dict:
                ElementTag = SlabData['Element']
                t_slab = SlabData['Thickness']
                unitweight_slab = SlabData['Unitweight']
                TributaryLength = SlabData['Tributary Length']
                          # '-ele', *eleTags,   '-type', '-beamUniform', Wy,                                          Wz,  Wx
                ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -TributaryLength * unitweight_slab * t_slab, 0.0, 0.0) # Assigning slab weight
        
        ## Superimposed Dead Load
        if LoadOptions['Superimposed Dead Load'] == 1:
            TimeseriesTag = self.tag.add('Timeseries', 'Superimposed Dead Load')
            PatternTag = self.tag.add('Pattern', 'Superimposed Dead Load')
                 # tsType: 'Constant', tsTag,         '-factor', factor
            ops.timeSeries('Constant', TimeseriesTag, '-factor', 1.0) # Creating Timeseries object (Represents the relationship between time and load factor)
            # patternType: 'Plain', patternTag, tsTag
            ops.pattern('Plain',    PatternTag, TimeseriesTag) # Creating Load Pattern object
            ### Roof and Typical Floor Dead Load
            RoofHeight = max(StoreyHeight) # Defining roof height
            for height in StoreyHeight[1:]:
                Elements = SlabElements_Storey_dict[height] # Recalling elements from dictionary
                for ElementTag in Elements:
                    TributaryLength = SlabLoad_to_Element_TributaryLength[ElementTag] # Recalling tributary length of each element
                    if height == RoofHeight:
                                 # '-ele', *eleTags,   '-type', '-beamUniform', Wy,                             Wz,  Wx
                        ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -TributaryLength * wDead_roof, 0.0, 0.0) # Assigning superimposed dead load of roof floor
                    else:
                                  # '-ele', *eleTags,   '-type', '-beamUniform', Wy,                             Wz,  Wx
                        ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -TributaryLength * wDead_floor, 0.0, 0.0) # Assigning superimposed dead load of typical floor
                
            ### Parapet and Cladding Load
            for height in StoreyHeight[1:]:
                EdgeElements = EdgeElements_Storey_dict[height] # Recalling edge elements from dictionary
                if height == RoofHeight:
                              # '-ele', *eleTags,      '-type', '-beamUniform', Wy,        Wz,  Wx
                    ops.eleLoad('-ele', *EdgeElements, '-type', '-beamUniform', -wParapet, 0.0, 0.0) # Assigning parapet weight
                else:
                              # '-ele', *eleTags,      '-type', '-beamUniform', Wy,        Wz,  Wx
                    ops.eleLoad('-ele', *EdgeElements, '-type', '-beamUniform', -wCladding, 0.0, 0.0) # Assigning cladding weight
        
        ## Live Load
        if LoadOptions['Live Load']:
            TimeseriesTag = self.tag.add('Timeseries', 'Live Load')
            PatternTag = self.tag.add('Pattern', 'Live Load')
                 # tsType: 'Constant', tsTag,         '-factor', factor
            ops.timeSeries('Constant', TimeseriesTag, '-factor', 1.0) # Creating Timeseries object (Represents the relationship between time and load factor)
            # patternType: 'Plain', patternTag, tsTag
            ops.pattern('Plain',    PatternTag, TimeseriesTag) # Creating Load Pattern object
            ### Floor Live Load
            for height in StoreyHeight[1:nStoreys]:
                Elements = SlabElements_Storey_dict[height] # Recalling elements from dictionary
                for ElementTag in Elements:
                    TributaryLength = SlabLoad_to_Element_TributaryLength[ElementTag] # Recalling tributary length of each element
                              # '-ele', *eleTags,   '-type', '-beamUniform', Wy,                             Wz,  Wx
                    ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -TributaryLength * wLive_floor, 0.0, 0.0) # Assigning live load
        
        ## Roof Live Load
        if LoadOptions['Roof Live Load'] == 1:
            TimeseriesTag = self.tag.add('Timeseries', 'Roof Live Load')
            PatternTag = self.tag.add('Pattern', 'Roof Live Load')
                 # tsType: 'Constant', tsTag,         '-factor', factor
            ops.timeSeries('Constant', TimeseriesTag, '-factor', 1.0) # Creating Timeseries object (Represents the relationship between time and load factor)
            # patternType: 'Plain', patternTag, tsTag
            ops.pattern('Plain',    PatternTag, TimeseriesTag) # Creating Load Pattern object
            ### Roof Live Load
            RoofHeight = max(StoreyHeight) # Defining roof height
            Elements = SlabElements_Storey_dict[RoofHeight]
            for ElementTag in Elements:
                TributaryLength = SlabLoad_to_Element_TributaryLength[ElementTag] # Recalling tributary length of each element
                          # '-ele', *eleTags,   '-type', '-beamUniform', Wy,                            Wz,  Wx
                ops.eleLoad('-ele', ElementTag, '-type', '-beamUniform', -TributaryLength * wLive_roof, 0.0, 0.0) # Assigning roof live load
    
    def _assign_ground_motion(self, acc_x, acc_y, dt):
        for i, value in enumerate([acc_x, acc_y]):
            TimeseriesTag = self.tag.add('Timeseries', f'Ground Motion_{i}')
            PatternTag = self.tag.add('Pattern', f'Ground Motion_{i}')
                 # tsType: 'Path', tsTag,         '-dt', dt, '-values', values, '-factor', factor, '-prependZero'
            ops.timeSeries('Path', TimeseriesTag, '-dt', dt, '-values', *value, '-factor', g,      '-prependZero') # Creating Timeseries object (Represents the relationship between time and load factor)
            # patternType: 'UniformExcitation', patternTag, dir, '-accel', accelSeriesTag
            ops.pattern('UniformExcitation',    PatternTag, i,   '-accel', TimeseriesTag) # Creating Load Pattern object
            ops.rayleigh(0.44, 0.0, 0.0, 3.601e-3)

        