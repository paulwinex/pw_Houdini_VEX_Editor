from .. widgets.vexSyntax import keywords
from PySide.QtCore import QProcess
from .. import vex_settings
import os, hou, re, json, zipfile, subprocess

# save functions in memory
global functions
functions = None
global attributes
attributes = None
global functions_help
functions_help = None


def get_functions():
    global functions
    if functions:
        return functions
    cache_file = vex_settings.get_autocomplete_cache_file()
    if os.path.exists(cache_file):
        comp = json.load(open(cache_file))
        functions = sorted(comp['functions'].keys(), key=lambda x: len(x))
        return functions
    else:
        return sorted(words['functions_all'], key=lambda x: len(x))

def get_attributes():
    global attributes
    if attributes:
        return attributes
    cache_file = vex_settings.get_autocomplete_cache_file()
    if os.path.exists(cache_file):
        comp = json.load(open(cache_file))
        attributes = comp['attributes'].keys() + attribs
        return attributes
    else:
        return attribs

def get_functions_help_window(func_name):
    global functions_help
    if not functions_help:
        cache_file = vex_settings.get_autocomplete_cache_file()
        if os.path.exists(cache_file):
            comp = json.load(open(cache_file))
            functions_help = comp['functions']
    if functions_help:
        if func_name in functions_help:
            res = r'<br>'.join([r'<u><b>%s</b></u>' % functions_help[func_name].get('hlp','')]+[ x for x in functions_help[func_name]['args']])
            # res = '\n'.join(['%s' % functions_help[func_name].get('hlp','')]+[ x for x in functions_help[func_name]['args']])
            if res:
                return res
            else:
                return func_name+'()'

def generate_completes(force=False):
    # si = subprocess.STARTUPINFO()
    # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # check parsed functions
    cache_file = vex_settings.get_autocomplete_cache_file()
    if os.path.exists(cache_file) and not force:
        return True
    # get vcc
    vcc = os.path.join(hou.getenv('HFS'), 'bin', 'vcc')
    if os.name == 'nt':
        vcc = (vcc + '.exe').replace('/','\\')
        def get_output(cmd):
            if isinstance(cmd, list):
                cmd = ' '.join(cmd)
            process = QProcess()
            process.start(cmd)
            process.waitForFinished()
            return str(process.readAll())
    else:
        def get_output(cmd):
            return subprocess.check_output(cmd)#, startupinfo=si)

    if not os.path.exists(vcc):
        return False
    # generate new
    funcs = {}
    attrs = {}
    lines =  get_output([vcc, '-X']).split('\n')
    for context in lines:
        if context:
            # print 'Context: %s' % context
            context_lines = get_output([vcc, '-X', context])
            # variables
            variables = re.search(r'Global Variables:(.*)Control Statements:', context_lines, re.DOTALL)
            if variables:
                lines = variables.group(1).strip().split('\n')
                for l in lines:
                    s = l.split()
                    if len(s)==3:
                        attrs[s[-1]] = s[-2]
            # functions
            pat = r'^\s*(\w+\[?\]?)\s(\w+)(\(.+\))'
            for l in context_lines.split('\n'):
                func = re.findall(pat, str(l))
                if func:
                    f_name = func[0][1]
                    f_args = func[0][2]
                    if f_name in funcs:
                        if not f_args in funcs[f_name].get('args', []):
                            funcs[f_name]['args'].append(f_args)
                    else:
                        funcs[f_name] = {'args':  [f_args]}
    # parse help if Houdini 15
    if hou.applicationVersion()[0] >= 15:
        funcs = parse_help(funcs)
    # save to cache
    if os.path.exists(cache_file):
        comp = json.load(open(cache_file))
    else:
        comp = {}
    comp['functions'] = funcs
    comp['attributes'] = attrs
    json.dump(comp, open(cache_file, 'w'))
    return True

def parse_help(source):
    vexzip = os.path.join(os.getenv('HFS'), 'houdini/help/vex.zip').replace('\\','/')
    if not os.path.exists(vexzip):
        return source
    try:
        zf = zipfile.ZipFile(vexzip, 'r')
    except:
        return source
    # funcs = {}
    for f in zf.namelist():
        if f.startswith('functions'):
            func = os.path.splitext(os.path.basename(f))[0]
            if not func in source: continue
            if func[0] == '_':continue
            text = zf.read(f)
            args = re.findall(r"`(\w+\s%s.*)`" % func, text)
            hlp = re.findall(r'"""(.*)"""', text, re.DOTALL)
            data = {}
            if args:
                data['args'] = [x.replace(' ,', ',') for x in args]
            if hlp:
                data['hlp'] = hlp[0].replace('\n', ' ')
            if data:
                source[func] = data
    return source


