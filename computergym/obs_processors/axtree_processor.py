from browsergym.utils.obs import flatten_axtree_to_str


def axtree_processor(axtree_object, extra_properties):
    return flatten_axtree_to_str(
        axtree_object, extra_properties=extra_properties, with_visible=True
    )
