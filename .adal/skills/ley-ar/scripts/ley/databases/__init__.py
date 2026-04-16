from . import csjn, juba, juscaba, saij

DATABASES = {
    "saij": saij.search,
    "juba": juba.search,
    "csjn": csjn.search,
    "juscaba": juscaba.search,
}