# def generate_completes_old(force=False):
#     # check parsed functions
#     cache_file = vex_settings.get_autocomplete_cache_file()
#     if os.path.exists(cache_file) and not force:
#         return True
#     # get vcc
#     vcc = os.path.join(hou.getenv('HFS'), 'bin', 'vcc').replace('/','\\')
#     if os.name == 'nt':
#         vcc = vcc + '.exe'
#     if not os.path.exists(vcc):
#         return False
#     print vcc
#     # generate new
#     funcs = {}
#     attrs = {}
#     process = QProcess()
#     process.start(' '.join([vcc, '-X']))
#     process.waitForFinished()
#     lines =  str(process.readAll()).split('\n')
#     for context in lines:
#         if context:
#             process.start(' '.join([vcc, '-X', context]))
#             process.waitForFinished()
#             context_lines =  str(process.readAll())
#             # variables
#             variables = re.search(r'Global Variables:(.*)Control Statements:', context_lines, re.DOTALL)
#             if variables:
#                 lines = variables.group(1).strip().split('\n')
#                 for l in lines:
#                     s = l.split()
#                     if len(s)==3:
#                         attrs[s[-1]] = s[-2]
#             # functions
#             pat = r'^\s*(\w+\[?\]?)\s(\w+)(\(.+\))'
#             for l in context_lines.split('\n'):
#                 func = re.findall(pat, str(l))
#                 if func:
#                     if func[0][1] in funcs:
#                         funcs[func[0][1]].append({'ret': func[0][0], 'args':func[0][2]})
#                     else:
#                         funcs[func[0][1]] = [{'ret': func[0][0], 'args':func[0][2]}]
#     # save to cache
#     if os.path.exists(cache_file):
#         comp = json.load(open(cache_file))
#     else:
#         comp = {}
#     comp['functions'] = funcs
#     comp['attributes'] = attrs
#     print comp['finctions'].keys()
#     print cache_file
#     json.dump(comp, open(cache_file, 'w'))
#     return True


##############################################################################
##########  DEFAULT LISTS ####################################################
##############################################################################

