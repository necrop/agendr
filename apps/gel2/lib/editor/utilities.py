import re
from ...models import FreqTable

core_fields = {
    "entry": ("label", "soundfile_uk", "soundfile_us"),
    "wordclass": ("penn", "definition",),
    "type": ("form", "penn", "variant",),}

freqtable_fields = [f.name for f in FreqTable._meta.fields
                    if re.search(r"^f[0-9]{4}$", f.name)]

variant_opts = (("s", "standard spelling"), ("u", "US spelling"),
                ("v", "variant spelling"),)
