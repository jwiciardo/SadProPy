from enum import IntEnum

# MATERIAL/SECTION CLASS INDEX
class MaterialType(IntEnum):
    Concrete = 0
    Steel = 1
    Spring = 2
    Aggregator = 3

class MaterialModel(IntEnum):
    Elastic = 0
    Concrete04 = 1
    Concrete04MinMax = 2
    Steel02 = 11
    Steel02MinMax = 12
    Axial = 51
    FlexuralZ = 52
    ShearY = 53
    FlexuralY = 54
    ShearZ = 55
    Torsional = 56
    IMKBilinear = 91
    IMKPeakOriented = 92
    IMKPinching = 93

class SectionShape(IntEnum):
    Rectangular = 0
    Circular = 1
    WideFlange = 2
    Channel = 3
    RectangularHollow = 4
    CircularHollow = 5

class SectionModel(IntEnum):
    Elastic = 0
    Fiber = 1
    Aggregator = 2

class IntegrationType(IntEnum):
    Lobatto = 0
    HingeRadau = 11

class ElementType(IntEnum):
    Column = 0
    Beam = 1
    Slab = 2
    Brace = 3
    ZeroLength = 11

class ConnectionEnd(IntEnum):
    I_End = 0
    J_End = 1

class NodeSource(IntEnum):
    User = 0 # Userdefined Generated source
    ZeroLength = 1 # Zero Length Auto Generated source
    PanelZone = 2 # Panel Zone Auto Generated source

class LoadCaseType:
    SW = 0
    D = 1
    L = 2
    Lr = 3
    Ex = 4
    Ey = 5
    Wx = 6
    Wy = 7

# MATERIAL PROPERTIES
class ConcreteElasticProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fc = 4
    Count = 5 # Total number of properties

class Concrete04Properties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fc = 4
    epsc = 5
    epscu = 6
    fct = 7
    et = 8
    beta = 9
    Count = 10 # Total number of properties

class Concrete04MinMaxProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fc = 4
    epsc = 5
    epscu = 6
    fct = 7
    et = 8
    beta = 9
    ecmax = 10
    etmax = 11
    Count = 12 # Total number of properties

class SteelElasticProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fy = 4
    fu = 5
    Count = 6 # Total number of properties

class Steel02Properties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fy = 4
    fu = 5
    eu = 6
    b = 7
    R0 = 8
    cR1 = 9
    cR2 = 10
    a1 = 11
    a2 = 12
    a3 = 13
    a4 = 14
    finit = 15
    Count = 16 # Total number of properties

class Steel02MinMaxProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fy = 4
    fu = 5
    eu = 6
    b = 7
    R0 = 8
    cR1 = 9
    cR2 = 10
    a1 = 11
    a2 = 12
    a3 = 13
    a4 = 14
    finit = 15
    ecmax = 16
    etmax = 17
    Count = 18 # Total number of properties

class SpringIMKBilinearProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    K0 = 4
    asPos = 5
    asNeg = 6
    MyPos = 7
    MyNeg = 8
    MuPos = 9
    MuNeg = 10
    LamdaS = 11
    LamdaC = 12
    LamdaA = 13
    LamdaK = 14
    cS = 15
    cC = 16
    cA = 17
    cK = 18
    thetapPos = 19
    thetapNeg = 20
    thetapcPos = 21
    thetapcNeg = 22
    thetauPos = 23
    thetauNeg = 24
    ResPos = 25
    ResNeg = 26
    DPos = 27
    DNeg = 28
    nFactor = 29
    Count = 30 # Total number of properties

class SpringIMKPeakOrientedProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    K0 = 4
    asPos = 5
    asNeg = 6
    MyPos = 7
    MyNeg = 8
    MuPos = 9
    MuNeg = 10
    LamdaS = 11
    LamdaC = 12
    LamdaA = 13
    LamdaK = 14
    cS = 15
    cC = 16
    cA = 17
    cK = 18
    thetapPos = 19
    thetapNeg = 20
    thetapcPos = 21
    thetapcNeg = 22
    thetauPos = 23
    thetauNeg = 24
    ResPos = 25
    ResNeg = 26
    DPos = 27
    DNeg = 28
    Count = 29 # Total number of properties

class SpringIMKPinchingProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    K0 = 4
    asPos = 5
    asNeg = 6
    MyPos = 7
    MyNeg = 8
    MuPos = 9
    MuNeg = 10
    LamdaS = 11
    LamdaC = 12
    LamdaA = 13
    LamdaK = 14
    cS = 15
    cC = 16
    cA = 17
    cK = 18
    thetapPos = 19
    thetapNeg = 20
    thetapcPos = 21
    thetapcNeg = 22
    thetauPos = 23
    thetauNeg = 24
    ResPos = 25
    ResNeg = 26
    DPos = 27
    DNeg = 28
    FprPos = 29
    FprNeg = 30
    Apinch = 31
    Count = 32 # Total number of properties

class AggregatorElasticProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    EA = 4
    EIz = 5
    GAvy = 6
    EIy = 7
    GAvz = 8
    GJxx = 9
    Count = 10 # Total number of properties

# SECTION PROPERTIES
class SectionProperties(IntEnum):
    A = 0
    Avy = 1
    Avz = 2
    Iz = 3
    Iy = 4
    Jxx = 5
    alphaY = 6
    alphaZ = 7
    AbarHoop = 8
    AbarTop = 9
    AbarBot = 10
    AbarInt = 11
    Count = 12 # Total number of properties

class RectangularElasticDimensions(IntEnum):
    h = 0
    b = 1
    Count = 2 # Total number of properties

class RectangularConcreteFiberDimensions(IntEnum):
    h = 0
    b = 1
    cover = 2
    barDiaHoop = 3
    barDiaTop = 4
    barDiaBot = 5
    barDiaInt = 6
    nBarsTop = 7
    nBarsBot = 8
    nBarsInt = 9
    Count = 10 # Total number of properties

class SlabSectionDimensions(IntEnum):
    t = 0
    Count = 1 # Total number of properties

class RectangularConcreteFiberProperties(IntEnum):
    yCore = 0
    zCore = 1
    yCover = 2
    zCover = 3
    yStartInt = 4
    yEndInt = 5
    nMeshYCore = 6
    nMeshZCore = 7
    nMeshYCover = 8
    nMeshZCover = 9
    Count = 10 # Total number of properties

class AggregatorSectionDofs(IntEnum):
    P = 0
    Mz = 1
    Vy = 2
    My = 3
    Vz = 4
    T = 5
    Count = 6 # Total number of properties

class SeismicCode(IntEnum):
    EN_8_2004 = 0
    SNI_1726_2019 = 1