words = {
    # "functions":get_functions(),
    "functions_all": [
        "Dux",
        "Dv",
        "Dw",
        "abs",
        "accessframe",
        "acos",
        "addattrib",
        "addattribute",
        "adddetailattrib",
        "addgroup",
        "addpoint",
        "addpointattrib",
        "addprim",
        "addprimattrib",
        "addvariablename",
        "addvertex",
        "addvertexattrib",
        "agentaddclip",
        "agentclipcatalog",
        "agentcliplength",
        "agentclipnames",
        "agentclipsamplelocal",
        "agentclipsampleworld",
        "agentcliptimes",
        "agentclipweights",
        "agentcollisionlayer",
        "agentcurrentlayer",
        "agentlayerbindings",
        "agentlayers",
        "agentlayershapes",
        "agentlocaltransform",
        "agentlocaltransforms",
        "agentrigchildren",
        "agentrigfind",
        "agentrigparent",
        "agenttransformcount",
        "agenttransformnames",
        "agenttransformtolocal",
        "agenttransformtoworld",
        "agentworldtransform",
        "agentworldtransforms",
        "albedo",
        "alphaname",
        "ambient",
        "anoise",
        "append",
        "area",
        "argsort",
        "array",
        "arraylength",
        "ashikhmin",
        "asin",
        "assert_enabled",
        "assign",
        "atan",
        "atan2",
        "atof",
        "atoi",
        "atten",
        "attribsize",
        "attribtype",
        "attribtypeinfo",
        "avg",
        "binput",
        "blackbody",
        "blinn",
        "blinnBRDF",
        "bouncelabel",
        "bouncemask",
        "bumpmap",
        "bumpmapA",
        "bumpmapB",
        "bumpmapG",
        "bumpmapL",
        "bumpmapR",
        "bumpname",
        "cbrt",
        "ceil",
        "ch",
        "ch3",
        "ch4",
        "chend",
        "chendf",
        "chendt",
        "chf",
        "chi",
        "chinput",
        "chname",
        "chnumchan",
        "chp",
        "chr",
        "chramp",
        "chrate",
        "chs",
        "chsraw",
        "chstart",
        "chstartf",
        "chstartt",
        "chv",
        "cinput",
        "ckspline",
        "clamp",
        "clip",
        "colormap",
        "colorname",
        "computenormal",
        "concat",
        "cone",
        "cos",
        "cosh",
        "cracktransform",
        "cross",
        "cspline",
        "ctransform",
        "curlnoise",
        "curlnoise2d",
        "curlxnoise",
        "curlxnoise2d",
        "cvex_bsdf",
        "degrees",
        "depthmap",
        "depthname",
        "detail",
        "detailattrib",
        "detailattribsize",
        "detailattribtype",
        "detailattribtypeinfo",
        "detailintrinsic",
        "determinant",
        "diffuse",
        "diffuseBRDF",
        "dihedral",
        "dimport",
        "distance",
        "distance2",
        "dot",
        "dsmpixel",
        "eigenvalues",
        "emission_bsdf",
        "endswith",
        "environment",
        "erf",
        "erf_inv",
        "erfc",
        "eulertoquaternion",
        "eval_bsdf",
        "exp",
        "expand_udim",
        "expandpointgroup",
        "expandprimgroup",
        "fastshadow",
        "filamentsample",
        "file_eof",
        "file_flush",
        "file_open",
        "file_read",
        "file_readline",
        "file_readlines",
        "file_seek",
        "file_size",
        "file_stat",
        "file_tell",
        "file_write",
        "file_writeline",
        "file_writelines",
        "filtershadow",
        "filterstep",
        "find",
        "findattribval",
        "findattribvalcount",
        "finput",
        "fit",
        "fit01",
        "fit10",
        "fit11",
        "floor",
        "flownoise",
        "flowpnoise",
        "foreach",
        "forpoints",
        "frac",
        "fresnel",
        "fromNDC",
        "frontface",
        "gather",
        "geoself",
        "getattribute",
        "getbbox",
        "getblurP",
        "getbounces",
        "getbounds",
        "getcomp",
        "getcomponents",
        "getfogname",
        "getglobalraylevel",
        "getlight",
        "getlightid",
        "getlightname",
        "getlights",
        "getlightscope",
        "getmaterial",
        "getobjectname",
        "getphotonlight",
        "getpointbbox",
        "getprimid",
        "getptextureid",
        "getraylevel",
        "getrayweight",
        "getscope",
        "getspace",
        "gradient",
        "gradient3d",
        "hair",
        "hasdetailattrib",
        "haslight",
        "hasplane",
        "haspointattrib",
        "hasprimattrib",
        "hasvertexattrib",
        "hedge_dstpoint",
        "hedge_dstvertex",
        "hedge_equivcount",
        "hedge_isequiv",
        "hedge_isprimary",
        "hedge_isvalid",
        "hedge_next",
        "hedge_nextequiv",
        "hedge_postdstpoint",
        "hedge_postdstvertex",
        "hedge_presrcpoint",
        "hedge_presrcvertex",
        "hedge_prev",
        "hedge_prim",
        "hedge_primary",
        "hedge_srcpoint",
        "hedge_srcvertex",
        "henyeygreenstein",
        "hscript_noise",
        "hscript_rand",
        "hscript_snoise",
        "hscript_sturb",
        "hscript_turb",
        "hsvtorgb",
        "iaspect",
        "ichname",
        "ident",
        "iend",
        "iendtime",
        "ihasplane",
        "illuminance",
        "import",
        "importance_light",
        "ingroup",
        "inpointgroup",
        "inprimgroup",
        "insert",
        "instance",
        "integrate3d",
        "integrate3dClip",
        "interpolate",
        "intersect",
        "intersect3d",
        "intersect_all",
        "intersect_lights",
        "inumplanes",
        "invert",
        "iplaneindex",
        "iplanename",
        "iplanesize",
        "irate",
        "irradiance",
        "isalpha",
        "isbound",
        "isconnected",
        "isdigit",
        "isfinite",
        "isfogray",
        "isframes",
        "isnan",
        "isotropic",
        "israytracing",
        "issamples",
        "isseconds",
        "isshadowray",
        "istart",
        "istarttime",
        "istracing",
        "isuvrendering",
        "isvalidindex",
        "isvarying",
        "itoa",
        "ixres",
        "iyres",
        "join",
        "kspline",
        "len",
        "length",
        "length2",
        "lerp",
        "lightid",
        "limit_sample_space",
        "limport",
        "lkspline",
        "log",
        "log10",
        "lookat",
        "lspline",
        "lstrip",
        "luminance",
        "lumname",
        "makebasis",
        "maketransform",
        "maskname",
        "match",
        "matchvex_blinn",
        "matchvex_specular",
        "mattrib",
        "max",
        "mdensity",
        "metaimport",
        "metamarch",
        "metanext",
        "metastart",
        "metaweight",
        "min",
        "minpos",
        "mspace",
        "nbouncetypes",
        "nearpoint",
        "nearpoints",
        "neighbour",
        "neighbourcount",
        "neighbours",
        "newgroup",
        "newsampler",
        "nextsample",
        "ninput",
        "noise",
        "noised",
        "normal_bsdf",
        "normalize",
        "normalname",
        "npoints",
        "npointsgroup",
        "nprimitives",
        "nprimitivesgroup",
        "nrandom",
        "ntransform",
        "nuniqueval",
        "occlusion",
        "onoise",
        "opend",
        "opstart",
        "optransform",
        "ord",
        "osd_facecount",
        "osd_firstpatch",
        "osd_limitsurface",
        "osd_limitsurfacevertex",
        "osd_patchcount",
        "osd_patches",
        "outerproduct",
        "ow_nspace",
        "ow_space",
        "ow_vspace",
        "pack_inttosafefloat",
        "pathtrace",
        "pcclose",
        "pcconvex",
        "pcexport",
        "pcfarthest",
        "pcfilter",
        "pcfind",
        "pcfind_radius",
        "pcgenerate",
        "pcimport",
        "pcimportbyidx3",
        "pcimportbyidx4",
        "pcimportbyidxf",
        "pcimportbyidxi",
        "pcimportbyidxp",
        "pcimportbyidxs",
        "pcimportbyidxv",
        "pciterate",
        "pcnumfound",
        "pcopen",
        "pcopenlod",
        "pcsampleleaf",
        "pcsize",
        "pcunshaded",
        "pcwrite",
        "phong",
        "phongBRDF",
        "phonglobe",
        "photonmap",
        "planeindex",
        "planename",
        "planesize",
        "pluralize",
        "pnoise",
        "point",
        "pointattrib",
        "pointattribsize",
        "pointattribtype",
        "pointattribtypeinfo",
        "pointedge",
        "pointhedge",
        "pointhedgenext",
        "pointname",
        "pointprims",
        "pointvertex",
        "pointvertices",
        "polardecomp",
        "pop",
        "pow",
        "prim",
        "prim_attribute",
        "prim_normal",
        "primattrib",
        "primattribsize",
        "primattribtype",
        "primattribtypeinfo",
        "primhedge",
        "primintrinsic",
        "primpoint",
        "primpoints",
        "primuv",
        "primvertex",
        "primvertexcount",
        "primvertices",
        "printf",
        "print_once",
        "ptexture",
        "ptlined",
        "ptransform",
        "push",
        "qconvert",
        "qdistance",
        "qinvert",
        "qmultiply",
        "qrotate",
        "quaternion",
        "radians",
        "rand",
        "random",
        "random_fhash",
        "random_ihash",
        "random_shash",
        "random_sobol",
        "rawbumpmap",
        "rawbumpmapA",
        "rawbumpmapB",
        "rawbumpmapG",
        "rawbumpmapL",
        "rawbumpmapR",
        "rawcolormap",
        "rayhittest",
        "rayimport",
        "re_find",
        "re_findall",
        "re_match",
        "re_replace",
        "re_split",
        "reflect",
        "reflectlight",
        "refract",
        "refractlight",
        "relbbox",
        "relpointbbox",
        "removegroup",
        "removeindex",
        "removepoint",
        "removeprim",
        "removevalue",
        "renderstate",
        "reorder",
        "resize",
        "resolvemissedray",
        "reverse",
        "rgbtohsv",
        "rgbtoxyz",
        "rint",
        "rotate",
        "rotate_x_to",
        "rstrip",
        "sample_bsdf",
        "sample_cauchy",
        "sample_circle_arc",
        "sample_circle_edge_uniform",
        "sample_circle_slice",
        "sample_circle_uniform",
        "sample_direction_cone",
        "sample_direction_uniform",
        "sample_discrete",
        "sample_exponential",
        "sample_geometry",
        "sample_hemisphere",
        "sample_hypersphere_cone",
        "sample_hypersphere_uniform",
        "sample_light",
        "sample_lognormal",
        "sample_lognormal_by_median",
        "sample_normal",
        "sample_orientation_cone",
        "sample_orientation_uniform",
        "sample_photon",
        "sample_sphere_cone",
        "sample_sphere_uniform",
        "sampledisk",
        "scale",
        "select",
        "sensor_panorama_create",
        "sensor_panorama_getcolor",
        "sensor_panorama_getcone",
        "sensor_panorama_getdepth",
        "sensor_save",
        "serialize",
        "set",
        "setagentclipnames",
        "setagentcliptimes",
        "setagentclipweights",
        "setagentcollisionlayer",
        "setagentcurrentlayer",
        "setagentlocaltransform",
        "setagentlocaltransforms",
        "setagentworldtransform",
        "setagentworldtransforms",
        "setattrib",
        "setattribtypeinfo",
        "setcomp",
        "setcurrentlight",
        "setdetailattrib",
        "setpointattrib",
        "setpointgroup",
        "setprimattrib",
        "setprimgroup",
        "setprimintrinsic",
        "setprimvertex",
        "setvertexattrib",
        "shadow",
        "shadow_light",
        "shadowmap",
        "shimport",
        "shl",
        "shr",
        "shrz",
        "sign",
        "simport",
        "sin",
        "sinh",
        "sleep",
        "slerp",
        "slice",
        "smooth",
        "snoise",
        "solvecubic",
        "solvepoly",
        "solvequadratic",
        "sort",
        "specular",
        "specularBRDF",
        "spline",
        "split",
        "sprintf",
        "sqrt",
        "startswith",
        "storelightexport",
        "strip",
        "strlen",
        "switch",
        "swizzle",
        "tan",
        "tanh",
        "tet_adjacent",
        "tet_faceindex",
        "teximport",
        "texprintf",
        "texture",
        "texture3d",
        "texture3dBox",
        "titlecase",
        "toNDC",
        "tolower",
        "toupper",
        "trace",
        "translate",
        "translucent",
        "transpose",
        "trunc",
        "tw_nspace",
        "tw_space",
        "tw_vspace",
        "uniqueval",
        "unpack_intfromsafefloat",
        "unserialize",
        "upush",
        "variadicarguments",
        "variance",
        "velocityname",
        "vertex",
        "vertexattrib",
        "vertexattribsize",
        "vertexattribtype",
        "vertexattribtypeinfo",
        "vertexhedge",
        "vertexindex",
        "vertexnext",
        "vertexpoint",
        "vertexprev",
        "vertexprim",
        "vertexprimindex",
        "vnoise",
        "volume",
        "volumegradient",
        "volumeindex",
        "volumeindexorigin",
        "volumeindextopos",
        "volumeindexv",
        "volumepostoindex",
        "volumeres",
        "volumesample",
        "volumesamplev",
        "vtransform",
        "wireblinn",
        "wirediffuse",
        "wnoise",
        "wo_nspace",
        "wo_space",
        "wo_vspace",
        "writepixel",
        "wt_nspace",
        "wt_space",
        "wt_vspace",
        "xnoise",
        "xnoised",
        "xyzdist",
        "xyztorgb",
      ],
    "keywords":keywords.syntax['keywords']+keywords.syntax['directive'],
    "types":keywords.syntax['types'],
    "variables":[
        "__vex",
        "__vex_major",
        "__vex_minor",
        "__vex_build",
        "__vex_patch",
        "__LINE__",
        "__FILE__",
        "__DATE__",
        "__TIME__",
        "__nondiffuse",
        "__nonspecular",
        "__contrib_names",
        "__contrib_amounts",
        "__nofog",
        "__illuminateangle",
    ],

}

