
from disk import *

import svgwrite

def render():
    data = db()

    sortedstories = sorted((v for (k, v) in data.items()), key = lambda story: story.words_total())
    longestlength = sortedstories[-1].words_total() * 1.03  # little extra just so the graph isn't ending at the exact box edge

    width = 800
    columnheight = 10
    columnborder = 3

    textwidth = 150
    imageborder = 20

    ul = (-(textwidth + imageborder), -imageborder)
    br = (width + imageborder, columnheight * len(sortedstories) + imageborder)
    size = (br[0] - ul[0], br[1] - ul[1])

    dwg = svgwrite.Drawing(filename='quantity.svg', debug=True)

    gradient = dwg.linearGradient((0, 0), (1, 0))
    gradient.add_stop_color(0, 'black', opacity=0.3)
    gradient.add_stop_color(1, 'black', opacity=0)
    dwg.defs.add(gradient)


    dwg.viewbox(
        minx = ul[0],
        miny = ul[1],
        width = size[0],
        height = size[1])
    dwg.add(dwg.rect(ul, size, fill='ghostwhite'))
    dwg.add(dwg.polyline([(0, 0), (0, columnheight * len(sortedstories)), (width, columnheight * len(sortedstories))], fill = 'none', stroke = 'black'))
    for idx, story in enumerate(sortedstories):
        start = (0, idx * columnheight + columnborder)
        size = (story.words_total() / longestlength * width, columnheight - columnborder * 2)
        dwg.add(dwg.rect(start, size))
        if not story.finished:
            dwg.add(dwg.rect((start[0] + size[0], start[1] + 1), (20, size[1] - 2), fill = gradient.get_paint_server()))
        dwg.add(dwg.text(story.name, insert = (-5, (idx + 0.8) * columnheight), text_anchor = 'end', font_size = 10, alignment_baseline = 'middle'))
    dwg.save()
