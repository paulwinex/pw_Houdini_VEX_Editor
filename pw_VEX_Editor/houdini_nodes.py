import hou

def get_sections_from_node( node):
    default = ['Help', 'TypePropertiesOptions', 'ExtraFileOptions',  'Tools.shelf', 'InternalFileOptions', 'Contents.gz', 'CreateScript', 'DialogScript', 'VexCode']
    res = {}
    Def = node.type().definition()
    if Def:
        sections = Def.sections()
        # res = {x:sections[x] for x in sections if not sections[x].name() in default}
        res = {}
        for x in sections:
            if not sections[x].name() in default:
                res[x] = sections[x]
        # for s in sections:
        #     if not sections[s].name() in default:
        #         res[s] = sections[s]
    return res

def get_parms_from_node(node):
    parms = []
    for p in node.parms():
        if p.parmTemplate().type() == hou.parmTemplateType.String:
            parms.append(p)
    return parms

def get_selected_node():
    sel = hou.selectedNodes()
    if not sel:
        #open select node dialog
        return
    else:
        if len(sel) > 1:
            # open choice dialog
            pass
            node = sel[0]
        else:
            node = sel[0]
    return node