context_complete = {
    '#pragma\s+':[
            "bindhandle",
            "bindhandlereserved",
            "bindselector",
            "bindselectorreserved",
            "callback",
            "disablewhen",
            "hidewhen",
            "export",
            "group",
            "info",
            "help",
            "hint",
            "inputlabel",
            "label",
            "name",
            "opicon",
            "opmininputs",
            "opmaxinputs",
            "opname",
            "oplabel",
            "opscript",
            "parmhelp",
            "parmtag",
            "ramp_flt",
            "ramp_rgb",
            "ramp",
            "range",
            "rendermask",
            "optable",
            "rename",
    ],
    "#if\s+!?":[
            "defined",
            "environment",
            "access",
            "strcmp",
            ],
    "#elif\s+!?":[
            "defined",
            "environment",
            "access",
            "strcmp",
            ],
}

attribs = [
        #SOP
        'Cd',
        'Time',
        'accel',
        'life',
        'P',
        'Pw',
        'id',
        'v',
        'ptnum',
        'primnum',
        'pstate',
        'Npt',
        'age',
        'TimeInc',
        'N',
        'Frame',
        'density',
        # SHOP
        'dPdz',
        'P',
        'Ng',
        'L',
        'dPds',
        'Pz',
        'I',
        'Of',
        'Eye',
        'dPdt',
        'Cf',
        'F',
        't',
        'N',
        'Cl',
        's',
        'Af',
        'Lz',
        # COP
        'IX',
        'PXSC',
        'PS',
        'AS',
        'EF',
        'SF',
        'H',
        'Cb',
        'FR',
        'C4',
        'G',
        'V',
        'I',
        'NP',
        'A',
        'F',
        'PNAME',
        'X',
        'Cr',
        'S',
        'TIME',
        'R',
        'YRES',
        'IY',
        'XRES',
        'AI',
        'Cg',
        'B',
        'AR',
        'PL',
        'Y',
        'NI',
        'TINC',
        # CHOP
        'SR',
        'NC',
        'I',
        'C',
        'L',
        'V',
        'E',
        # MISC
        'OpInput1',
        'OpInput2',
        'OpInput3',
        'OpInput4'

]
variables = [
    # Playbar variables
    'FPS',
    'FSTART',
    'FEND',
    'F',
    'FF',
    'NFRAMES',
    'RFSTART',
    'RFEND',
    'T',
    'TLENGTH',
    'TSTART',
    'TEND',
    # Global Variables
    # 'ACTIVETAKE',
    'E',
    # 'HFS',
    # 'HH',
    # 'HIP',
    # 'HIPFILE',
    # 'HIPNAME',
    # 'HOME',
    # 'JOB',
    'PI',
    # 'WEDGE',
    # # Channel Variables
    # 'OS',
    # 'CH',
    # 'IV',
    # 'OV',
    # 'IM',
    # 'OM',
    # 'IA',
    # 'OA',
    # 'LT',
    # 'IT',
    # 'OT',
    # 'LIT',
    # 'LOT',
    # 'PREV_IT',
    # 'NEXT_OT',
    # # COP-specific variables
    # 'CSTART',
    # 'CEND',
    # 'CFRAMES',
    # 'CFRAMES_IN',
    # 'CINC',
    # 'W',
    # 'H',
    # Output Driver Specific Variables
    # 'N',
    # 'NRENDER',
    # SOP Context
    # 'AGE',
    # 'BBX',
    # 'BBY',
    # 'BBZ',
    # 'CA',
    # 'CEX',
    # 'CEY',
    # 'CEZ',
    # 'COMX',
    # 'COMY',
    # 'COMZ',
    # 'CR',
    # 'CG',
    # 'CB',
    # 'CREASE',
    # 'DIST',
    # 'DRAG',
    # 'ID',
    # 'LIFE',
    # 'MAPU',
    # 'MAPV',
    # 'MAPW',
    # 'MASS',
    # 'MAT',
    # 'NPT',
    # 'NX',
    # 'NY',
    # 'NZ',
    # 'PR',
    # 'NPR',
    # 'PSCALE',
    # 'PT',
    # 'RESTX',
    # 'RESTY',
    # 'RESTZ',
    # 'SIZEX',
    # 'SIZEY',
    # 'SIZEZ',
    # 'TX',
    # 'TY',
    # 'TZ',
    # 'VTX',
    # 'NVTX',
    # 'XMIN',
    # 'XMAX',
    # 'YMIN',
    # 'YMAX',
    # 'ZMIN',
    # 'ZMAX',
]