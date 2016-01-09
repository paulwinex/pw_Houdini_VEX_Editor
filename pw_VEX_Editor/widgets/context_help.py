from vexSyntax import keywords


context_help = [
    dict(
        names =['pragma']+keywords.syntax["pragma"],
        link = 'vex/pragmas'),
    dict(
        names =keywords.syntax["directive"]+keywords.syntax["ifdirective"],
        link = 'vex/vcc#idp1562256416'),
    dict(
        names=['struct'],
        link='vex/lang#structs'
    ),
    dict(
        names=keywords.syntax['types'][:15],
        link='vex/lang#idm2135997536'
    ),
    dict(
        names=['light', 'material'],
        link='vex/lang#mantratypes'
    ),
    dict(
        names=keywords.syntax['types'][18:],
        link='vex/contexts/'
    ),
    dict(
        names=keywords.syntax['keywords'][:10],
        link='vex/statement'
    ),





]