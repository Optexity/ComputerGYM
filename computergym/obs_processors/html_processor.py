from browsergym.utils.obs import flatten_dom_to_str, prune_html


# TODO: FIX this to our own import
def html_processor(dom_object):
    return prune_html(flatten_dom_to_str(dom_object))
