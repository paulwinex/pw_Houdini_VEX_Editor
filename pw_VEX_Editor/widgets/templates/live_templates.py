
auto_templates = [
    # src, add after
    ['"', '"'],
    ["'", "'"],
    ["(", ")"],
    ["[", "]"],
    ["{", "}"],
    ]

# tab_templates = [
#     # src, add after TAB
#     ['for', 'for (int i=0; i<$cursor$; i++) {\n        \n    }'],
#     ['if', 'if ($cursor$) {\n        \n    }'],
#     ['fore', 'foreach (x; $cursor$) {\n        \n    }'],
#     ['print', 'printf("%s\\n", $cursor$);']
# ]

def get_templates():
    return [
    # src, add after TAB
    ['for', 'for (int i=0; i<$cursor$; i++) {\n        \n    }'],
    ['if', 'if ($cursor$) {\n        \n    }'],
    ['fore', 'foreach (x; $cursor$) {\n        \n    }'],
    ['print', 'printf("%s\\n", $cursor$);']
]