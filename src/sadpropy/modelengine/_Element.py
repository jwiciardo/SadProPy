import openseespy.opensees as ops

class Elements:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager
    
    def create(self):
        FrameSections_dict = self.ws.framesections
        Sec_Fiber_dict = self.ws.sec_fiber
        Sec_Aggregator_dict = self.ws.sec_aggregator
        AnalysisSettings = self.ws.analysis_settings
        PDelta = AnalysisSettings['P-Delta']
        NonlinearAnalysis = AnalysisSettings['Nonlinear Analysis']
        ElementOffset_dict = self.ws.elementoffset
        
        # Column
        TransfType = 'PDelta' if PDelta == 1 else 'Linear'
        ElementCol_dict = self.ws.elementscol
        for SectionName, data in ElementOffset_dict.items():
            iOffsetLength, jOffsetLength = data['Offset Length (I)'], data['Offset Length (J)']
            if data['Element Type'] == 'Column':
                iend_offset = (0.0, 0.0, iOffsetLength)
                jend_offset = (0.0, 0.0, -jOffsetLength)
            TransfTag = self.tag.add('Transformation', f"{SectionName}_{TransfType}")
                         # transfType, transfTag, *vecxz (X, Y, Z), '-jntOffset', *dI (X, Y, Z), *dJ (X, Y, Z)
            ops.geomTransf(TransfType, TransfTag, *(0, 1, 0),       '-jntOffset', *iend_offset,  *jend_offset) # Local Z of the section towards Global Y +ve

        for ElementTag, data in ElementCol_dict.items():
            inode, jnode, BaseSection, NLSection, ElementType = data['I'], data['J'], data['Base Section'], data['NL Section'], data['Element Type']
            if NLSection in Sec_Aggregator_dict:
                NLSection = Sec_Aggregator_dict[NLSection]['Aggregated Section']
            elif NLSection in Sec_Fiber_dict or NLSection in FrameSections_dict:
                pass
            SectionTag = self.tag.get_tag('Section', f"{BaseSection}")
            TransfTag = self.tag.get_tag('Transformation', f"{BaseSection}_{TransfType}")
            if NonlinearAnalysis == 0 or NLSection == BaseSection:
                 # eleType: 'elasticBeamColumn', eleTag,     *eleNodes,       secTag,     transfTag, '-mass', mass
                ops.element('elasticBeamColumn', ElementTag, *(inode, jnode), SectionTag, TransfTag, '-mass', 0.0) # Creating Element objects for Linear Analysis
            else:
                IntegrationTag = self.tag.get_tag('Integration', f"{NLSection}")
                 # eleType: 'forceBeamColumn', eleTag,     *eleNodes,       transfTag, integrationTag, '-mass', mass
                ops.element('forceBeamColumn', ElementTag, *(inode, jnode), TransfTag, IntegrationTag, '-mass', 0.0) # Creating Element objects for Nonlinear Analysis
            self.tag.store('Element', ElementTag, f"{ElementTag}")
            
        # Beam X
        ElementBeamX_dict = self.ws.elementsbeamx
        for SectionName, data in ElementOffset_dict.items():
            iOffsetLength, jOffsetLength = data['Offset Length (I)'], data['Offset Length (J)']
            if data['Element Type'] == 'Beam':
                iend_offset = (iOffsetLength, 0.0, 0.0)
                jend_offset = (-jOffsetLength, 0.0, 0.0)
            TransfTag = self.tag.add('Transformation', f"{SectionName}_X")
             # transfType: 'Linear', transfTag, *vecxz (X, Y, Z), '-jntOffset', *dI (X, Y, Z), *dJ (X, Y, Z)   
            ops.geomTransf('Linear', TransfTag, *(0, -1, 0),      '-jntOffset', *iend_offset,  *jend_offset) # Local Z of the section towards Global Y -ve

        for ElementTag, data in ElementBeamX_dict.items():
            inode, jnode, BaseSection, NLSection, ElementType = data['I'], data['J'], data['Base Section'], data['NL Section'], data['Element Type']
            if NLSection in Sec_Aggregator_dict:
                NLSection = Sec_Aggregator_dict[NLSection]['Aggregated Section']
            elif NLSection in Sec_Fiber_dict or NLSection in FrameSections_dict:
                pass
            SectionTag = self.tag.get_tag('Section', f"{BaseSection}")
            TransfTag = self.tag.get_tag('Transformation', f"{BaseSection}_X")
            if NonlinearAnalysis == 0 or NLSection == BaseSection:
                 # eleType: 'elasticBeamColumn', eleTag,     *eleNodes,       secTag,     transfTag, '-mass', mass
                ops.element('elasticBeamColumn', ElementTag, *(inode, jnode), SectionTag, TransfTag, '-mass', 0.0) # Creating Element objects for Linear Analysis
            else:
                IntegrationTag = self.tag.get_tag('Integration', f"{NLSection}")
                 # eleType: 'forceBeamColumn', eleTag,     *eleNodes,       transfTag, integrationTag, '-mass', mass
                ops.element('forceBeamColumn', ElementTag, *(inode, jnode), TransfTag, IntegrationTag, '-mass', 0.0) # Creating Element objects for Nonlinear Analysis
            self.tag.store('Element', ElementTag, f"{ElementTag}")
        
        # Beam Y
        ElementBeamY_dict = self.ws.elementsbeamy
        for SectionName, data in ElementOffset_dict.items():
            iOffsetLength, jOffsetLength = data['Offset Length (I)'], data['Offset Length (J)']
            if data['Element Type'] == 'Beam':
                iend_offset = (0.0, iOffsetLength, 0.0)
                jend_offset = (0.0, -jOffsetLength, 0.0)
            TransfTag = self.tag.add('Transformation', f"{SectionName}_Y")
             # transfType: 'Linear', transfTag, *vecxz (X, Y, Z), '-jntOffset', *dI (X, Y, Z), *dJ (X, Y, Z)   
            ops.geomTransf('Linear', TransfTag, *(1, 0, 0),       '-jntOffset', *iend_offset,  *jend_offset) # Local Z of the section towards Global X +ve

        for ElementTag, data in ElementBeamY_dict.items():
            inode, jnode, BaseSection, NLSection, ElementType = data['I'], data['J'], data['Base Section'], data['NL Section'], data['Element Type']
            if NLSection in Sec_Aggregator_dict:
                NLSection = Sec_Aggregator_dict[NLSection]['Aggregated Section']
            elif NLSection in Sec_Fiber_dict or NLSection in FrameSections_dict:
                pass
            SectionTag = self.tag.get_tag('Section', f"{BaseSection}")
            TransfTag = self.tag.get_tag('Transformation', f"{BaseSection}_Y")
            if NonlinearAnalysis == 0 or NLSection == BaseSection:
                 # eleType: 'elasticBeamColumn', eleTag,     *eleNodes,       secTag,     transfTag, '-mass', mass
                ops.element('elasticBeamColumn', ElementTag, *(inode, jnode), SectionTag, TransfTag, '-mass', 0.0) # Creating Element objects for Linear Analysis
            else:
                IntegrationTag = self.tag.get_tag('Integration', f"{NLSection}")
                 # eleType: 'forceBeamColumn', eleTag,     *eleNodes,       transfTag, integrationTag, '-mass', mass
                ops.element('forceBeamColumn', ElementTag, *(inode, jnode), TransfTag, IntegrationTag, '-mass', 0.0) # Creating Element objects for Nonlinear Analysis
            self.tag.store('Element', ElementTag, f"{ElementTag}")

        Element_dict = ElementCol_dict | ElementBeamX_dict | ElementBeamY_dict # Combining elements dictionary
        Nodes_to_Element_dict = {} # Predefined Nodes to element dictionary
        for ElementTag, (inode, jnode, BaseSection, NLSection, ElementType) in Element_dict.items():
            Nodes = tuple(sorted((inode, jnode)))
            Nodes_to_Element_dict[Nodes] = ElementTag # Storing element tag for each nodes
        return Element_dict, Nodes_to_Element_dict