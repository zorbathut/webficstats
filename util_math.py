
def remap(astart, aend, bstart, bend, v):
    return bstart + (v - astart) * (bend - bstart) / (aend - astart)
